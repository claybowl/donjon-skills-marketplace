# Component Library

Five reusable components live in `src/components/`. Each consumes the
theme, so palette changes propagate without touching component code.

## AgentBadge

Color-coded pill representing an agent. The primary visual unit of these
cuts — use it any time an agent acts.

```tsx
<AgentBadge
  agent="orchestrator"     // AgentKey from theme.ts
  label="ORCHESTRATOR"     // displayed text (UPPERCASE)
  size="md"                // "sm" | "md" | "lg"
  glow={true}              // soft color-matched box-shadow
  delay={10}               // frames to wait before entering
/>
```

**When to use each size:**
- `sm` — pills in a row (Council scene, stats legend)
- `md` — standard per-scene agent identifier
- `lg` — hero moment (Receive, Plan, when an agent is THE subject)

**When to set `glow`:** hero moments and the first appearance of each agent. Turn it off for secondary appearances to avoid visual noise.

**Adding a new agent:**
1. Add a key + color to `AGENT_COLORS` in `theme.ts`
2. The `AgentKey` type picks it up automatically
3. Use `<AgentBadge agent="newAgent" label="NEW AGENT" />`

## TerminalLine

Typed-in line for tool calls, results, dispatches, or narration. Spring-
animates in from the left with a 1-frame-per-char feel.

```tsx
<TerminalLine
  delay={30}               // frames to wait
  type="tool"              // "tool" | "result" | "dispatch" | "highlight" | "default"
  fontSize={26}            // optional, defaults to 26
>
  web_search("competitive analysis")
</TerminalLine>
```

**Type semantics:**
- `tool` — cyan, `›` prefix. Use for tool invocations.
- `result` — green, `✓` prefix. Use for successful outputs.
- `dispatch` — amber, `▸` prefix. Use for task routing.
- `highlight` — white, no prefix. Use for agent speech / narrative lines.
- `default` — light gray, no prefix. Use for attributions and asides.

**Custom prefix:** pass `prefix="✗"` (or similar) to override the default.

**Spacing:** 10px margin-bottom is baked in. Don't wrap in extra divs for spacing — add a `<div style={{ height: 24 }} />` between logical groups instead.

## ActLabel

Small uppercase letter-spaced label above each scene's body. Gives the
viewer 10 frames to orient before the main content animates in.

```tsx
<ActLabel text="Act III — Execution" delay={0} />
```

**Rules of thumb:**
- Every scene should have one (except maybe Outro, where the tagline IS the label).
- Keep under 30 chars — letter-spacing eats horizontal room fast.
- Use em-dashes (—) not hyphens (-) for act separators. It looks sharper.

## MeshBackdrop

Drifting radial-gradient background. Drop it once at the top level —
don't instantiate per-scene.

```tsx
<AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
  <MeshBackdrop />
  <ProgressBar totalFrames={TOTAL_FRAMES} />
  {/* ...scenes... */}
</AbsoluteFill>
```

**Tuning the motion:** the speed is controlled by `frame * 0.008` inside
the component. Bump to `0.012` for faster aurora; drop to `0.005` for
glacial. Don't go above `0.02` — it starts to feel seasick on mobile.

**Tuning the colors:** the three gradients use `COLORS.purple`, `COLORS.cyan`, and `COLORS.pink` at low alpha (22, 18, 14 hex). Change those in `theme.ts` to shift the mood — amber/red for urgent, cyan/green for calm.

## ProgressBar

6px progress stripe at the top of the frame. Pure visual — no text. Fills
left-to-right over `totalFrames`.

```tsx
<ProgressBar totalFrames={TOTAL_FRAMES} />
```

**When to hide it:** for a 15-second hype cut you might want it off so
the viewer doesn't feel rushed. Comment it out at the top level.

---

## Adding new components

Stick to the conventions:

- Take `delay?: number` for entrance timing — viewers expect scenes to reveal progressively
- Consume `COLORS`, `FONT_MONO`, `AGENT_COLORS` from `theme.ts` — never hardcode hex
- Use `spring()` for scale/opacity entrances, `interpolate()` with `extrapolateRight: "clamp"` for translate/fade
- Default `fontSize` / `size` props so scenes can drop them in without ceremony

If the component is scene-specific (like `StatCard` in the Stats scene), inline it in `ProjectVideo.tsx`. If it's reusable across cuts, promote it to `components/`.
