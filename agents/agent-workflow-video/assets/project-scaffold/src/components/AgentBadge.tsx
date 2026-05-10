import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AGENT_COLORS, AgentKey, FONT_MONO } from "../theme";

type Size = "sm" | "md" | "lg";

const SIZE_MAP: Record<Size, { paddingY: number; paddingX: number; font: number; radius: number }> = {
  sm: { paddingY: 6, paddingX: 12, font: 16, radius: 6 },
  md: { paddingY: 10, paddingX: 18, font: 22, radius: 10 },
  lg: { paddingY: 14, paddingX: 24, font: 30, radius: 12 },
};

export const AgentBadge: React.FC<{
  agent: AgentKey;
  label: string;
  size?: Size;
  glow?: boolean;
  delay?: number;
}> = ({ agent, label, size = "md", glow = false, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const color = AGENT_COLORS[agent];
  const { paddingY, paddingX, font, radius } = SIZE_MAP[size];

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 10,
        padding: `${paddingY}px ${paddingX}px`,
        borderRadius: radius,
        background: `${color}22`,
        border: `1.5px solid ${color}`,
        color: color,
        fontFamily: FONT_MONO,
        fontSize: font,
        fontWeight: 600,
        letterSpacing: "2px",
        textTransform: "uppercase",
        transform: `scale(${enter})`,
        opacity: enter,
        boxShadow: glow ? `0 0 30px ${color}55` : "none",
      }}
    >
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: 4,
          backgroundColor: color,
          boxShadow: `0 0 8px ${color}`,
        }}
      />
      {label}
    </div>
  );
};
