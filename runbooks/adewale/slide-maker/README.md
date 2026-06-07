# adewale/slide-maker — demo payload

A launch payload for the `adewale/slide-maker` runbook: the optimized runbook, a
`manifest.json` (matching the directory detail-page mockup), and three worked example
decks — each a real production run with a `deck.pdf` and a thumbnail.

```
slide-maker/
  RUNBOOK.md                              # the runbook (v1.2.0)
  manifest.json                           # directory metadata: cta, example_outputs[], inputs[], secrets[], meta
  README.md                               # this file
  examples/
    jetty-pitch-deck/                     # project deck (GitHub repo) · bold-signal
      input.json  trajectory.json  thumbnail.png
      expected/  deck.pdf (primary) · slides.md · deck.spec.md · README.md · styles/ · summary.md · validation_report.json
    zod-pitch-deck/                       # project deck (public repo colinhacks/zod) · terminal-green
      input.json  trajectory.json  thumbnail.png  expected/ …
    verification-keynote/                 # brief-driven (no repo) · dark-botanical
      input.json  trajectory.json  thumbnail.png  expected/ …
```

## The gallery: three decks, three modes/styles

| # | Deck | Source | Style | Slides | Trajectory | Eval |
|---|------|--------|-------|--------|-----------|------|
| 1 | Investor pitch for Jetty | repo `jettyio/jettyio-skills` | bold-signal | 16 | `3d528c58` | ✓ |
| 2 | Developer pitch for Zod | repo `colinhacks/zod` | terminal-green | 14 | `224baedb` | ✓ |
| 3 | Keynote: The Verification Gap | brief (no repo) | dark-botanical | 12 | `24390596` | ✓ |

Each `expected/deck.pdf` is the headline deliverable. Thumbnails use a representative
**content slide** (covers can render sparse in `slidev export`).

## What changed (v1.0.0 → v1.2.0), driven by auditing real runs

The audit found a green 06-03 run that produced **no `deck.pdf`** and persisted **100+
`node_modules`/`dist` files** as "results", plus every run today failing in ~20s.

1. **Reliability — the run no longer stalls.** The runbook read the goal from a `$GOAL`
   environment variable that is never set, so the agent **asked the user "what should the
   deck cover?" and exited with zero files** (4/4 failures on 06-07). v1.2.0 reads the
   goal/mode/style from a `{{...}}` **Inputs block** (the parameter-substitution path that
   actually works) and an "execute now, don't ask" directive.
2. **`deck.pdf` is now a hard gate.** The old validation only checked `slidev build` (a
   static site), so runs passed with no PDF. v1.2.0 forces a real `slidev export`, adds a
   `pdf_export` validation stage, and fails the run if `deck.pdf` is missing.
3. **Results hygiene.** All Slidev project setup now happens in `/app/work`; only the
   deliverables land in `/app/results` (was 90+ `node_modules`/`dist` junk files, now 7
   clean files), enforced by a `results_hygiene` stage + a final scrub.
4. **`primary_outputs`** declares `[deck.pdf, slides.md]` so the UI surfaces the rendered
   deck as the headline artifact.

All three optimized runs are green with a real `deck.pdf` and clean results.

## Known limitations (honest)

- **Dark-preset fidelity is inconsistent.** `bold-signal`/`dark-botanical` do not always
  apply their page background — `styles/tokens.css` overrides aren't reliably honored by
  the default Slidev theme (Zod's terminal-green applied cleanly; Jetty's bold-signal
  stayed light). Documented in the runbook's Common Fixes.
- **Covers can render sparse** in `slidev export`. Content/section slides render well.

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"mode":"create","style_preset":"bold-signal","source_repo_url":"jettyio/jettyio-skills","goal_or_update_instructions":"investor pitch deck for Jetty (jetty.io)"}}' \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/slide-maker-grand-pearl"
```
