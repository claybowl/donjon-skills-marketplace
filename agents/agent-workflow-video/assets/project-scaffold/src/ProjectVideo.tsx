import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { AgentBadge } from "./components/AgentBadge";
import { TerminalLine } from "./components/TerminalLine";
import { ActLabel } from "./components/ActLabel";
import { MeshBackdrop } from "./components/MeshBackdrop";
import { ProgressBar } from "./components/ProgressBar";
import { COLORS, FONT_MONO, TOTAL_FRAMES } from "./theme";

/**
 * Starter narrative composition.
 *
 * Replace the scene contents below with your actual agent workflow.
 * See references/scene-patterns.md in the skill for templates for every
 * scene type (Intro, Mission, Receive, Plan, Dispatch, Gremlin, Stats,
 * Outro, etc.).
 *
 * Total runtime: 50s (1500 frames @ 30fps). Adjust TOTAL_FRAMES in
 * theme.ts if you need 30s or 60s.
 */

const SceneFrame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      padding: 80,
      justifyContent: "center",
      alignItems: "flex-start",
      color: COLORS.text,
      fontFamily: FONT_MONO,
    }}
  >
    {children}
  </AbsoluteFill>
);

// ---------- Scene 1: Intro ----------
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
            letterSpacing: "-2px",
            lineHeight: 1.05,
            background: `linear-gradient(135deg, ${COLORS.purple}, ${COLORS.pink}, ${COLORS.warn})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Agents at work.
        </div>
      </div>
    </SceneFrame>
  );
};

// ---------- Scene 2: Mission ----------
const Mission: React.FC = () => (
  <SceneFrame>
    <ActLabel text="The Mission" delay={0} />
    <TerminalLine delay={10} type="highlight" fontSize={44}>
      Build a competitive analysis landing page.
    </TerminalLine>
    <div style={{ height: 24 }} />
    <TerminalLine delay={40} type="default" fontSize={24}>
      — the user
    </TerminalLine>
  </SceneFrame>
);

// ---------- Scene 3: Receive ----------
const Receive: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Act I — Receive" delay={0} />
    <div style={{ marginBottom: 24 }}>
      <AgentBadge agent="orchestrator" label="ORCHESTRATOR" size="lg" glow delay={10} />
    </div>
    <TerminalLine delay={30} type="tool">read_block("agent_manifest")</TerminalLine>
    <TerminalLine delay={55} type="result">loaded 12 memory blocks</TerminalLine>
    <TerminalLine delay={80} type="highlight">Mission understood.</TerminalLine>
  </SceneFrame>
);

// ---------- Scene 4: Plan ----------
const Plan: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Act II — Plan" delay={0} />
    <div style={{ marginBottom: 24 }}>
      <AgentBadge agent="planner" label="PLANNER" size="lg" glow delay={10} />
    </div>
    <TerminalLine delay={30} type="tool">create_task(T1: "research competitors")</TerminalLine>
    <TerminalLine delay={50} type="tool">create_task(T2: "draft positioning")</TerminalLine>
    <TerminalLine delay={70} type="tool">create_task(T3: "build the page")</TerminalLine>
    <TerminalLine delay={90} type="tool">create_task(T4: "deploy")</TerminalLine>
    <TerminalLine delay={110} type="result">4 tasks created</TerminalLine>
  </SceneFrame>
);

// ---------- Scene 5: Dispatch ----------
const Dispatch: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Dispatch" delay={0} />
    <TerminalLine delay={10} type="dispatch">T1 → RETRIEVER</TerminalLine>
    <TerminalLine delay={30} type="dispatch">T2 → WRITER</TerminalLine>
    <TerminalLine delay={50} type="dispatch">T3 → WORKER</TerminalLine>
    <TerminalLine delay={70} type="dispatch">T4 → DEPLOYER</TerminalLine>
  </SceneFrame>
);

// ---------- Reusable Gremlin execution scene ----------
const Gremlin: React.FC<{
  agent: "retriever" | "writer" | "worker" | "deployer";
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
      <TerminalLine key={i} delay={25 + i * 18} type="tool">
        {t}
      </TerminalLine>
    ))}
    <TerminalLine delay={25 + tools.length * 18 + 15} type="result">
      {result}
    </TerminalLine>
  </SceneFrame>
);

// ---------- Scene 10: Results ----------
const Results: React.FC = () => (
  <SceneFrame>
    <ActLabel text="Results" delay={0} />
    <TerminalLine delay={10} type="result" fontSize={30}>
      ✓ 4 tasks complete
    </TerminalLine>
    <TerminalLine delay={35} type="result" fontSize={30}>
      ✓ Page live: donjon.agency/ca
    </TerminalLine>
    <TerminalLine delay={60} type="result" fontSize={30}>
      ✓ All checks green
    </TerminalLine>
  </SceneFrame>
);

// ---------- Scene 11: Council ----------
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
      “Ship it. Log it. Learn from it.”
    </TerminalLine>
  </SceneFrame>
);

// ---------- Scene 12: Stats ----------
const StatCard: React.FC<{ label: string; value: string; delay: number; color: string }> = ({
  label,
  value,
  delay,
  color,
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
    <div style={{ display: "flex", flexWrap: "wrap", gap: 24, marginTop: 16 }}>
      <StatCard label="agents" value="7" delay={10} color={COLORS.purple} />
      <StatCard label="tool calls" value="46" delay={25} color={COLORS.cyan} />
      <StatCard label="minutes" value="3" delay={40} color={COLORS.warn} />
      <StatCard label="memory blocks" value="12" delay={55} color={COLORS.pink} />
    </div>
  </SceneFrame>
);

// ---------- Scene 13: Outro ----------
const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const shimmer = interpolate(frame, [0, 90], [-100, 200], { extrapolateRight: "clamp" });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <SceneFrame>
      <div style={{ opacity, position: "relative" }}>
        <div style={{ fontSize: 32, color: COLORS.muted, marginBottom: 32, fontFamily: FONT_MONO }}>
          Orchestrator plans. Workers execute. You ship.
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
          Built to last.
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

// ---------- Composition ----------
export const ProjectVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: COLORS.bg, fontFamily: FONT_MONO }}>
    <MeshBackdrop />
    <ProgressBar totalFrames={TOTAL_FRAMES} />

    <Sequence from={0} durationInFrames={90}><Intro /></Sequence>
    <Sequence from={90} durationInFrames={90}><Mission /></Sequence>
    <Sequence from={180} durationInFrames={120}><Receive /></Sequence>
    <Sequence from={300} durationInFrames={120}><Plan /></Sequence>
    <Sequence from={420} durationInFrames={120}><Dispatch /></Sequence>

    <Sequence from={540} durationInFrames={90}>
      <Gremlin
        agent="retriever"
        agentLabel="RETRIEVER"
        taskId="T1"
        taskName="research competitors"
        tools={["web_search('competitive analysis SaaS')", "http_get('g2.com/category/...')"]}
        result="12 sources indexed"
      />
    </Sequence>

    <Sequence from={630} durationInFrames={90}>
      <Gremlin
        agent="writer"
        agentLabel="WRITER"
        taskId="T2"
        taskName="draft positioning"
        tools={["read_block('brand_voice')", "generate('positioning copy')"]}
        result="hero + 3 sections drafted"
      />
    </Sequence>

    <Sequence from={720} durationInFrames={90}>
      <Gremlin
        agent="worker"
        agentLabel="WORKER"
        taskId="T3"
        taskName="build the page"
        tools={["execute_python('scaffold.py')", "execute_bash('pnpm build')"]}
        result="page/index.tsx compiled"
      />
    </Sequence>

    <Sequence from={810} durationInFrames={90}>
      <Gremlin
        agent="deployer"
        agentLabel="DEPLOYER"
        taskId="T4"
        taskName="deploy"
        tools={["vercel deploy --prod"]}
        result="live at donjon.agency/ca"
      />
    </Sequence>

    <Sequence from={900} durationInFrames={90}><Results /></Sequence>
    <Sequence from={990} durationInFrames={90}><Council /></Sequence>
    <Sequence from={1080} durationInFrames={180}><Stats /></Sequence>
    <Sequence from={1260} durationInFrames={240}><Outro /></Sequence>
  </AbsoluteFill>
);
