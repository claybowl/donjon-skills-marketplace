import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_MONO } from "../theme";

type LineType = "tool" | "result" | "dispatch" | "highlight" | "default";

const PREFIX: Record<LineType, string> = {
  tool: "›",
  result: "✓",
  dispatch: "▸",
  highlight: "",
  default: "",
};

const COLOR: Record<LineType, string> = {
  tool: COLORS.cyan,
  result: COLORS.success,
  dispatch: COLORS.warn,
  highlight: COLORS.highlight,
  default: COLORS.text,
};

export const TerminalLine: React.FC<{
  delay: number;
  children: React.ReactNode;
  type?: LineType;
  prefix?: string;
  fontSize?: number;
}> = ({ delay, children, type = "default", prefix, fontSize = 26 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, stiffness: 110 },
  });

  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const x = interpolate(enter, [0, 1], [-16, 0]);

  const displayedPrefix = prefix ?? PREFIX[type];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        gap: 12,
        opacity,
        transform: `translateX(${x}px)`,
        fontFamily: FONT_MONO,
        fontSize,
        color: COLOR[type],
        lineHeight: 1.4,
        marginBottom: 10,
      }}
    >
      {displayedPrefix ? (
        <span style={{ color: COLOR[type], opacity: 0.85, minWidth: 24 }}>
          {displayedPrefix}
        </span>
      ) : null}
      <span>{children}</span>
    </div>
  );
};
