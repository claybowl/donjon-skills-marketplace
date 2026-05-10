# Agent Workflow Video — Remotion

Programmatic social cut for an agent / workflow narrative, built with
[Remotion](https://remotion.dev). Ships two compositions out of the same
codebase:

| Composition      | Resolution | Use for                                       |
|------------------|-----------|-----------------------------------------------|
| `DonjonVertical` | 1080×1920 | X, LinkedIn mobile, Reels, Shorts, TikTok     |
| `DonjonSquare`   | 1080×1080 | LinkedIn desktop feed, X desktop, IG feed     |

Default runtime: **50 seconds** (1500 frames @ 30fps).

---

## Install & Preview

```sh
npm install              # or pnpm install
npm run dev              # opens Remotion Studio at http://localhost:3000
```

In Studio you can scrub the timeline, toggle between the vertical and square
compositions, and preview every scene in isolation.

## Render

```sh
# Vertical 9:16 MP4 → out/video-vertical.mp4
npm run render

# Square 1:1 MP4 → out/video-square.mp4
npm run render:square

# GIF (smaller, looping, no audio) → out/video.gif
npm run render:gif

# Single still frame for thumbnails → out/preview.png
npm run still
```

---

## Structure

```
src/
├── index.ts              # registerRoot entry
├── Root.tsx              # two <Composition> registrations
├── ProjectVideo.tsx      # the whole narrative, one file
├── theme.ts              # palette, fonts, agent → color map, constants
└── components/
    ├── AgentBadge.tsx    # color-coded agent pill
    ├── TerminalLine.tsx  # tool/result/dispatch typed-in lines
    ├── ActLabel.tsx      # "ACT III — EXECUTION" style header
    ├── MeshBackdrop.tsx  # slow-drifting radial gradients
    └── ProgressBar.tsx   # top-of-frame progress stripe
```

---

## Customize the mission

The mission text is hard-coded in the `Mission` scene (inside
`ProjectVideo.tsx`). To change it, edit the string directly:

```tsx
const mission = "Build a competitive analysis landing page for X";
```

For per-render dynamic text, wire it through Zod (see Remotion docs).

---

## Adding music

Drop an MP3 into `public/` (create the folder if needed) and use Remotion's
`<Audio>` component inside the top-level composition:

```tsx
import { Audio, staticFile } from "remotion";

<Audio src={staticFile("bgm.mp3")} volume={0.35} />
```

Pick a track that's calm/confident for the first 30s and lifts at the Stats
reveal. Hip-hop instrumentals, cinematic trailer builds, or synthwave all
work with the dark palette.

---

## Publishing notes

- **X (Twitter):** Upload the 9:16 MP4 directly. Max 140s, 512MB.
- **LinkedIn:** 9:16 for mobile, 1:1 for desktop. Posts with video see ~5×
  more engagement than text.
- **Captions:** Both platforms auto-generate captions. Override with an
  `.srt` if you want exact phrasing.

Built to last. Progress to stay.
