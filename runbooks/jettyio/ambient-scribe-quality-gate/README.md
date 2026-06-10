# ambient-scribe-quality-gate

Treat **prompt quality like a test suite**. This runbook is the eval an ambient AI medical-scribe team actually runs: it generates synthetic clinical encounters with a **known answer key**, has a scribe model write the SOAP note, scores it with an **independent judge**, and then **hill-climbs** the scribe prompt until it clears a verifiable gate — logging every iteration so the climb is visible.

Synthetic data only. No PHI, no real patients — every case is generated in-workflow.

## Why it's interesting

- **Long-running agentic workflow** — a panel of N encounters, each running generate → scribe → judge → iterate, is dozens of sequential model calls captured durably as one trajectory.
- **Hill-climb with a runbook** — a declared rubric + pass threshold, self-scored, with the single weakest criterion re-rolled until the gate is met. The iteration log is the deliverable.
- **An honest eval** — a *hard hallucination floor* (computed in code, not from the judge's vibe) caps any note that invents a claim the transcript doesn't support, and the judge is always a **different model than the scribe** so it can't rubber-stamp its own output.

## How it works (per encounter)

| Stage | What it does | Emits |
|-------|--------------|-------|
| Case author | Writes a structured ground-truth case sheet with one embedded **trap** (a stopped med, a denied symptom, an indirectly-stated value, a relative's condition) | `case_sheets.json` |
| Transcript synth | Turns the case sheet into a messy spoken visit transcript containing every fact + the trap, out of order | `transcripts/encounter_NN.md` |
| Scribe (under test) | Writes a SOAP note from the **transcript only** — never sees the answer key | `notes/encounter_NN.md` |
| Judge (independent) | Scores 5 criteria vs the ground truth and extracts any unsupported claims | `scorecards/encounter_NN.json` |

If the note fails the gate (`overall ≥ 4.0`, no criterion below 3, zero hallucinations), the runbook appends the targeted fix for the weakest criterion and re-rolls — up to 3 rounds.

## What's here

| File | What it is |
|------|------------|
| `RUNBOOK.md` | The runbook. Self-contained: it writes its own LLM helper, generates the panel, runs the scribe/judge/hill-climb loop, and scores against a 5-criterion rubric with a hard hallucination floor. |

## Run it

### On jetty.io (recommended)

Run this runbook and Jetty executes it in a sandbox, returning the leaderboard, per-encounter scorecards, the hill-climbed scribe prompt, and a validation report. Configure the scribe and judge as collection environment variables / parameters:

- `scribe_model` — the model under test (e.g. `anthropic/claude-sonnet-4-6`)
- `judge_model` — must differ from the scribe; cross-vendor is strongest (e.g. `openai/gpt-4o`)
- `panel_size` — number of synthetic encounters (4 for a quick walkthrough, 8–12 for a real run)
- `max_iterations` (default 3) · `pass_threshold` (default 4.0)

Needs `ANTHROPIC_API_KEY` (scribe + judge via litellm); set `OPENAI_API_KEY` to use a cross-vendor judge.

**Model bake-off mode.** Upload a shared panel (`case_sheets.json` + `transcripts/encounter_*.md` from a prior run) and the runbook reuses it verbatim instead of generating — so several scribe models can be compared apples-to-apples on identical transcripts.

### Locally

Point an agent at `RUNBOOK.md`, set `ANTHROPIC_API_KEY`, and it writes everything to `./results`.

## Output

`leaderboard.md` (per-criterion baseline → final, pass rate, hallucinations caught) · `scribe_prompt_final.md` (the hill-climbed prompt a team would ship) · `summary.md` · `validation_report.json` · plus `notes/`, `transcripts/`, and `scorecards/` per encounter.
