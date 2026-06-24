# /brag — Launch Video (Jetty runbook)

**You built it. Now brag.** Point this runbook at a project URL (or upload the project files) and
it turns the project into a short, shareable launch video — music, motion, and share copy included.

Converted, with attribution, from [`latent-spaces/brag`](https://github.com/latent-spaces/brag), a
Claude Code skill. This runbook adapts it to the Jetty sandbox:

- **Input** is a project **URL** (captured with `hyperframes capture`) or **uploaded files** in
  `/app/assets/`, instead of the local working directory.
- It clones the source repo at run time for its bundled **music + SFX** and step references.
- It composes and renders **locally** with [`npx hyperframes`](https://www.npmjs.com/package/hyperframes)
  (headless Chromium + FFmpeg) — **no API key required**.

## Flow

1. **Inspect** — read the project, answer the 9-question brag rubric (what it is, the hook, the
   real UI to show, the user flow).
2. **Plan** — write `brag-plan.md`: angle, hook, key moments, tone, visual identity, and a
   beat-by-beat storyboard that sums to 15–25s.
3. **Compose** — hand a focused brief to Hyperframes; scaffold and build `composition/`; `lint`.
4. **Render** — `brag.mp4` (15–25s), snapshot key frames, write `share-copy.txt`.

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `brag.mp4` | The rendered launch video |
| `brag-plan.md` | The creative plan + storyboard |
| `composition-brief.md` | The Hyperframes handoff brief |
| `share-copy.txt` | The postable caption |
| `composition/` | The Hyperframes project |

## Tones

`default` · `polished` · `yc-parody` · `chaotic` · `deadpan` · `cinematic` · `app-store` — or a
freeform creative direction. Presets are defaults, not limits.

## Credits

Music — [ende.app](https://ende.app/en) · SFX — [Kenney](https://kenney.nl/) · Video generation —
[Hyperframes](https://hyperframes.heygen.com/) · Demo sites — [Impeccable](https://impeccable.style/).
The example thumbnails are reference brags from the source project's benchmark suite.
