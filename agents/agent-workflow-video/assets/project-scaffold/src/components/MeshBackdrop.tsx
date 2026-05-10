import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS } from "../theme";

/**
 * Slow-drifting radial gradients. Pure CSS, no images. Creates that
 * subtle "aurora" motion behind every scene so static frames don't
 * feel frozen.
 */
export const MeshBackdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame * 0.008;

  const x1 = 30 + Math.sin(t) * 20;
  const y1 = 30 + Math.cos(t * 0.7) * 20;
  const x2 = 70 + Math.cos(t * 1.2) * 18;
  const y2 = 70 + Math.sin(t * 0.9) * 18;
  const x3 = 50 + Math.sin(t * 1.5) * 25;
  const y3 = 50 + Math.cos(t * 1.1) * 25;

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(circle at ${x1}% ${y1}%, ${COLORS.purple}22 0%, transparent 40%),
          radial-gradient(circle at ${x2}% ${y2}%, ${COLORS.cyan}18 0%, transparent 40%),
          radial-gradient(circle at ${x3}% ${y3}%, ${COLORS.pink}14 0%, transparent 50%),
          ${COLORS.bg}
        `,
      }}
    />
  );
};
