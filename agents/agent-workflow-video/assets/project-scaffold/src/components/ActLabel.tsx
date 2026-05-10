import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONT_MONO } from "../theme";



export const ActLabel: React.FC<{ text: string; delay?: number }> = ({
  text,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [delay, delay + 15], [-10, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${y}px)`,
        color: COLORS.muted,
        fontFamily: FONT_MONO,
        fontSize: 22,
        letterSpacing: "4px",
        marginBottom: 24,
        textTransform: "uppercase",
      }}
    >
      {text}
    </div>
  );
};
