import React from "react";
import { useCurrentFrame } from "remotion";
import { COLORS } from "../theme";

/**
 * 6px progress stripe pinned to the top of the frame. Fills left-to-right
 * over the life of the video — gives the viewer a non-verbal sense of
 * "how much is left." Pulls colors directly from the accent ramp.
 */
export const ProgressBar: React.FC<{ totalFrames: number }> = ({
  totalFrames,
}) => {
  const frame = useCurrentFrame();
  const progress = Math.min(frame / totalFrames, 1);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 6,
        background: "rgba(255, 255, 255, 0.05)",
        zIndex: 10,
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${progress * 100}%`,
          background: `linear-gradient(90deg, ${COLORS.purple}, ${COLORS.pink}, ${COLORS.warn})`,
          boxShadow: `0 0 12px ${COLORS.purple}88`,
        }}
      />
    </div>
  );
};
