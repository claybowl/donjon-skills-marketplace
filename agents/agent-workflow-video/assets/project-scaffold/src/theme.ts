/**
 * Palette, fonts, agent-color map, and timing constants.
 * Every component and scene pulls from this file — change the look by
 * editing COLORS / AGENT_COLORS here rather than editing components.
 */

export const COLORS = {
  bg: "#0a0e1a",
  bgRaised: "#111827",
  muted: "#64748b",
  subtle: "#475569",
  text: "#e5e7eb",
  highlight: "#ffffff",

  // Semantic
  success: "#22c55e",
  warn: "#f59e0b",
  danger: "#ef4444",

  // Accent ramp — reused by gradients and highlights
  purple: "#a855f7",
  green: "#22c55e",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#06b6d4",
  pink: "#ec4899",
  indigo: "#6366f1",
} as const;

export const FONT_MONO =
  "'SF Mono', 'Menlo', 'Monaco', 'Cascadia Code', 'Fira Code', 'Consolas', monospace";

export const FONT_SANS =
  "'Inter', 'SF Pro Text', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif";

/**
 * Add or rename agents here. The key becomes the `AgentKey` union type
 * used by <AgentBadge agent="..." />. Pick colors that stay legible on
 * the dark background and that feel distinct in motion.
 */
export const AGENT_COLORS = {
  user: "#e5e7eb",
  orchestrator: "#a855f7",
  planner: "#f59e0b",
  dispatcher: "#f59e0b",
  worker: "#06b6d4",
  retriever: "#22c55e",
  writer: "#ec4899",
  deployer: "#6366f1",
  system: "#64748b",
} as const;

export type AgentKey = keyof typeof AGENT_COLORS;

export const FPS = 30;
export const TOTAL_FRAMES = 1500; // 50s @ 30fps
