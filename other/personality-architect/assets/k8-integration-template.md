# K8 Integration Template

This is the blueprint for shipping a personality-architect-designed test into the K8 codebase (`/Users/clay/Donjon Repos/im-k8`). K8 is Vite + React + TS + Tailwind + shadcn-ui + Supabase.

## Architecture overview

```
React form (src/components/assessment/)
  ↓ submits responses
Supabase Edge Function (supabase/functions/score-personality/)
  ↓ scores using question_bank.json + scoring.json
PostgreSQL (assessment_results table, JSONB result column)
  ↓ exposed via React Query hooks (src/hooks/useAssessments.ts)
Agent Builder (consumes trait_vector to seed agent persona)
```

## 1. Database schema

Add to `supabase/migrations/<timestamp>_personality_assessment.sql`:

```sql
-- Question bank (one row per item, sourced from question_bank.json)
create table if not exists assessment_questions (
  id text primary key,                       -- matches Q-CON-01 format
  text text not null,
  primary_trait text not null,
  secondary_trait text,
  polarity smallint not null check (polarity in (-1, 1)),
  scale text not null default 'likert_7',
  status text not null default 'draft' check (status in ('draft', 'pilot', 'production')),
  display_order int,
  created_at timestamptz not null default now()
);

-- One response per (user, question) per assessment session
create table if not exists assessment_responses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid not null,
  question_id text not null references assessment_questions(id),
  response smallint not null,                -- 1-7
  responded_at timestamptz not null default now(),
  unique (session_id, question_id)
);

-- One result row per completed session
create table if not exists assessment_results (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid not null unique,
  trait_vector jsonb not null,               -- {conscientiousness: 0.5, ...}
  trait_uncertainty jsonb,                   -- Tier 2+ only
  ers_estimate numeric,
  archetype_distribution jsonb not null,
  primary_archetype text not null,
  secondary_archetype text,
  scoring_version text not null,             -- so old results stay traceable
  completed_at timestamptz not null default now()
);

-- RLS: users can only see their own data
alter table assessment_responses enable row level security;
alter table assessment_results enable row level security;

create policy "users read own responses" on assessment_responses
  for select using (auth.uid() = user_id);
create policy "users insert own responses" on assessment_responses
  for insert with check (auth.uid() = user_id);

create policy "users read own results" on assessment_results
  for select using (auth.uid() = user_id);
-- results inserted only via edge function (service role); no user-side insert policy
```

## 2. Edge function — scoring

`supabase/functions/score-personality/index.ts` — scores responses server-side so weights stay private. Port `scripts/score_test.py` to Deno-flavored TS:

```typescript
import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import scoringConfig from "./scoring.json" with { type: "json" };
import questionBank from "./question_bank.json" with { type: "json" };

interface Response { question_id: string; response: number }

function scoreTier1(responses: Response[]) {
  // 1. Build user-level z-score (poor-person ERS correction)
  const raw = responses.map(r => r.response);
  const mean = raw.reduce((a, b) => a + b, 0) / raw.length;
  const sd = Math.sqrt(raw.reduce((a, b) => a + (b - mean) ** 2, 0) / raw.length) || 1;

  // 2. Sum weighted contributions per trait
  const traits: Record<string, number[]> = {};
  for (const t of scoringConfig.traits) traits[t] = [];

  for (const r of responses) {
    const item = questionBank.items.find(i => i.id === r.question_id);
    if (!item) continue;
    const z = (r.response - mean) / sd;
    const adjusted = item.polarity * z;
    traits[item.primary_trait].push(adjusted);
    if (item.secondary_trait) {
      traits[item.secondary_trait].push(adjusted * scoringConfig.cross_loading_secondary_weight);
    }
  }

  const trait_vector: Record<string, number> = {};
  for (const [t, vals] of Object.entries(traits)) {
    trait_vector[t] = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  }

  // 3. Map to archetypes via cosine similarity (direction-only, magnitude-invariant)
  // This is what makes calibration work — distance-based scoring biases toward
  // whichever archetype is closest to origin under random input.
  const traits = scoringConfig.traits;
  const tMag = Math.sqrt(traits.reduce((a, t) => a + trait_vector[t] ** 2, 0)) || 1e-9;
  const archetype_logits: Record<string, number> = {};
  for (const [name, arch] of Object.entries(scoringConfig.archetypes)) {
    const sig = (arch as any).trait_signature;
    const sMag = Math.sqrt(traits.reduce((a, t) => a + sig[t] ** 2, 0)) || 1e-9;
    const dot = traits.reduce((a, t) => a + trait_vector[t] * sig[t], 0);
    archetype_logits[name] = dot / (tMag * sMag);  // cosine similarity
  }

  // 4. Softmax
  const max = Math.max(...Object.values(archetype_logits));
  const exps = Object.fromEntries(
    Object.entries(archetype_logits).map(([k, v]) => [k, Math.exp(v - max)])
  );
  const sumExp = Object.values(exps).reduce((a, b) => a + b, 0);
  const archetype_distribution = Object.fromEntries(
    Object.entries(exps).map(([k, v]) => [k, v / sumExp])
  );

  // 5. Top two
  const sorted = Object.entries(archetype_distribution).sort(([, a], [, b]) => b - a);
  return {
    trait_vector,
    ers_estimate: 0,  // user-z-score doesn't produce a separate ERS scalar; placeholder
    archetype_distribution,
    primary_archetype: sorted[0][0],
    secondary_archetype: sorted[1][0],
  };
}

serve(async (req) => {
  const { session_id } = await req.json();

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const { data: responses } = await supabase
    .from("assessment_responses")
    .select("question_id, response, user_id")
    .eq("session_id", session_id);

  if (!responses || responses.length === 0) {
    return new Response(JSON.stringify({ error: "no responses" }), { status: 400 });
  }

  const result = scoreTier1(responses);
  const { error } = await supabase.from("assessment_results").insert({
    user_id: responses[0].user_id,
    session_id,
    ...result,
    scoring_version: "personality-architect-v0.1.0-tier1",
  });

  if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  return new Response(JSON.stringify(result), { headers: { "Content-Type": "application/json" } });
});
```

Set `verify_jwt = true` in `supabase/config.toml` for this function — only authenticated users score themselves.

## 3. React Query hook

`src/hooks/useAssessment.ts`:

```typescript
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export function useAssessmentQuestions() {
  return useQuery({
    queryKey: ["assessment_questions"],
    queryFn: async () => {
      const { data } = await supabase
        .from("assessment_questions")
        .select("*")
        .eq("status", "production")
        .order("display_order");
      return data ?? [];
    },
  });
}

export function useSubmitResponse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { session_id: string; question_id: string; response: number }) => {
      const { error } = await supabase.from("assessment_responses").upsert(input);
      if (error) throw error;
    },
  });
}

export function useFinalizeAssessment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (session_id: string) => {
      const { data, error } = await supabase.functions.invoke("score-personality", {
        body: { session_id },
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assessment_result"] }),
  });
}

export function useAssessmentResult(session_id?: string) {
  return useQuery({
    queryKey: ["assessment_result", session_id],
    enabled: !!session_id,
    queryFn: async () => {
      const { data } = await supabase
        .from("assessment_results")
        .select("*")
        .eq("session_id", session_id!)
        .single();
      return data;
    },
  });
}
```

## 4. UI component shape

Use existing shadcn-ui primitives (`Slider`, `Button`, `Progress` from `src/components/ui/`). Suggested layout:

```
src/components/assessment/
├── AssessmentFlow.tsx      // session-level container; manages session_id, current item index
├── ItemCard.tsx            // renders one Likert question + slider
├── ProgressHeader.tsx      // shows N of M, with progress bar
└── ResultView.tsx          // archetype + trait radar (use Recharts)
```

Don't auto-advance the user when they pick a value — give an explicit Next button. Auto-advance feels rushed and amplifies ERS noise.

## 5. Voice intake (K8's `analyze-voice-transcript` modality)

For voice-based assessment, treat the trait model the same; just change the rendering layer:

- Voice prompts are scenarios ("Tell me about a time you had to make a hard call.")
- Transcript goes to the existing `analyze-voice-transcript` edge function
- That function already calls an LLM to extract structured data — extend its output schema to include trait scores per the same trait model
- Merge voice-derived trait scores with Likert-derived trait scores using a weighted mean (Likert at 0.7, voice at 0.3 by default; tune from validation data)

Voice intake is not a replacement for Likert — it's a complement. It catches things Likert misses (linguistic style, hesitation, narrative structure) that the agent will need to mimic the user well.

## 6. Linking trait_vector to the agent

The whole point. When K8 builds an agent persona for a user, it should:

1. Pull the user's `trait_vector` from `assessment_results`
2. Inject it into the agent's system prompt with archetype guidance from `archetypes.md`
3. Use the agent-behavior notes for each archetype to bias the agent's defaults under uncertainty

Pseudocode for the agent system prompt scaffold:

```typescript
const agentSystemPrompt = `
You are an AI agent representing ${userName}.

Their trait profile (signed z-scores, 0 = population average):
- Conscientiousness: ${tv.conscientiousness.toFixed(2)}
- Need for Cognition: ${tv.need_for_cognition.toFixed(2)}
- Analytical Thinking: ${tv.analytical_thinking.toFixed(2)}
- Agency Motivation: ${tv.agency_motivation.toFixed(2)}
- Promotion Focus: ${tv.promotion_focus.toFixed(2)}
- Sensation Seeking: ${tv.sensation_seeking.toFixed(2)}
- Emotional Expressivity: ${tv.emotional_expressivity.toFixed(2)}
- Communion Motivation: ${tv.communion_motivation.toFixed(2)}

Primary archetype: ${primaryArchetype} — ${archetypeNarratives[primaryArchetype].oneLineFromArchetype}

Behavioral defaults you should adopt:
${archetypeNarratives[primaryArchetype].agentBehaviorNotes.map(n => `- ${n}`).join('\n')}

When the user is in a situation that triggers their secondary archetype (${secondaryArchetype}), bias toward those behaviors instead.
`;
```

This is the contract between the assessment and the agent. Keep it simple at first; make it richer as you collect data on which patterns produce recognizable agents.
