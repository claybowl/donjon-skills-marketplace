# Scene Patterns

Ready-to-paste JSX templates for every standard scene in an agent workflow
video. Each one assumes the imports already in `ProjectVideo.tsx`:

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AgentBadge } from "./components/AgentBadge";
import { TerminalLine } from "./components/TerminalLine";
import { ActLabel } from "./components/ActLabel";
import { COLORS, FONT_MONO } from "./theme";
```

And a `<SceneFrame>` wrapper that pads + centers content. The starter
`ProjectVideo.tsx` defines this — reuse it.

## The narrative arc

Every cut follows the same shape. Don't reinvent — adapt the content,
keep the order:

```
Intro          → "what is this"
Mission        → "what's the user asking for"
Receive        → "top-level agent picks up the work"
Plan           → "tasks get created"
Dispatch       → "tasks get routed"
Execute (×N)   → "each specialized agent does its thing"
Results        → "what came out the other end"
Council        → "meta reflection" (optional)
Stats          → "by the numbers"
Outro          → "tagline + brand mark"
```

Why this order works: it matches how viewers process narrative — context
first, then conflict (the work), then resolution. Skipping Mission or
Results is the most common mistake; it leaves viewers asking "what
happened?"

---

## Intro

The first 1.5 seconds. Blur-reveal a title. Don't add an agent badge yet
— let the viewer read first.

```tsx
const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const blur = interpolate(frame, [0, 40], [20, 0], { extrapolateRight: "clamp" });
  const opacity = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: "clamp" });

  return (
    <SceneFrame>
      <div style={{ opacity, filter: `blur(${blur}px)` }}>
        <ActLabel text="A Day in the Donjon" delay={0} />
        <div
          style={{
            fontSize: 96,
            fontWeight: 800,
            background: `linear-gradient(135deg, ${COLORS.purple}, ${COLORS.pink}, ${COLORS.warn})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          {/* Hook — 2-4 words */}
          Agents at work.
        </div>
      </div>
    </SceneFrame>
  );
};
```

## Mission

The user's ask, in plain text. Quote-attribution feel. Keep it under 12
words — viewers read it once.

```tsx
const Mission: React.FC = () => (
  <SceneFrame>
    <ActLabel text="The Mission" delay={0} />
    <TerminalLine delay={10} type="highlight" fontSize={44}>
      Build a competitive analysis landing page for X.
    </TerminalLine>
    <TerminalLine delay={40} type="default" fontSize={24}>
      — the user
    </TerminalLine>
  </SceneFrame>
);
```

## Receive

Top-level agent loads memory / context. This sells the "intelligent" feel
— viewers see a system that *remembers* before it acts.

```tsx
const Receive: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Act I — Receive" delay={0} />
    <AgentBadge agent="orchestrator" label="ORCHESTRATOR" size="lg" glow delay={10} />
    <TerminalLine delay={30} type="tool">read_block("agent_manifest")</TerminalLine>
    <TerminalLine delay={55} type="result">loaded 12 memory blocks</TerminalLine>
    <TerminalLine delay={80} type="highlight">Mission understood.</TerminalLine>
  </SceneFrame>
);
```

## Plan

Top-level agent decomposes the mission into tasks. Use `type="tool"` for
each `create_task` call.

```tsx
const Plan: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Act II — Plan" delay={0} />
    <AgentBadge agent="planner" label="PLANNER" size="lg" glow delay={10} />
    <TerminalLine delay={30} type="tool">create_task(T1: "research")</TerminalLine>
    <TerminalLine delay={50} type="tool">create_task(T2: "draft")</TerminalLine>
    <TerminalLine delay={70} type="tool">create_task(T3: "build")</TerminalLine>
    <TerminalLine delay={90} type="tool">create_task(T4: "deploy")</TerminalLine>
    <TerminalLine delay={110} type="result">4 tasks created</TerminalLine>
  </SceneFrame>
);
```

## Dispatch

Tasks get routed to specialized agents. Use `type="dispatch"` (amber arrow
prefix). This scene is fast — no badges, just routing lines.

```tsx
const Dispatch: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Dispatch" delay={0} />
    <TerminalLine delay={10} type="dispatch">T1 → RETRIEVER</TerminalLine>
    <TerminalLine delay={30} type="dispatch">T2 → WRITER</TerminalLine>
    <TerminalLine delay={50} type="dispatch">T3 → WORKER</TerminalLine>
    <TerminalLine delay={70} type="dispatch">T4 → DEPLOYER</TerminalLine>
  </SceneFrame>
);
```

## Gremlin (reusable execution scene)

One scene per specialized agent. Use the reusable `Gremlin` component —
do *not* copy-paste this 4× per project.

```tsx
const Gremlin: React.FC<{
  agent: AgentKey;
  agentLabel: string;
  taskId: string;
  taskName: string;
  tools: string[];
  result: string;
}> = ({ agent, agentLabel, taskId, taskName, tools, result }) => (
  <SceneFrame>
    <ActLabel text={`Act III — ${agentLabel} Executes`} delay={0} />
    <div style={{ marginBottom: 20, display: "flex", gap: 12, alignItems: "center" }}>
      <AgentBadge agent={agent} label={agentLabel} size="md" glow delay={10} />
      <span style={{ color: COLORS.muted, fontSize: 20 }}>
        {taskId} · {taskName}
      </span>
    </div>
    {tools.map((t, i) => (
      <TerminalLine key={i} delay={25 + i * 18} type="tool">{t}</TerminalLine>
    ))}
    <TerminalLine delay={25 + tools.length * 18 + 15} type="result">
      {result}
    </TerminalLine>
  </SceneFrame>
);

// Then in the composition:
<Sequence from={540} durationInFrames={90}>
  <Gremlin
    agent="retriever"
    agentLabel="RETRIEVER"
    taskId="T1"
    taskName="research competitors"
    tools={["web_search('competitive analysis')", "http_get('g2.com/...')"]}
    result="12 sources indexed"
  />
</Sequence>
```

Tip: cap each gremlin at 3-4 tool calls. More than that and the scene
feels cluttered at 1080×1920.

## Results

Aggregated artifacts. Lean on `type="result"` (green ✓ prefix). Three
lines max.

```tsx
const Results: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Results" delay={0} />
    <TerminalLine delay={10} type="result" fontSize={30}>4 tasks complete</TerminalLine>
    <TerminalLine delay={35} type="result" fontSize={30}>Page live: domain.com/path</TerminalLine>
    <TerminalLine delay={60} type="result" fontSize={30}>All checks green</TerminalLine>
  </SceneFrame>
);
```

## Council (optional)

Meta-reflection beat. Show all agents together as small badges, then a
single italic line. Skip if your source narrative doesn't have a "we
talked it over" moment — forcing it feels artificial.

```tsx
const Council: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Council Reflects" delay={0} />
    <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
      <AgentBadge agent="orchestrator" label="ORCH" size="sm" delay={5} />
      <AgentBadge agent="planner" label="PLAN" size="sm" delay={12} />
      <AgentBadge agent="worker" label="WORK" size="sm" delay={19} />
      <AgentBadge agent="retriever" label="GET" size="sm" delay={26} />
    </div>
    <TerminalLine delay={40} type="highlight" fontSize={26}>
      "Ship it. Log it. Learn from it."
    </TerminalLine>
  </SceneFrame>
);
```

## Stats

Numbers reveal. Use spring-animated cards. Pick 3-5 stats — fewer feels
thin, more is overwhelming on mobile.

```tsx
const StatCard: React.FC<{ label: string; value: string; delay: number; color: string }> = ({
  label, value, delay, color,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 12, stiffness: 90 } });
  return (
    <div
      style={{
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [20, 0])}px)`,
        padding: 32,
        borderRadius: 16,
        border: `2px solid ${color}`,
        background: `${color}11`,
        minWidth: 240,
      }}
    >
      <div style={{ fontSize: 72, fontWeight: 800, color, fontFamily: FONT_MONO }}>{value}</div>
      <div style={{ fontSize: 18, color: COLORS.muted, letterSpacing: "2px", textTransform: "uppercase", marginTop: 8 }}>
        {label}
      </div>
    </div>
  );
};

const Stats: React.FC = () => (
  <SceneFrame>
    <ActLabel text="By the Numbers" delay={0} />
    <div style={{ display: "flex", flexWrap: "wrap", gap: 24 }}>
      <StatCard label="agents"        value="7"  delay={10} color={COLORS.purple} />
      <StatCard label="tool calls"    value="46" delay={25} color={COLORS.cyan} />
      <StatCard label="minutes"       value="3"  delay={40} color={COLORS.warn} />
      <StatCard label="memory blocks" value="12" delay={55} color={COLORS.pink} />
    </div>
  </SceneFrame>
);
```

## Outro

Tagline + brand mark. Two lines max. Add a shimmer sweep across the
gradient text — that one detail elevates the whole cut.

```tsx
const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const shimmer = interpolate(frame, [0, 90], [-100, 200], { extrapolateRight: "clamp" });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <SceneFrame>
      <div style={{ opacity, position: "relative" }}>
        <div style={{ fontSize: 32, color: COLORS.muted, marginBottom: 32 }}>
          Tagline preamble. Three short clauses.
        </div>
        <div
          style={{
            fontSize: 88,
            fontWeight: 800,
            background: `linear-gradient(135deg, ${COLORS.purple}, ${COLORS.pink}, ${COLORS.warn})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            position: "relative",
          }}
        >
          The punchline.
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: `linear-gradient(90deg, transparent, ${COLORS.highlight}44, transparent)`,
              transform: `translateX(${shimmer}%)`,
              mixBlendMode: "overlay",
              pointerEvents: "none",
            }}
          />
        </div>
      </div>
    </SceneFrame>
  );
};
```

---

## Pacing reference

Default 50s breakdown — adjust frame ranges in your `<Sequence>` calls:

| Scene    | from | durationInFrames | Wall time |
|----------|------|------------------|-----------|
| Intro    | 0    | 90               | 0–3s      |
| Mission  | 90   | 90               | 3–6s      |
| Receive  | 180  | 120              | 6–10s     |
| Plan     | 300  | 120              | 10–14s    |
| Dispatch | 420  | 120              | 14–18s    |
| Gremlin1 | 540  | 90               | 18–21s    |
| Gremlin2 | 630  | 90               | 21–24s    |
| Gremlin3 | 720  | 90               | 24–27s    |
| Gremlin4 | 810  | 90               | 27–30s    |
| Results  | 900  | 90               | 30–33s    |
| Council  | 990  | 90               | 33–36s    |
| Stats    | 1080 | 180              | 36–42s    |
| Outro    | 1260 | 240              | 42–50s    |

**30s cut:** drop Council, halve Stats and Outro, shorten each Plan/Dispatch to 60 frames.
**60s cut:** add a second Mission beat (the "why this matters"), extend Outro to 360 frames, give Gremlins 120 frames each.
