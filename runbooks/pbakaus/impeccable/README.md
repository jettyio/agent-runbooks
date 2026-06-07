# pbakaus/impeccable — de-slop a UI — demo payload

A **self-contained launch payload** for the `pbakaus/impeccable` runbook: the runbook
itself, three worked examples (real slop inputs + real Jetty outputs, each backed by a
green production trajectory), rendered thumbnails, and a `manifest.json` so the public
runbook directory can render a "try-this / here's-what-you-get" page.

```
impeccable/
  RUNBOOK.md                              # the runbook (v1.0.0)
  manifest.json                           # directory metadata: cta, example_outputs[], inputs[], meta, attribution
  README.md                               # this file
  examples/
    saas-hero-audit/                      # EXAMPLE 1 — audit (report only)
      input.html                          #   a textbook AI-slop SaaS hero (synthetic)
      input.json  trajectory.json  thumbnail.png
      expected/  audit_report.md (primary) · audit_report.json · audit_before.json · summary.md · validation_report.json
    saas-hero-polish/                     # EXAMPLE 2 — polish the same hero to zero
      input.json  trajectory.json  thumbnail.png    (shares example 1's input.html)
      expected/  polished.html (primary) · before_after.md · audit_before.json · audit_after.json · summary.md · validation_report.json
    pricing-cards-polish/                 # EXAMPLE 3 — polish a different surface to zero
      input.html (synthetic)  input.json  trajectory.json  thumbnail.png
      expected/  polished.html (primary) · before_after.md · audit_before.json · audit_after.json · summary.md · validation_report.json
```

## What it does

`impeccable detect` is the deterministic anti-pattern scanner that ships with Paul
Bakaus's [**impeccable**](https://github.com/pbakaus/impeccable) design skill. It reads
an HTML/CSS/JSX file (or a directory, or a live URL) and flags the tells that mark a UI
as AI-generated — gradient text, Inter/Roboto everywhere, side-tab accent borders,
nested cards, dark-mode glows, bounce easing, low-contrast text (WCAG ratios computed),
broken/placeholder images, and SaaS buzzword copy — and **exits `2` when it finds any,
`0` when the page is clean.**

This runbook wraps that scanner in two operations:

| Operation | What happens | Primary output |
|-----------|--------------|----------------|
| **`audit`** | Scan, report every finding, **change nothing** | `audit_report.md` |
| **`polish`** | Scan → rewrite the artifact to remove every finding → **re-scan to prove zero** | `polished.html` |

Because the same tool finds the slop and verifies the fix, evaluation is fully
programmatic and needs no LLM judge: **a polish run succeeds only when the re-scan exits
`0` with no new findings introduced.**

## The gallery: detect → fix → fix (one tool, both roles)

All three are **real production runs** on `jon-runbooks/impeccable-deslop` (Jetty,
claude-code / claude-sonnet-4-6):

| # | Capability | Operation | Input | Result | Trajectory | Eval |
|---|-----------|-----------|-------|--------|-----------|------|
| 1 | **Detect** | `audit` | AI-slop SaaS hero | 22 anti-patterns reported (13 slop + 9 quality) | [`b8bda6fc`](https://flows.jetty.io/jon-runbooks/impeccable-deslop/b8bda6fc) | ✓ |
| 2 | **Fix** | `polish` | the same hero | de-slopped, scans clean — **22 → 0** | [`2fc20cfd`](https://flows.jetty.io/jon-runbooks/impeccable-deslop/2fc20cfd) | ✓ |
| 3 | **Fix** | `polish` | AI-slop pricing section | de-slopped, scans clean — **10 → 0** (2 rounds) | [`8dce2661`](https://flows.jetty.io/jon-runbooks/impeccable-deslop/8dce2661) | ✓ |

Example 1's hero trips fourteen distinct rules, including `side-tab` ×3, `low-contrast`
×6, `gradient-text` ×2, `overused-font`, `single-font`, `ai-color-palette`, `dark-glow`,
`hero-eyebrow-chip`, `oversized-h1`, `extreme-negative-tracking`, `marketing-buzzword`,
`broken-image`, `skipped-heading`, and `tight-leading`. Example 3 adds `bounce-easing`
on a different surface, so the gallery exercises slop, accessibility, layout, motion, and
copy rules.

The before/after for example 2 (verbatim from its `validation_report.json`):

```json
{ "before_count": 22, "after_count": 0, "overall_passed": true }
```

and the polished re-scan (`expected/audit_after.json`) is literally `[]`.

## Reproduce (locally — no Jetty needed)

The detector is deterministic, so every `expected/` file regenerates from the inputs
with the **published** CLI (Node ≥ 24 required — `impeccable`'s `engines.node`):

```bash
npx --yes impeccable@latest detect --json examples/saas-hero-audit/input.html             # -> 22 findings, exit 2
npx --yes impeccable@latest detect --json examples/saas-hero-polish/expected/polished.html     # -> [] exit 0
npx --yes impeccable@latest detect --json examples/pricing-cards-polish/expected/polished.html # -> [] exit 0
```

> The published `npx impeccable@latest` and the Jetty run agree exactly (22 on the hero).
> A raw `git clone` + `node cli/bin/cli.js` reports fewer because the checkout's CLI
> bundle isn't built — always use `npx impeccable@latest` (or `npm run build` the repo
> first).

## Provenance & licensing

- **Outputs are real Jetty production runs**, not mocked. The runbook was deployed to
  `jon-runbooks/impeccable-deslop` and run once per example; each `expected/` folder is
  the actual run output, each `trajectory.json` carries the real `trajectory_id`, eval,
  and timing, and the polished pages are the agent's own work (verified clean by the
  production detector — a re-scan exiting `0`).
- **The production detector is thorough.** It computes WCAG contrast ratios and DOM
  structure, so the hero audit surfaced 22 issues (6 of them contrast failures), not just
  the surface-level slop tells.
- **Inputs are license-clean.** The slop inputs and all copy are hand-authored synthetic
  samples (no third-party content), safe to redistribute.

## Attribution (Apache-2.0)

This runbook wraps the `impeccable` skill's detector and carries its credit forward:

- **impeccable** © 2025–2026 **Paul Bakaus** — https://github.com/pbakaus/impeccable — Apache-2.0
- Builds on **Anthropic's frontend-design skill** (Apache-2.0, © 2025 Anthropic, PBC)
- Typography reference incorporates additions from **ehmo's typecraft-guide-skill**

The full upstream `NOTICE` is mirrored in the runbook's frontmatter (`origin.notice`)
and in `manifest.json` → `meta.attribution`. The runbook scopes the **de-slop**
capability (detect + polish) out of impeccable's full 23-command skill; the other
commands (craft, shape, animate, colorize, …) are out of scope here.

## Known follow-ups

- **URL + component modes** are supported but not yet captured as examples (see
  `manifest.json` → `demo_ideas`): a live-URL audit (browser engine) and a React/Tailwind
  `.tsx` polish (regex engine, proves it isn't HTML-only).
- **Snapshot Node version.** The runs succeeded on the `python312-uv` snapshot (Step 1
  installs Node ≥ 24 as needed). If a future snapshot ships Node ≥ 24 by default, the
  install step becomes a no-op.
- **The directory site ingests only `RUNBOOK.md`** today — the `manifest.json` +
  `examples/` gallery is forward-looking and needs the ingest + detail-page change to
  render (same limitation noted for the sibling payloads).
