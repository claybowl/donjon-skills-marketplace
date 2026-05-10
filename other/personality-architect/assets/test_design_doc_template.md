# [Test Name] — Design Spec

**Owner:** [name] · **Status:** [draft / pilot / production] · **Last updated:** [date]

## 1. Mission

> One sentence: what decision does this test feed?

Example: *"This test produces a personality profile that the K8 user's AI agent uses to mimic the user in lounge conversations."*

## 2. Target user & context

- **Who takes it:** [audience]
- **When:** [onboarding / settings / scheduled retest]
- **Modality:** [Likert web form / voice intake / hybrid]
- **Length budget:** [target N questions; max time]
- **Privacy posture:** [what is stored, who can see it, how it flows to downstream agents]

## 3. Trait model

| Trait | Operational Definition | Source / Citation | Items |
|---|---|---|---|
| | | | |

Rationale for trait selection: [1–2 paragraphs]

## 4. Question bank

- Total items: [N]
- Items per trait: [target]
- Polarity mix: [direct vs. reverse percentages]
- Scale: [Likert 7 / 5 / forced-choice / mixed]

Full bank lives in `question_bank.json`. Stages: draft → pilot → production.

## 5. Scoring approach

**Tier:** [1 / 2 / 3]

**Why this tier:** [1 paragraph defending the choice]

**Tier 1 (weighted sum) details:**
- Reverse-scored items handled via [subtraction from scale-max-plus-1 / multiply by −1]
- Cross-loading items: secondary trait gets [50%] weight
- ERS correction: [poor-person z-score / none]

**Tier 2 (Bayesian) details:**
- Prior: [Normal(0,1) per trait + Normal(0,1) ERS]
- Discrimination per item: [hand-set 1.0 / learned from pilot data]
- Inference: [closed-form Kalman / MCMC / variational]

**Tier 3 (adaptive) details:**
- IG computation: [Monte Carlo / lookup table]
- Coverage bonus λ: [value]
- Stopping rule: [entropy threshold / fixed cap]

## 6. Result schema

```json
{
  "trait_vector": {
    "conscientiousness": 0.0,
    "need_for_cognition": 0.0,
    ...
  },
  "trait_uncertainty": {
    "conscientiousness": 0.0,
    ...
  },
  "ers_estimate": 0.0,
  "archetype_distribution": {
    "blue": 0.0,
    "green": 0.0,
    ...
  },
  "primary_archetype": "blue",
  "secondary_archetype": "black",
  "completed_at": "ISO8601",
  "n_items_answered": 0
}
```

The **trait_vector** is what AI agents consume. The **archetype** is what users see.

## 7. Archetypes (if applicable)

Full descriptions in `archetypes.md`. Grid structure: [5×5 / 4×4 / 3×3 / N/A]

Each archetype includes:
- Name and shorthand
- Trait signature
- Strengths (what this pattern enables)
- Shadow side (what this pattern makes hard)
- 2nd-person, present-tense narrative copy
- Recommended agent behaviors (for K8: how should the agent representing this archetype act?)

## 8. Validation plan

(Copy from `references/validation.md` validation plan template, fill in actuals.)

## 9. Open questions

- [ ] [Anything you flagged for follow-up]

## 10. Next steps

- **Owner:** [name]
- **Action:** [single, crisp action]
- **When:** [ETA]
- **Success:** [observable criteria]
