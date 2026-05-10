# Publishing Notes

Per-platform specs and tactics for shipping these cuts.

## X (Twitter)

- **Format:** Upload the 9:16 MP4 directly. X handles the crop on desktop.
- **Max duration:** 140s for standard accounts, 10 min for Verified. You're at 50s — well under.
- **Max file size:** 512MB. Our output is ~40MB. Fine.
- **Codec:** H.264 / AAC. Remotion's default MP4 output is compliant.
- **Caption strategy:** X auto-generates captions from audio. Since this is silent-by-default, add a caption in the tweet itself — one sentence summarizing the pipeline ("Watch what happens when our orchestrator picks up a task"). Don't explain the video.
- **Thumbnail:** use `npm run still` to generate a PNG. Pick a Stats or Intro frame.

## LinkedIn

- **Mobile feed:** 9:16 MP4.
- **Desktop feed:** 1:1 MP4 performs better — less content gets clipped above the fold.
- **Max duration:** 10 minutes. Way over what we need.
- **Post structure:** the hook line is the first 120 chars (everything before "...see more"). Make it count. Don't describe the video — pose a question or a claim.
- **Why LinkedIn matters more here:** posts with video see ~5× the engagement of text-only. The algorithm also favors dwell time, and a 50s cut that people actually watch clears a very high bar.

## Instagram Reels

- **Format:** 9:16 MP4.
- **Max duration:** 90s. We're fine.
- **Tactic:** add music. Instagram's algorithm leans heavily on trending audio. The default silent cut will underperform on Reels.
- **Cover image:** use a Stats card frame, not the Intro — gives browsers something concrete to see at a glance.

## TikTok

- **Format:** 9:16 MP4.
- **Max duration:** 10 min. Ours is 50s. Fine.
- **Tactic:** same as Reels — add music. A silent cut gets eaten by the algorithm.
- **Text overlay:** consider adding a text hook in the first frame ("How our AI ships a landing page in 3 minutes"). TikTok viewers decide in <1 second.

## YouTube Shorts

- **Format:** 9:16 MP4, max 60s.
- **Trim target:** you're at 50s — leaves 10s of buffer. Don't pad.
- **Thumbnail:** Shorts use the first frame; make sure your Intro scene reads well at 1 frame (not just in motion).

---

## Sizing cheat sheet

| Platform       | Best format | Why                                    |
|----------------|-------------|----------------------------------------|
| X mobile       | 9:16        | Takes the full column                  |
| X desktop      | 1:1         | Less dead space left/right             |
| LinkedIn mobile| 9:16        | Full-feed immersion                    |
| LinkedIn desktop| 1:1        | Above-the-fold without scrolling       |
| IG Reels       | 9:16        | Native                                 |
| IG Feed        | 1:1         | Native                                 |
| TikTok         | 9:16        | Native                                 |
| YT Shorts      | 9:16        | Native                                 |

---

## Caption strategy

The cuts are designed to read without audio. But if you want spoken
captions:

1. Write a 50s voiceover script matching the scene beats
2. Record it (or generate with an ElevenLabs-style TTS)
3. Drop into `public/vo.mp3`
4. Add `<Audio src={staticFile("vo.mp3")} />` in the composition
5. Remotion will mix it into the render

For burned-in subtitles: export an `.srt` with the scene timestamps, then
upload alongside the video (LinkedIn, X, and YT all accept `.srt` upload
separately).

---

## Render settings to know

From `package.json`:

```sh
npm run render         # vertical MP4, ~40MB
npm run render:square  # square MP4, similar size
npm run render:gif     # vertical GIF, ~15MB, no audio, loops
npm run still          # single PNG at frame 45
```

For higher-quality renders (e.g. 4K vertical for LinkedIn ads):

```sh
npx remotion render DonjonVertical out/4k.mp4 \
  --scale=2 \
  --concurrency=4
```

This doubles pixel density without re-authoring anything. Expect ~3-5×
render time.
