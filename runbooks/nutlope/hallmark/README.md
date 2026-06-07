# nutlope/hallmark — launch payload

A launch payload for the **Hallmark** runbook: a self-contained `RUNBOOK.md`, a
`manifest.json` (directory detail-page metadata), and four worked examples — each a real
production run on Jetty (`jon-runbooks/hallmark`).

Hallmark ([`Nutlope/hallmark`](https://github.com/Nutlope/hallmark), MIT) is an
anti-AI-slop design skill: a tight, opinionated rule set (21 macrostructures, a 20-theme
catalog, OKLCH tokens, a 58-gate slop test, a pre-emit self-critique) that makes the UI an
agent generates look **made, not generated**. Its differentiator is *structural* variety —
two pages for two briefs should feel like different sites, not colour-swaps of one template.

```
hallmark/
  RUNBOOK.md                       # the runbook (v1.0.0) — drives Hallmark's 4 verbs non-interactively
  manifest.json                    # directory metadata: cta, example_outputs[], inputs[], secrets[], meta
  README.md                        # this file
  examples/
    cricket-atmospheric/           # build · atmospheric AI app · Midnight theme · Narrative Workflow
      input.json  trajectory.json  thumbnail.png
      expected/  screenshot.png (hero) · index.html · styles.css · tokens.css · summary.md · validation_report.json
    marginalia-editorial/          # build · indie city quarterly · Almanac theme · Letter macrostructure
      input.json  trajectory.json  thumbnail.png  expected/ …
    audit-saas-slop/               # audit · a textbook AI-slop SaaS page (synthetic input)
      input/index.html  input.json  trajectory.json  thumbnail.png
      expected/  audit_report.md (primary) · summary.md · validation_report.json
    govuk-study/                   # study · GOV.UK URL-mode → portable design.md
      input.json  trajectory.json  thumbnail.png  expected/ …
```

## The gallery: four examples, four verbs

| # | Example | Operation | Result | Trajectory | Eval |
|---|---------|-----------|--------|-----------|------|
| 1 | Cricket — nocturnal AI app | `build` | Midnight theme · Narrative-Workflow macro · 58/58 gates | `e7dbdc23` | ✓ |
| 2 | Marginalia — city quarterly | `build` | Almanac theme · Letter macro · 58/58 gates | `cdbcaba1` | ✓ |
| 3 | Nimbus — AI-slop SaaS page | `audit` | **7 critical · 9 major · 4 minor** (24/58 gates fail) | `a45a609c` | ✓ |
| 4 | GOV.UK | `study` | portable `design.md` + OGL provenance | `4e4867f2` | ✓ |

Examples 1 and 2 are the proof of Hallmark's thesis: **same runbook, two briefs, two sites
that share nothing.** Cricket is a dark, atmospheric, screen-at-2am page with a four-stage
narrative workflow; Marginalia is a warm cream editorial letter from the editors. Different
theme, macrostructure, nav archetype, footer archetype, type pairing — no shared rhythm.

Each build's `expected/screenshot.png` is a real in-sandbox render (the gallery hero).
The audit/study thumbnails are rendered summary cards (those verbs emit Markdown, not a page).

## How the conversion works

Hallmark is ~930 KB across `SKILL.md` + ~40 `references/` files — far too large to inline
into a runbook. So the runbook **clones the skill at runtime** (Step 1) and instructs the
agent to read `SKILL.md` and lazy-load only the references it needs, while inlining the
**overrides** that make a famously interactive skill run unattended:

1. **Non-interactive gate.** Hallmark's SKILL.md *always* asks the user three questions
   (audience / use case / tone) before designing. In a sandbox there is no user, so the
   runbook forces "go ahead" mode: infer the three, pick a non-default macrostructure, and
   **state the inferences in `summary.md`**. This is the #1 thing that would otherwise hang
   the run (cf. the slide-maker `$GOAL` failure mode).
2. **Operation routing.** The four verbs become one `operation` parameter with
   **operation-conditional** outputs — `build`/`redesign` emit a page (+ screenshot),
   `audit` emits only a punch list (no edits), `study` emits only a `design.md`. Each run
   produces *only* its operation's deliverables; nothing leaks from the others.
3. **A real screenshot hero.** `build`/`redesign` render `index.html` to `screenshot.png`
   with the snapshot's headless Chromium — the page is judged on rendered pixels, not the
   agent's self-report.
4. **Results hygiene.** The clone, `node_modules/`, and `.hallmark/log.json` stay in
   `/app/work`; only deliverables land in `/app/results`. All four runs were clean.
5. **`primary_outputs`** declares `[screenshot.png, index.html, audit_report.md, design.md]`
   so Mise surfaces the right hero per operation (operation-aware, declaration order).

## Known limitations (honest)

- **Build/redesign need the `prism-playwright` snapshot** for the screenshot. On a
  non-browser snapshot the page still builds but the render degrades to `PARTIAL`.
- **Web fonts load over the network at render time.** Offline sandboxes fall back to each
  theme's system font stack (the page stays legible, the type loses its character).
- **`study` URL-mode can't judge rhythm** from HTML alone — it says so in the diagnosis —
  and falls back to a screenshot request on JS-only SPA shells or auth walls.
- **The non-interactive override disables Hallmark's design-context question.** That's the
  right call for unattended runs, but it means the agent commits to inferred audience/use/tone;
  those inferences are disclosed in `summary.md` so a human can redirect.

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"operation":"build","tone":"austere","genre":"atmospheric","theme":"auto","brief":"A landing page for Cricket — a late-night AI voice companion that captures, transcribes, and threads the half-formed ideas you have at 2am into something you can act on by morning."}}' \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/hallmark"
# audit instead: add -F "files=@page.html" and set "operation":"audit"
# study instead: set "operation":"study","target_url":"https://example.com"
```
