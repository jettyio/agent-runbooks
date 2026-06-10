# aapersh/diagnosis-and-framing — demo payload

A launch payload for the `aapersh/diagnosis-and-framing` runbook: the runbook, a
`manifest.json`, and two worked examples — each a **real production Jetty run** that takes a
business situation + a decision and hands back a single board-ready strategic diagnosis.

```
diagnosis-and-framing/
  RUNBOOK.md                        # the runbook (v1.0.0, python312-uv snapshot)
  manifest.json                     # directory metadata
  README.md                         # this file
  examples/
    meridian-series-b/              # vertical SaaS — should we raise a $40M Series B?
      input.json  trajectory.json  thumbnail.png
      expected/  diagnosis.md (primary) · summary.md · validation_report.json
    lumen-b2b-pivot/                # consumer subscription — pivot to B2B or fix the funnel?
      input.json  trajectory.json  thumbnail.png  expected/ …
```

## Attribution

Migrated, with attribution, from **01 — Diagnosis & Framing** in
[aapersh/strategy-skills-for-claude](https://github.com/aapersh/strategy-skills-for-claude/tree/main/skills/01-diagnosis-and-framing)
— a collection of McKinsey-style strategy skills for Claude (independent and unofficial; no
LICENSE file in the source repo). The source "skill" is a bundle of three method files —
`situation-assessment.md`, `growth-barriers.md`, and `assumption-audit.md`. This runbook
**composes all three into a single diagnosis pass** so a reviewer gets one board-ready
artifact instead of three separate analyses. The MBB method itself (MECE structure,
hypothesis-led, fact-before-recommendation, 80/20 focus) is general consulting practice; this
is a re-expression of the method with attribution, not a copy.

## What it does

You describe a business situation in plain language — with whatever facts you have (ARR,
growth, retention, unit economics, competitive signals) — and the decision in front of you.
The agent runs the diagnosis the way a top-tier consultant would, **in order**:

1. **Situation Assessment** — build a fact base, separating **facts vs. interpretations vs.
   assumptions**, each with a confidence label, across a MECE set of lenses (financial,
   market, customer, competitive, operating, org). Momentum and trend, not just a snapshot.
2. **Growth Barrier** — build the growth driver tree, find where it breaks, and isolate the
   **one** binding constraint — separating root cause from symptom — instead of listing ten
   issues.
3. **Assumption Audit** — surface the **load-bearing** beliefs the strategy rests on
   (including the implicit ones), grade them by importance and evidence strength, and turn the
   weak ones into a **test plan with owners and decision triggers**.
4. **Framed Recommendation** — a single explicit verdict: **Proceed / Pause / Test first /
   Redesign**, anchored to the constraint and the audit, with what would change it.

The headline deliverable is `diagnosis.md`. A programmatic self-check (`validation_report.json`)
enforces the method's non-negotiables — fact base with confidence, a single binding constraint,
a test plan with owners + triggers, an explicit verdict — so a structurally weak pass can't slip
through.

## The gallery: two decisions, two industries

| # | Subject | Decision | Binding constraint | Verdict | Trajectory |
|---|---------|----------|--------------------|---------|-----------|
| 1 | Meridian (vertical SaaS) | Raise a $40M Series B to go upmarket into DSOs? | Free competitive substitution in the core + an un-scoped DSO product gap | **Test first** | `3fcd1c83` |
| 2 | Lumen (consumer app) | Pivot to B2B corporate wellness, or fix the funnel? | 8.5% monthly churn — growth is zero-sum until it's fixed | **Test first** | `1646887f` |

Both ran green on Jetty's `python312-uv` snapshot with `claude-code` / `claude-sonnet-4-6`,
each **12/12** structural checks PASS (358s and 214s respectively). Both companies are fully
**synthetic** — safe to publish and to fork. Notice that both land on **"Test first"**: that's
the method working, not a bug. The discipline of this diagnosis is that it refuses to
rubber-stamp an expensive, under-derisked bet — it tells you exactly which 2–3 tests would
turn the verdict into "Proceed".

## Reproduce (example 1)

```bash
TOKEN="$(cat ~/.config/jetty/token)"   # a jon-runbooks-scoped Jetty token
A="https://flows-api.jetty.io"

# situation + decision come straight from examples/meridian-series-b/input.json
INIT=$(jq -n --argjson v "$(jq .params.vars examples/meridian-series-b/input.json)" '{vars: $v}')
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string "init_params=$INIT" \
  "$A/api/v1/run/jon-runbooks/diagnosis-and-framing" | jq .workflow_id
```

Then poll the trajectory (`workflow_id`'s 8-hex suffix after `--`) until `completed` and
download `diagnosis.md`. See the runbook's Final Checklist for the verification script.

## Notes for the directory

`manifest.json` + `examples/` are the source of truth for the directory detail page
(gallery tiles, sample outputs, inputs). The runbooks-directory site currently ingests only
`RUNBOOK.md`; these are shipped ahead of that ingest work and surface via "View source" in the
meantime. Never commit a runbook's `results/` output — only `examples/`.
