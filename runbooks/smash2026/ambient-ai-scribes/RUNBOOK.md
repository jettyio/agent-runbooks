---
version: "1.0.0"
evaluation: programmatic
evals_version: 2
agent: claude-code
model: anthropic/claude-haiku-5.5
model_provider: openrouter
snapshot: python312-uv
primary_outputs:
  - result_card.html
origin:
  attribution:
    collection_or_org: jon-smash2026
    skill_name: smash-08-scribe-reality-check
    confidence: high
---

# Scribe Reality Check: Edit Burden vs. the Promise (SMASH 2026 · Paper #8)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Implementing Ambient Artificial Intelligence (AI) Scribes in Hospital-based Specialty Care: A Mixed-Methods Evaluation on Administrative Burden and Clinical Workflows"** (Nishila Mehta, Emily Ha, Andrew Gordon, Rodica Balaci, Onil Bhattacharya, Geetha Mukerji).
Read the paper: https://drive.google.com/file/d/1I4e3YIe7SLrZE1yJefyni5q4t2k4JwKW/view?usp=sharing

The paper's finding: an EHR-integrated ambient AI scribe (Microsoft Dragon Copilot, Epic) was feasible in
hospital-based specialty clinics, **but it did not by itself reduce documentation burden**. Adoption was
heterogeneous. Most generated notes needed editing, especially where specialty formats and personal style mattered.
EHR data showed longer notes and more editing time. The value depended "less on availability alone and more on
effective workflow integration, tool features and customization to clinical context." Implementation reality is not
the vendor promise.

The participant runs both halves of that story:
1. **Edit-burden lab** (LLM, about 36 small calls). Six synthetic specialty encounters (psychiatry ×2, endocrinology ×2,
   rheumatology, internal medicine; fictional patients), plus optionally the participant's own transcript, go through
   an ambient-scribe draft (generic SOAP *or* customized to the specialty template). A simulated specialist then makes
   the minimum edits needed to sign it, following the specialty template **and a personal style the scribe was never
   told about**. Outputs: word-level edit burden, PDQI-9-style rubric scores and an error list (LLM judge),
   planted-fact recall (rules), and modelled minutes per note.
2. **Implementation model** (no LLM). The paper's adoption funnel and usage distribution, combined with the
   participant's clinic assumptions and the minutes measured in part 1, give clinician-hours saved per month. These are
   compared with a "promise" scenario and a ladder of implementation levers (customization, consent and trainee
   workflows, activating every enrollee, full adoption).

Output: a shareable **result card**. Target wall-clock: **under 5 minutes**; the experiment takes about 30–70 s.

### The time model (this runbook's assumptions, not the paper's)
- Finalizing a scribe draft = read it at 200 wpm + type inserted/substituted words at `edit_sec_per_word` + deletions
  at a quarter of that + 0.5 min overhead (consent, start/stop, transfer to the EHR).
- Net minutes saved per note = `baseline_doc_minutes` (writing the note yourself) − finalizing time.
- Usage among active users: lognormal fitted to the paper's median 0.94% and IQR 3.04% of encounters (σ ≈ 1.87),
  capped at the paper's maximum of 18.4%. Funnel: 140 eligible → 43 enrolled → 21 active (paper ratios).
- Listed barriers: a share `patient_decline_rate` of encounters is declined and `trainee_share` is trainee-led
  (trainees are "not permitted to use an AI scribe"). Removing them scales usage by 1 / ((1 − decline)(1 − trainee)).
- Hours/month = active users × `encounters_per_month` × usage share × net minutes / 60. A Monte Carlo over enrolment,
  activation, usage and notes gives a 90% interval for the "pilot reality" rung.

### Paper headline numbers (quote exactly)
- 140 eligible HCPs; **43** enrolled; **21 (49%)** used the AI scribe for at least one encounter (interim, ~3 months).
- Encounters with the scribe per user: range 1-132 (median 11, IQR 26.5); proportion of encounters 0.05-18.4%
  (**median 0.94%**, IQR 3.04%).
- 17 mid-pilot survey respondents: **52%** easy to use; **88%** reported that generated notes required frequent
  editing; **29%** reduced documentation time; **41%** overall time savings; **59%** more engaged with patients;
  **65%** patients reacted positively.
- Barriers: Epic integration (n=5), inaccurate content information (n=4), mismatch with specialty-specific
  documentation requirements (n=4); patients declining (n=7), medical trainees conducting the encounter (n=6),
  inconvenient workflow (n=4).
- EHR: "longer clinical notes, greater editing time, slightly more time spent documenting per encounter", but "a higher
  proportion of same-day encounter closure".

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All computed numbers, every draft and final note (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Specialty | `{{specialty}}` | `mixed` | `mixed` (all 6 encounters), `psychiatry`, `endocrinology`, `rheumatology` or `internal_medicine` |
| Your transcript | `{{your_transcript}}` | — | Paste a short, **de-identified or invented** encounter transcript (Dr:/Pt: lines). It is drafted and finalized with the chosen specialty's template (`internal_medicine` if `mixed`) |
| Encounters per month | `{{encounters_per_month}}` | `390` | Encounters per clinician per month. The default is implied by the paper's medians (11 scribe encounters ÷ 0.94% ≈ 1,170 per ~3 months), so treat it as rough |
| Patients declining | `{{patient_decline_rate}}` | `0.10` | Share of encounters where the patient declines the scribe (assumption) |
| Trainee-led encounters | `{{trainee_share}}` | `0.20` | Share of encounters conducted by trainees, who may not use the scribe (assumption) |
| Baseline note time | `{{baseline_doc_minutes}}` | `6` | Minutes to write the note yourself without the scribe (assumption) |
| Edit speed | `{{edit_sec_per_word}}` | `1.5` | Seconds per inserted or substituted word when editing a draft (≈ 40 wpm typing) |
| The promise | `{{promised_minutes_per_note}}` | `5` | Illustrative "minutes saved per note" claim for the promise scenario (not from the paper) |
| Seed | `{{seed}}` | `8` | Random seed for the implementation Monte Carlo |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). LLM access goes through the embedded `llm.py`, which uses
whichever key the sandbox provides (OpenRouter, Anthropic or OpenAI). No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
python -c "import os; ks=[k for k in ('OPENROUTER_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY') if os.environ.get(k)]; print('LLM keys present:', ks or 'NONE')"
```

If no key is present, stop and report that an LLM key is required. Never print key values.

Write `/app/work/params.json`. If a value is blank or still looks like an unsubstituted `{{…}}` placeholder, use the
table default (`""` for the transcript). Clamp `encounters_per_month` to [20, 1000], `patient_decline_rate` and
`trainee_share` to [0, 0.9], `baseline_doc_minutes` to [1, 30], `edit_sec_per_word` to [0.3, 10], and
`promised_minutes_per_note` to [0, 30]. An unknown `specialty` becomes `mixed`. Record any clamp or substitution as
a caveat. If the transcript looks like it contains real identifiers (full names with health card numbers, dates of
birth, addresses), do not run it: blank it and say why in a caveat.

```json
{"specialty": "{{specialty}}", "your_transcript": "{{your_transcript}}", "encounters_per_month": {{encounters_per_month}},
 "patient_decline_rate": {{patient_decline_rate}}, "trainee_share": {{trainee_share}},
 "baseline_doc_minutes": {{baseline_doc_minutes}}, "edit_sec_per_word": {{edit_sec_per_word}},
 "promised_minutes_per_note": {{promised_minutes_per_note}}, "seed": {{seed}}, "runbook_url": ""}
```

## Step 2: Get the code (extract it, don't retype it)

The tested implementation is embedded in the **Appendix** at the end of this runbook. Do not rewrite, "improve" or
re-derive it. **Always run the command below first, exactly as written.** It copies the files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it won't work: run it and read its output:

```bash
cd /app/work && cat > extract.py <<'PYEOF'
"""Extract the runbook's embedded files without retyping them.

The runbook text reaches the agent as one command-line argument, so it is readable from /proc.
Every embedded file sits under a heading "### `/app/work/<name>`" followed by one fenced block.
Exits non-zero if any requested file can't be found, so the caller falls back to writing it by hand.

usage: python3 extract.py <name> [<name> ...]   (writes /app/work/<name>)
"""
import ast, glob, re, sys
from pathlib import Path

want = sys.argv[1:]
cands = []
for p in glob.glob("/proc/[0-9]*/cmdline"):
    try:
        s = Path(p).read_bytes().decode("utf-8", "ignore")
    except OSError:
        continue
    if all(f"### `/app/work/{w}`" in s for w in want):
        cands.append(s)
if not cands:
    sys.exit("runbook text not found in /proc; write the files by hand")
# The agent's own argv holds the raw text; wrapper shells hold a shell-quoted copy, so prefer the shortest
# and undo shell single-quote escaping as a fallback.
best = min(cands, key=len).replace("'\"'\"'", "'")
ok = True
for w in want:
    m = re.search(r"### `/app/work/" + re.escape(w) + r"`\s*\n+```[a-z]*\n(.*?)\n```\n", best, re.S)
    if not m or len(m.group(1)) < 50:
        print(f"MISSING {w}"); ok = False; continue
    code = m.group(1) + "\n"
    if w.endswith(".py"):
        try:
            ast.parse(code)
        except SyntaxError as e:
            print(f"MISSING {w} (extracted text does not parse: {e})"); ok = False; continue
    Path("/app/work", w).write_text(code)
    print(f"extracted {w}: {code.count(chr(10))} lines")
sys.exit(0 if ok else 1)
PYEOF
python3 extract.py experiment.py render_card.py validate.py llm.py
```

If it exits non-zero or prints `MISSING`, write each missing file from the Appendix **exactly as given**, one heredoc
per file (quoted delimiter, e.g. `cat > experiment.py <<'PYEOF'`). If a later step fails, fix only environment
problems (missing package, network retry), never the methodology, the prompts or the transcripts.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && SMASH_LLM_CACHE=/app/work/llm_cache.json timeout 300 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: 30–70 s. It ends with a `done:` line giving edit rates, net minutes per note, and promised vs pilot-reality
hours. On a network or rate-limit error, rerun the same command once (finished calls are cached).

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Skim at least one generic draft
and its final note in `notes[]`. Write `{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3),
`findings` (2–4), `try_next` (2–3), `caveats` (2–4):

- **headline** (≤ 30 words): the gap between promise and reality, with 1–2 numbers from `results.json`. Typically
  `promise_hours` vs `reality_hours`, or the edit burden (`edit_rate_generic` as a %). If `net_minutes_generic` is
  negative, lead with the scribe *adding* time.
- **idea**: (1) ambient scribes promise less documentation burden; (2) the paper's interim evaluation (NASSS-guided,
  mixed methods) found heterogeneous adoption (21 of 43, median 0.94% of encounters), frequent editing (88%) and no
  measured time reduction; (3) its lesson: value depends on workflow integration and specialty customization, not
  availability.
- **findings**: (1) edit burden generic vs customized, with what the edits were (`error_types`; format and omission
  usually dominate), against the paper's 88% and its specialty-mismatch barrier; (2) net minutes per note and
  `share_notes_saving_time_*` against the paper's 41% / 29%. State plainly that minutes come from the stated
  assumptions. (3) The ladder: pilot reality (`reality_hours`, 90% interval `reality_mc`) vs `promise_hours`, which
  lever moves it most, and `full_adoption_hours`. Note that adoption, not note quality, dominates the gap.
  (4) Optionally: `barrier_points` of the unused encounters are explained by the listed barriers you assumed;
  the rest (`unexplained_points`) were clinician choice or workflow.
- **try_next**: 2–3 runs with exact values using only `specialty, your_transcript, encounters_per_month,
  patient_decline_rate, trainee_share, baseline_doc_minutes, edit_sec_per_word, promised_minutes_per_note, seed`.
  Good contrasts: a fast note-writer (`baseline_doc_minutes` 3, `edit_sec_per_word` 2.5), which usually turns savings
  negative as in the paper's EHR data; `specialty` `psychiatry`, where the paper says customization mattered most;
  an academic clinic with more trainees (`trainee_share` 0.5).
- **caveats**: synthetic transcripts with an LLM scribe and an LLM "specialist" (not Dragon Copilot, not real
  clinicians, and the two share a model family, which may understate disagreement); PDQI-style scores come from an
  LLM judge, not the paper's planned content analysis; minutes and hours come from this runbook's assumptions; the
  paper's survey percentages are perceptions of 17 respondents and are not directly comparable.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, edit rates, net minutes, ladder hours, headline).

## Writing style for narrative.json

These rules apply to every field and override any longer limits stated earlier in this runbook. Let the paper
and the numbers speak; the card is not the place for commentary.

- **Length:** `headline` one sentence; `idea` 1–3 bullets of at most 30 words; `findings` 1–2 paragraphs of at
  most 60 words each; `caveats` 1–2 bullets of at most 20 words. Cut anything the tiles, figures or tables
  already show.
- **Plain statements of what was measured.** Write "Sensitivity gap −0.284 [−0.354, −0.218]; the paper reports
  +0.088", not an interpretation of what it means for the field.
- **Avoid:** em-dash asides; "not X, but Y" framings; colon-then-reveal sentences; rhetorical questions; words
  such as *crucially, notably, strikingly, remarkably, collapses, illustrating, underscores, highlights, delve,
  powerful, key insight, worth noting*; exclamation marks; restating the method before the result.
- Use the paper's own terms for its concepts. Quote the paper's numbers exactly.

## Code Checks

Jetty runs these checks itself in the sandbox after the agent finishes, so they cannot be skipped or
misreported. `validate.py` (see Write Validation Report) runs the same checks first so you can fix problems before you stop.

### outputs-exist — Result card, numbers, narrative and summary were written

```bash
cd {{results_dir}} && for f in result_card.html results.json card_data.json narrative.json summary.md; do test -s "$f" || { echo "missing or empty: $f"; exit 1; }; done; echo "all 5 outputs present"
```

### results-valid — Experiment numbers are valid JSON and the experiment stayed within its time budget

```bash
python3 - "{{results_dir}}" 300 <<'PY'
import json, sys
from pathlib import Path
R, budget = Path(sys.argv[1]), float(sys.argv[2])
res = json.loads((R / "results.json").read_text())
json.loads((R / "card_data.json").read_text())
rt = float(res.get("runtime_sec", 0))
if rt > budget:
    sys.exit(f"experiment took {rt}s, budget {budget}s")
print(f"results.json and card_data.json parse; experiment {rt}s within {budget:.0f}s")
PY
```

### narrative-complete — The narrative is complete and within the length limits

```bash
python3 - "{{results_dir}}" <<'PY'
import json, sys
from pathlib import Path
n = json.loads((Path(sys.argv[1]) / "narrative.json").read_text())
problems = []
if not str(n.get("headline", "")).strip(): problems.append("no headline")
if len(str(n.get("headline", "")).split()) > 45: problems.append("headline over 45 words")
if not 1 <= len(n.get("idea", [])) <= 3: problems.append(f"idea has {len(n.get('idea', []))} bullets, need 1-3")
if not 1 <= len(n.get("findings", [])) <= 2: problems.append(f"{len(n.get('findings', []))} findings, need 1-2")
if any(len(f.split()) > 70 for f in n.get("findings", [])): problems.append("a findings paragraph is over 60 words")
if not 2 <= len(n.get("try_next", [])) <= 3: problems.append(f"{len(n.get('try_next', []))} try_next, need 2-3")
if not 1 <= len(n.get("caveats", [])) <= 2: problems.append(f"{len(n.get('caveats', []))} caveats, need 1-2")
if problems: sys.exit("; ".join(problems))
print("headline, %d idea bullets, %d findings, %d try_next, %d caveats" % (len(n["idea"]), len(n["findings"]), len(n["try_next"]), len(n["caveats"])))
PY
```

### try-next-valid — Every try-next suggestion uses only this runbook's parameters

```bash
python3 - "{{results_dir}}" "specialty,your_transcript,encounters_per_month,patient_decline_rate,trainee_share,baseline_doc_minutes,edit_sec_per_word,promised_minutes_per_note,seed" <<'PY'
import json, sys
from pathlib import Path
allowed = set(sys.argv[2].split(","))
n = json.loads((Path(sys.argv[1]) / "narrative.json").read_text())
bad = sorted({k for t in n.get("try_next", []) for k in (t.get("params") or {}) if k not in allowed})
empty = [t.get("label", "?") for t in n.get("try_next", []) if not t.get("params")]
if bad or empty: sys.exit(f"unknown parameters: {bad}; suggestions without params: {empty}")
print("all try_next parameters are declared runbook parameters")
PY
```

### headline-grounded — Every number in the headline appears in the run's results

```bash
python3 - "{{results_dir}}" <<'PY'
import json, re, sys
from pathlib import Path
R = Path(sys.argv[1])
blob = (R / "results.json").read_text() + (R / "card_data.json").read_text()
vals = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", blob)]
head = json.loads((R / "narrative.json").read_text())["headline"]
nums = re.findall(r"(?<![\w.−-])[−-]?\d[\d,]*(?:\.\d+)?(?![\w-])", head)
missing = []
for n in nums:
    s = n.replace("−", "-").replace(",", ""); v = float(s); dec = len(s.split(".")[1]) if "." in s else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    if not any(abs(abs(x) - abs(v)) <= tol or abs(abs(x * 100) - abs(v)) <= max(tol, 0.5) for x in vals):
        missing.append(n)
if missing: sys.exit(f"headline numbers not found in results: {missing}")
print(f"{len(nums)} headline number(s) all grounded in results")
PY
```

### card-integrity — The card embeds its figures, shows the headline, and contains no NaN

```bash
python3 - "{{results_dir}}" <<'PY'
import html, json, re, sys
from pathlib import Path
R = Path(sys.argv[1])
card = (R / "result_card.html").read_text()
text = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", card)
head = json.loads((R / "narrative.json").read_text())["headline"]
problems = []
if card.count("data:image/png;base64") < 1: problems.append("no embedded figures")
if re.search(r"\bNaN\b|\bnan%|\bInfinity\b", text): problems.append("NaN/Infinity in card text")
if len(card) > 5_000_000: problems.append(f"card is {len(card) // 1024} KB")
plain = html.unescape(re.sub(r"<[^>]+>", "", text))
if re.sub(r"[*`]", "", head)[:40] not in plain: problems.append("headline not on card")
if problems: sys.exit("; ".join(problems))
print(f"card {len(card) // 1024} KB, {card.count('data:image/png;base64')} figures, headline present")
PY
```

## Checklist

- [ ] The headline states this run's finding with its numbers, not a description of the method
- [ ] Paper numbers are quoted exactly and any disagreement with the paper is stated plainly
- [ ] Caveats say what is synthetic, reconstructed or an extension of the paper
- [ ] Each try-next suggestion would plausibly give a contrasting result

## Write Validation Report

Judge the four Checklist items honestly against your outputs and write them to `/app/work/checklist.json` as a
list, using the checklist ids Jetty gives you (one entry per item):

```json
[{"id": "<checklist id>", "status": "pass", "message": "one line on why"}]
```

Then write the report and self-check in one command:

```bash
cd /app/work && python3 validate.py {{results_dir}} specialty,your_transcript,encounters_per_month,patient_decline_rate,trainee_share,baseline_doc_minutes,edit_sec_per_word,promised_minutes_per_note,seed 300 checklist.json
```

`validate.py` writes `{{results_dir}}/validation_report.json` in the v2 shape Jetty reads (`version: 2`, one
`step` entry per runbook step, one `code_check` entry per check above, one `checklist` entry per item). Jetty
replaces the `code_check` entries with its own independent run of the same checks. Do not write the report by hand.

## Iteration (up to 2 rounds)

If `validate.py` prints any `FAIL`, fix the named problem (usually a headline number that does not match
`results.json`, or an unknown `try_next` key), re-render the card (Step 5) and rerun the command above. Never
rerun the experiment just to change the narrative.

## Appendix: code

These files are extracted verbatim in Step 2.

### `/app/work/experiment.py`

```python
"""Scribe reality check — SMASH 2026 paper #8 (Mehta, Ha, Gordon, Balaci, Bhattacharya, Mukerji; Women's College Hospital).

The paper's finding: an EHR-integrated ambient AI scribe was feasible in hospital specialty clinics, but adoption was
heterogeneous (21 of 43 enrolled used it; median 0.94% of their encounters), 88% of survey respondents said notes
required frequent editing, and EHR data showed longer notes and more editing time. Implementation reality != the promise.

This run has two linked parts:
  A. Edit-burden lab (LLM). Synthetic specialty encounter transcripts -> an ambient-scribe draft (generic SOAP, or
     customized to the specialty's template) -> a simulated specialist makes the minimum edits needed to sign it ->
     word-level edit burden, planted-fact recall (rules), and a PDQI-9-style rubric + error list (LLM judge).
  B. Implementation model (no LLM). The paper's adoption funnel (140 eligible -> 43 enrolled -> 21 active, usage share
     lognormal fitted to median 0.94% / IQR 3.04%), the participant's clinic assumptions (patient declines, trainee-led
     encounters, documentation time) and the per-note minutes measured in part A -> clinician-hours saved per month,
     versus a "promise" scenario and a ladder of implementation levers.

usage: python experiment.py params.json outdir
"""
import concurrent.futures as cf, difflib, json, math, re, sys, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from llm import chat, chat_many, save_cache, parse_json, backend, model_name

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(int(P.get("seed", 8)))


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


# ------------------------------------------------------------------ specialty documentation styles
STYLES = {
    "psychiatry": "Psychiatry follow-up note in narrative prose (no SOAP headings). Sections: Identification and reason for visit; "
                  "Interval history; Mental status examination (appearance, behaviour, speech, mood in the patient's own words, "
                  "affect, thought process, thought content including suicidal and homicidal ideation, perception, insight, "
                  "judgment); Risk assessment (static and dynamic factors, protective factors, overall risk level); "
                  "Formulation (2-3 sentences); Plan (medications with exact doses, psychotherapy, safety plan, follow-up).",
    "endocrinology": "Consult letter back to the referring physician. Open with 'Dear Dr <referrer>, I saw <patient> in follow-up "
                     "for ...'. Sections: Diabetes summary (type, duration, complications); Current regimen with exact doses; "
                     "Glycemic data (A1c, CGM time in range, hypoglycemia); Assessment; Recommendations as a numbered list "
                     "addressed to the referring physician; Follow-up. Brief and letter-like.",
    "rheumatology": "Rheumatology clinic letter. Sections: Diagnoses (list); Current DMARDs and doses; Disease activity "
                    "(tender and swollen joint counts, patient global, CDAI if available); Relevant labs; Impression; Plan as a "
                    "numbered list including monitoring bloodwork and vaccination; Follow-up interval.",
    "internal_medicine": "Problem-oriented general internal medicine clinic note: one-line summary, then Assessment and Plan by "
                         "numbered problem (#1, #2, ...) each with status and specific actions; medication reconciliation list; "
                         "follow-up. Concise.",
}

# ------------------------------------------------------------------ synthetic encounters (fictional patients)
ENCOUNTERS = [
    {"id": "PSY-1", "specialty": "psychiatry", "facts": [r"sertraline", r"150\s*mg", r"suicid", r"sleep", r"(4|four) weeks"],
     "transcript": """Dr: Hi Ms. Alvarez, good to see you. How have the last six weeks been since we increased the sertraline?
Pt: Better, I think. I'm at the 100 milligrams. Mornings are still hard but I'm getting to work most days.
Dr: Most days - how many did you miss?
Pt: Two days last week. I just couldn't get out of bed.
Dr: How's your sleep?
Pt: I fall asleep okay but I'm up at 4 a.m. every night and can't get back to sleep.
Dr: And your mood, if you rated it out of ten?
Pt: Maybe a four. It was a two when I first came.
Dr: Any thoughts that life isn't worth living, or of hurting yourself?
Pt: Sometimes I think it would be easier not to wake up, but I'd never do anything. My kids.
Dr: Thank you for telling me. Any plan or anything you've done to prepare?
Pt: No, nothing like that.
Dr: Drinking or other substances?
Pt: A glass of wine on weekends.
Dr: Side effects from the sertraline? Stomach, sexual side effects?
Pt: A bit of nausea the first week, that's gone.
Dr: Okay. I'd like to go up to 150 milligrams, keep seeing your therapist weekly, and let's review your safety plan - you still have the crisis line number?
Pt: Yes, it's on my fridge.
Dr: Good. I'll see you in four weeks, sooner if things get worse."""},
    {"id": "PSY-2", "specialty": "psychiatry", "facts": [r"quetiapine", r"lithium", r"0\.8", r"manic|mania|hypomani", r"(2|two) weeks"],
     "transcript": """Dr: Mr. Chen, you came in today because your wife was worried. Tell me what's been happening.
Pt: I've been fine. Better than fine. I've got three new business ideas and I'm finally getting things done.
Dr: How much are you sleeping?
Pt: Three hours, maybe. I don't need more.
Dr: Your wife mentioned you spent a lot of money this month.
Pt: Investments. Eight thousand dollars on equipment. It'll pay off.
Dr: Are you taking the lithium every day?
Pt: I stopped about a month ago. It made me feel flat.
Dr: Your last level in March was 0.8, which was in range. Any thoughts of harming yourself or anyone else?
Pt: No, nothing like that. I'm happy.
Dr: Are you hearing or seeing things others don't?
Pt: No.
Dr: I'm concerned this is a manic episode, given the sleep, the spending, and stopping lithium. I'd like to restart lithium at your previous dose, 900 milligrams at bedtime, and add quetiapine 100 milligrams at night to help with sleep. We'll check a lithium level and kidney function in five days.
Pt: Fine, if it helps you relax.
Dr: Can your wife hold onto the credit cards for now?
Pt: I suppose.
Dr: I'll see you in two weeks, and the crisis team number is on your sheet."""},
    {"id": "END-1", "specialty": "endocrinology", "facts": [r"8\.4", r"glargine", r"(22|twenty[- ]two)\s*units", r"time in range|TIR", r"Dr\.? Okafor"],
     "transcript": """Dr: Hello Mr. Singh. Dr. Okafor sent you back to us about your sugars. How has it been?
Pt: Up and down. My sensor shows a lot of highs after dinner.
Dr: Your A1c came back at 8.4, up from 7.6 in the spring. Your sensor time in range is 52 percent, and I see very few lows, under one percent.
Pt: I've been eating later because of night shifts.
Dr: You're on metformin 1000 twice a day, and glargine 18 units at bedtime?
Pt: Yes. And the semaglutide, 0.5 weekly.
Dr: Any trouble with the semaglutide - nausea?
Pt: No, it's fine.
Dr: Any numbness in your feet, eye exam this year?
Pt: Eye exam was in January, it was okay. No numbness.
Dr: Okay. I'd suggest increasing the glargine to 22 units, and increasing semaglutide to 1 milligram weekly. I'll write to Dr. Okafor with these changes. Please do your bloodwork - A1c and kidney function - in three months.
Pt: And the night shifts?
Dr: Take the glargine at the same time each day, even on shift days. We'll see you in three months."""},
    {"id": "END-2", "specialty": "endocrinology", "facts": [r"TSH", r"0\.0[0-9]|suppress", r"methimazole", r"(10|ten)\s*mg", r"Graves"],
     "transcript": """Dr: Hi Ms. Patel, Dr. Brennan referred you for the overactive thyroid. How are you feeling?
Pt: Shaky, my heart races, and I've lost about five kilos without trying.
Dr: Your TSH is suppressed, under 0.01, and free T4 is 38, which is high. Your TSH receptor antibodies are positive, so this looks like Graves disease.
Pt: Is that serious?
Dr: It's very treatable. Any eye symptoms - grittiness, double vision, bulging?
Pt: My eyes feel gritty sometimes.
Dr: Your heart rate today is 112. I'd like to start methimazole 10 milligrams once daily and propranolol 10 milligrams up to three times a day for the racing heart. Methimazole can rarely lower white blood cells, so if you get a fever or sore throat, stop it and get a blood count the same day.
Pt: Okay. Should I worry about pregnancy?
Dr: Are you planning a pregnancy?
Pt: Not in the next year.
Dr: Then methimazole is the right choice, but tell us right away if that changes. We'll repeat thyroid tests in six weeks, and I'll send a letter to Dr. Brennan."""},
    {"id": "RHE-1", "specialty": "rheumatology", "facts": [r"methotrexate", r"(20|twenty)\s*mg", r"folic", r"swollen", r"CDAI|disease activity"],
     "transcript": """Dr: Mrs. Dubois, how are the hands since we started methotrexate?
Pt: The mornings are better - stiffness is about an hour now instead of three. But the right wrist still swells.
Dr: Let me examine. I count four tender joints and three swollen - the right wrist and two knuckles on the right hand. How would you rate your overall arthritis, zero to ten?
Pt: About five.
Dr: I'd rate it a four. That puts your clinical disease activity index around 16, which is moderate. You're on methotrexate 15 milligrams weekly by mouth and folic acid 5 milligrams weekly?
Pt: Yes, on Fridays.
Dr: Any mouth sores, nausea, or cough?
Pt: A bit of nausea the day after.
Dr: Your liver tests and blood counts last month were normal. I'd like to increase methotrexate to 20 milligrams weekly, and switch to the injection, which often helps the nausea. Keep the folic acid. We'll check bloodwork in four weeks, then every three months.
Pt: Can I still get my flu shot?
Dr: Yes, please do, and the shingles vaccine too. If you're not at low disease activity in three months, we'll talk about adding a second medication. See you in three months."""},
    {"id": "GIM-1", "specialty": "internal_medicine", "facts": [r"amlodipine", r"(5|five)\s*mg", r"152|blood pressure", r"ferritin|iron", r"colonoscopy"],
     "transcript": """Dr: Mr. Osei, we've got a few things to go over. First, your blood pressure today is 152 over 94.
Pt: It's always high here. At home it's about 140.
Dr: Still above target. You're on ramipril 10 milligrams. I'd like to add amlodipine 5 milligrams daily. It can cause ankle swelling, let me know if that happens.
Pt: Okay.
Dr: Second, your blood work shows you're anemic - hemoglobin 108 - and your ferritin is low at 9, so you're low on iron.
Pt: I've been more tired.
Dr: Any black stools, blood in the stool, or heartburn?
Pt: No blood. Sometimes heartburn.
Dr: At 61, with iron deficiency, we need to look for slow bleeding in the gut. I'm referring you for a colonoscopy and a gastroscopy. In the meantime, start ferrous sulfate 300 milligrams every other day.
Pt: Is it cancer?
Dr: Most often it's something less serious, like an ulcer, but it's important to check.
Pt: And my knee?
Dr: For the knee arthritis, keep using the topical diclofenac and the exercises - avoid ibuprofen tablets with your stomach symptoms. We'll recheck your blood pressure and hemoglobin in six weeks."""},
]

# Each clinician also has a personal style the scribe was never told about (paper: limited learning of "personal style").
PERSONAL = {
    "PSY-1": "You write in the first person ('I saw...'), keep the mental status exam to one compact line, and always state the overall risk as LOW, MODERATE or HIGH in capitals.",
    "PSY-2": "You never use bullet points, and you record what family members reported under a separate 'Collateral' heading.",
    "END-1": "You put the numbered recommendations immediately after the greeting, before any history, and keep the whole letter under 200 words.",
    "END-2": "You always end with a 'Patient counselled on:' line listing the safety advice given, and you keep lab values in a single line.",
    "RHE-1": "You record joint counts as 'TJC x/28, SJC y/28' and use short bullet points throughout.",
    "GIM-1": "You write each problem on one line as '#n Problem - status: plan' where possible and end with a 'Med changes today:' list.",
}

# ------------------------------------------------------------------ inputs
spec = (P.get("specialty") or "mixed").strip().lower().replace(" ", "_")
if spec not in STYLES and spec != "mixed":
    spec = "mixed"
encs = [e for e in ENCOUNTERS if spec == "mixed" or e["specialty"] == spec]
byo = (P.get("your_transcript") or "").strip()
if byo:
    encs = encs[:5] + [{"id": "YOURS", "specialty": spec if spec in STYLES else "internal_medicine", "facts": [],
                        "transcript": byo[:6000]}]
log(f"{len(encs)} encounters ({spec}); backend {backend()}")

SCRIBE_SYS = "You are an ambient AI medical scribe. You draft the clinician's note from the encounter transcript. Output only the note."
GENERIC = "Write a clinical note in standard SOAP format (Subjective, Objective, Assessment, Plan) from this encounter transcript.\n\nTRANSCRIPT:\n{t}"
CUSTOM = ("Write the clinician's note from this encounter transcript using this specialty template exactly:\n{style}\n\n"
          "TRANSCRIPT:\n{t}")
CLIN_SYS = ("You are a {sp} specialist finalizing a draft note before you sign it. Your notes must follow this template: {style}\n"
            "{personal}"
            "Make the MINIMUM edits necessary: correct anything inaccurate versus the transcript, add clinically important "
            "missing information, delete anything not said or not appropriate for your note, and restructure to your "
            "template. Keep every acceptable sentence word for word. Output only the final signed note.")
CLIN = "TRANSCRIPT:\n{t}\n\nDRAFT NOTE TO FINALIZE:\n{d}"

ARMS = ["generic", "custom"]
jobs = [(e, a) for e in encs for a in ARMS]
drafts = chat_many([(GENERIC if a == "generic" else CUSTOM).format(t=e["transcript"], style=STYLES[e["specialty"]])
                    for e, a in jobs], system=SCRIBE_SYS, size="small", max_tokens=900, workers=8)
log(f"scribe drafted {len(drafts)} notes")
# the clinician's system prompt differs by encounter (specialty template + personal style); group calls by encounter
RETRIES = []


def finalize(i):
    e = jobs[i][0]; pers = PERSONAL.get(e["id"], "")
    sysm = CLIN_SYS.format(sp=e["specialty"].replace("_", " "), style=STYLES[e["specialty"]],
                           personal=f"Your personal style: {pers}\n" if pers else "")
    out = chat(CLIN.format(t=e["transcript"], d=drafts[i]), system=sysm, size="small", max_tokens=1000)
    if len(out.split()) < 0.5 * len(drafts[i].split()):   # a cut-off reply (seen occasionally): retry once
        RETRIES.append(i)
        out = chat(CLIN.format(t=e["transcript"], d=drafts[i]) + "\n\nReturn the complete final note.", system=sysm,
                   size="small", max_tokens=1200)
    return out


with cf.ThreadPoolExecutor(8) as ex:
    finals = list(ex.map(finalize, range(len(jobs))))
save_cache()
log("simulated specialists finalized every draft")

PDQI = ["accurate", "thorough", "useful", "organized", "comprehensible", "succinct", "synthesized", "internally_consistent"]
JUDGE_SYS = ("You grade AI-scribe draft notes using items adapted from the Physician Documentation Quality Instrument "
             "(PDQI-9). Return JSON only.")
JUDGE = ("Specialty: {sp}. Required template: {style}\n\nTRANSCRIPT:\n{t}\n\nAI DRAFT:\n{d}\n\nCLINICIAN'S FINAL NOTE:\n{f}\n\n"
         "Grade the AI DRAFT. Return {{\"scores\": {{" + ", ".join(f'"{k}": 1-5' for k in PDQI) + "}}, "
         "\"errors\": [{{\"type\": \"omission|inaccuracy|hallucination|format\", \"severity\": \"minor|major\", \"what\": \"<=12 words\"}}], "
         "\"substantial_editing_needed\": true/false}}. Count only errors in the draft judged against the transcript and the template.")
jouts = chat_many([JUDGE.format(sp=e["specialty"], style=STYLES[e["specialty"]], t=e["transcript"], d=drafts[i], f=finals[i])
                   for i, (e, a) in enumerate(jobs)], system=JUDGE_SYS, size="small", max_tokens=900, workers=8)
log("judge graded every draft")


# ------------------------------------------------------------------ edit burden
def words(s):
    return re.findall(r"[A-Za-z0-9.%/<>-]+", s.lower())


def edit_stats(draft, final):
    a, b = words(draft), words(final)
    ins = dele = sub = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "insert":
            ins += j2 - j1
        elif op == "delete":
            dele += i2 - i1
        elif op == "replace":
            sub += min(i2 - i1, j2 - j1); ins += max(0, (j2 - j1) - (i2 - i1)); dele += max(0, (i2 - i1) - (j2 - j1))
    return {"draft_words": len(a), "final_words": len(b), "inserted": ins, "deleted": dele, "substituted": sub,
            "edit_rate": (ins + dele + sub) / max(len(a), len(b), 1), "kept_share": 1 - (dele + sub) / max(len(a), 1)}


BASE_MIN = float(P.get("baseline_doc_minutes", 6)); EDIT_SEC = float(P.get("edit_sec_per_word", 1.5))
READ_WPM, OVERHEAD = 200.0, 0.5   # proofreading speed; consent + start/stop + transfer to the EHR (minutes)


def scribe_minutes(st):
    """Clinician time to finalize a scribe draft: read it, type insertions/substitutions, delete (cheap)."""
    return (st["draft_words"] / READ_WPM + (st["inserted"] + st["substituted"]) * EDIT_SEC / 60
            + st["deleted"] * 0.25 * EDIT_SEC / 60 + OVERHEAD)


notes = []
for i, (e, a) in enumerate(jobs):
    st = edit_stats(drafts[i], finals[i])
    try:
        jd = parse_json(jouts[i])
    except ValueError:
        jd = {}
    sc = {k: float(jd.get("scores", {}).get(k, np.nan)) for k in PDQI}
    errs = [x for x in jd.get("errors", []) if isinstance(x, dict)]
    recall = [bool(re.search(f, drafts[i], re.I)) for f in e["facts"]]
    mins = scribe_minutes(st)
    notes.append({"encounter": e["id"], "specialty": e["specialty"], "arm": a, **st, "pdqi": sc,
                  "pdqi_mean": float(np.nanmean(list(sc.values()))) if any(np.isfinite(list(sc.values()))) else None,
                  "errors": errs, "n_errors": len(errs), "n_major": sum(x.get("severity") == "major" for x in errs),
                  "substantial_editing": bool(jd.get("substantial_editing_needed")) if jd else None,
                  "fact_recall": (sum(recall) / len(recall)) if recall else None, "facts_missed": [f for f, r in zip(e["facts"], recall) if not r],
                  "scribe_minutes": mins, "net_minutes_saved": BASE_MIN - mins, "draft": drafts[i], "final": finals[i]})


def arm_summary(a):
    N = [n for n in notes if n["arm"] == a]
    rec = [n["fact_recall"] for n in N if n["fact_recall"] is not None]
    sub = [n["substantial_editing"] for n in N if n["substantial_editing"] is not None]
    return {"n": len(N), "edit_rate": float(np.mean([n["edit_rate"] for n in N])),
            "draft_words": float(np.mean([n["draft_words"] for n in N])), "final_words": float(np.mean([n["final_words"] for n in N])),
            "kept_share": float(np.mean([n["kept_share"] for n in N])),
            "pdqi_mean": float(np.nanmean([n["pdqi_mean"] for n in N if n["pdqi_mean"] is not None])),
            "errors_per_note": float(np.mean([n["n_errors"] for n in N])), "major_per_note": float(np.mean([n["n_major"] for n in N])),
            "substantial_share": float(np.mean(sub)) if sub else None, "fact_recall": float(np.mean(rec)) if rec else None,
            "scribe_minutes": float(np.mean([n["scribe_minutes"] for n in N])),
            "net_minutes": float(np.mean([n["net_minutes_saved"] for n in N])),
            "share_saving_time": float(np.mean([n["net_minutes_saved"] > 0 for n in N]))}


lab = {a: arm_summary(a) for a in ARMS}
err_types = {a: {t: sum(1 for n in notes if n["arm"] == a for x in n["errors"] if x.get("type") == t)
                 for t in ["omission", "inaccuracy", "hallucination", "format"]} for a in ARMS}
log(f"edit rate generic {lab['generic']['edit_rate']:.2f} / custom {lab['custom']['edit_rate']:.2f}; "
    f"net min/note {lab['generic']['net_minutes']:.1f} / {lab['custom']['net_minutes']:.1f}")

# ------------------------------------------------------------------ B. implementation model calibrated to the paper
N_ELIG = 140; P_ENROLL = 43 / 140; P_ACTIVE = 21 / 43               # paper: 140 eligible, 43 enrolled, 21 used it
MED_SHARE, IQR_SHARE, MAX_SHARE = 0.0094, 0.0304, 0.184              # paper: median 0.94%, IQR 3.04%, max 18.4%
SIGMA = math.asinh(IQR_SHARE / (2 * MED_SHARE)) / 0.6745              # lognormal with that median and IQR
ENC = float(P.get("encounters_per_month", 390))
DECL = float(P.get("patient_decline_rate", 0.10)); TRAIN = float(P.get("trainee_share", 0.20))
PROMISE = float(P.get("promised_minutes_per_note", 5))
ELIG_FRAC = (1 - DECL) * (1 - TRAIN)
NSIM = 4000
shares = np.minimum(np.exp(np.log(MED_SHARE) + SIGMA * rng.standard_normal(200000)), MAX_SHARE)
E_SHARE = float(shares.mean())


def expected_hours(n_users, share, net_min):
    return n_users * ENC * share * net_min / 60


net_g, net_c = lab["generic"]["net_minutes"], lab["custom"]["net_minutes"]
ladder = [
    ("The promise", N_ELIG * ENC * PROMISE / 60, f"all {N_ELIG} clinicians, every encounter, {PROMISE:g} min saved"),
    ("Pilot reality (generic notes)", expected_hours(N_ELIG * P_ENROLL * P_ACTIVE, E_SHARE, net_g), "paper's adoption funnel x lab minutes"),
    ("+ specialty customization", expected_hours(N_ELIG * P_ENROLL * P_ACTIVE, E_SHARE, net_c), "customized drafts"),
    ("+ consent & trainee workflows", expected_hours(N_ELIG * P_ENROLL * P_ACTIVE, min(E_SHARE / ELIG_FRAC, 1), net_c),
     "listed barriers removed"),
    ("+ every enrollee active", expected_hours(N_ELIG * P_ENROLL, min(E_SHARE / ELIG_FRAC, 1), net_c), "43 of 43 use it"),
    ("Full adoption, measured minutes", N_ELIG * ENC * ELIG_FRAC * net_c / 60, "everyone, every eligible encounter"),
]
# Monte Carlo of the pilot-reality scenario (who enrolls/activates, how much each uses it, which notes they get)
sim = np.empty(NSIM)
net_pool = np.array([n["net_minutes_saved"] for n in notes if n["arm"] == "generic"])
for s in range(NSIM):
    n_act = rng.binomial(rng.binomial(N_ELIG, P_ENROLL), P_ACTIVE)
    sh = np.minimum(np.exp(np.log(MED_SHARE) + SIGMA * rng.standard_normal(n_act)), MAX_SHARE)
    used = rng.poisson(ENC * sh)
    sim[s] = sum(rng.choice(net_pool, u).sum() for u in used) / 60 if n_act else 0.0
reality_lo, reality_med, reality_hi = (float(x) for x in np.percentile(sim, [5, 50, 95]))
used_share_all = E_SHARE * P_ENROLL * P_ACTIVE
barrier_points = 100 * (1 - ELIG_FRAC)
unexplained_points = 100 * (ELIG_FRAC - MED_SHARE)

# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#868e96"

ids = [e["id"] for e in encs]
fig, ax = plt.subplots(figsize=(6.4, 3.0))
x = np.arange(len(ids)); w = 0.38
for k, (a, col) in enumerate([("generic", ACC), ("custom", BLUE)]):
    v = [next(n["edit_rate"] for n in notes if n["encounter"] == i and n["arm"] == a) for i in ids]
    ax.bar(x + (k - 0.5) * w, v, w, color=col, label={"generic": "generic SOAP draft", "custom": "specialty-customized draft"}[a])
    for xi, vi in zip(x, v):
        ax.text(xi + (k - 0.5) * w, vi + 0.02, f"{100 * vi:.0f}%", ha="center", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(ids, fontsize=8.5); ax.set_ylabel("edit burden\n(word edits / longer of draft, final)")
ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.13))
fig.tight_layout(); fig.savefig(OUT / "fig_edit_burden.png", dpi=160); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.1), gridspec_kw={"width_ratios": [1.5, 1]})
ax = axs[0]; y = np.arange(len(PDQI))
for k, (a, col) in enumerate([("generic", ACC), ("custom", BLUE)]):
    v = [np.nanmean([n["pdqi"][q] for n in notes if n["arm"] == a]) for q in PDQI]
    ax.barh(y + (k - 0.5) * 0.38, v, 0.38, color=col)
ax.set_yticks(y); ax.set_yticklabels([q.replace("_", " ") for q in PDQI], fontsize=8); ax.invert_yaxis()
ax.set_xlim(1, 5); ax.set_xlabel("PDQI-style score (1-5)", fontsize=8.5)
ax = axs[1]; types = ["omission", "inaccuracy", "hallucination", "format"]; y = np.arange(len(types))
for k, (a, col) in enumerate([("generic", ACC), ("custom", BLUE)]):
    ax.barh(y + (k - 0.5) * 0.38, [err_types[a][t] / lab[a]["n"] for t in types], 0.38, color=col)
ax.set_yticks(y); ax.set_yticklabels(types, fontsize=8); ax.invert_yaxis(); ax.set_xlabel("errors per draft", fontsize=8.5)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=ACC, label="generic SOAP draft"), Patch(color=BLUE, label="specialty-customized draft")],
           frameon=False, fontsize=8, ncol=2, loc="upper center")
fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(OUT / "fig_quality.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.2))
lab_ = [l[0] for l in ladder]; val = [l[1] for l in ladder]
cols = [MUTED] + [ACC if v < 0 else BLUE for v in val[1:]]
ax.barh(range(len(ladder)), val, color=cols); ax.invert_yaxis()
ax.set_yticks(range(len(ladder))); ax.set_yticklabels(lab_, fontsize=8.5)
ax.set_xscale("symlog", linthresh=10); ax.axvline(0, color=INK, lw=0.8)
for i, v in enumerate(val):
    ax.text(v * 1.15 + 0.5 if v >= 0 else 0.6, i, f"{v:,.0f} h" if abs(v) >= 10 else f"{v:,.1f} h", va="center",
            ha="left", fontsize=8, color=INK if v >= 0 else ACC)
ax.set_xlabel("clinician-hours saved / month (symlog; < 0 = time added)")
ax.set_xlim(min(-30, min(val) * 3), max(val) * 6)
fig.tight_layout(); fig.savefig(OUT / "fig_hours_ladder.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.6))
stages = [("eligible clinicians", 140), ("enrolled", 43), ("used it at least once", 21)]
ax.barh(range(3), [s[1] for s in stages], color=[MUTED, BLUE, BLUE]); ax.invert_yaxis()
ax.set_yticks(range(3)); ax.set_yticklabels([s[0] for s in stages])
for i, s in enumerate(stages):
    ax.text(s[1] + 2, i, f"{s[1]}", va="center", fontsize=9)
ax.set_xlim(0, 175); ax.set_xlabel("clinicians (paper, interim analysis at ~3 months)")
ax.text(172, 2.35, f"among users: median 0.94% of encounters;\nyour barrier assumptions explain {barrier_points:.0f} of the\n"
        f"{100 - 100 * MED_SHARE:.0f} percentage points of unused encounters", ha="right", va="bottom", fontsize=7.8, color=INK)
fig.tight_layout(); fig.savefig(OUT / "fig_funnel.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ outputs
G, C = lab["generic"], lab["custom"]
res = {"params": P, "specialty": spec, "n_encounters": len(encs), "byo_transcript": bool(byo), "lab": lab, "error_types": err_types,
       "edit_rate_generic": G["edit_rate"], "edit_rate_custom": C["edit_rate"],
       "substantial_share_generic": G["substantial_share"], "substantial_share_custom": C["substantial_share"],
       "net_minutes_generic": net_g, "net_minutes_custom": net_c, "scribe_minutes_generic": G["scribe_minutes"],
       "share_notes_saving_time_generic": G["share_saving_time"], "share_notes_saving_time_custom": C["share_saving_time"],
       "fact_recall_generic": G["fact_recall"], "fact_recall_custom": C["fact_recall"],
       "assumptions": {"baseline_doc_minutes": BASE_MIN, "edit_sec_per_word": EDIT_SEC, "read_wpm": READ_WPM, "overhead_min": OVERHEAD,
                       "encounters_per_month": ENC, "patient_decline_rate": DECL, "trainee_share": TRAIN,
                       "promised_minutes_per_note": PROMISE},
       "usage_model": {"lognormal_sigma": SIGMA, "median_share": MED_SHARE, "mean_share_active": E_SHARE, "cap": MAX_SHARE},
       "ladder": [{"scenario": l[0], "hours_per_month": l[1], "how": l[2]} for l in ladder],
       "promise_hours": ladder[0][1], "reality_hours": ladder[1][1], "reality_mc": {"p5": reality_lo, "median": reality_med, "p95": reality_hi},
       "reality_pct_of_promise": 100 * ladder[1][1] / ladder[0][1], "full_adoption_hours": ladder[-1][1],
       "used_share_all_encounters": used_share_all, "barrier_points": barrier_points, "unexplained_points": unexplained_points,
       "llm_backend": backend(), "llm_model": model_name("small"), "llm_calls": 3 * len(jobs) + len(RETRIES), "specialist_retries": len(RETRIES), "notes": notes}

tiles = [
    {"label": "Edit burden of scribe drafts", "value": f"{100 * G['edit_rate']:.0f}% → {100 * C['edit_rate']:.0f}%",
     "sub": "words changed to sign the draft: generic → specialty-customized", "tone": "warn"},
    {"label": "Net minutes per note", "value": f"{net_g:+.1f} / {net_c:+.1f}",
     "sub": f"vs writing it yourself in {BASE_MIN:g} min (generic / customized)", "tone": "accent" if net_g < 0 else "neutral"},
    {"label": "Clinic hours saved / month", "value": f"{ladder[1][1]:,.1f} h",
     "sub": f"at the paper's adoption, vs {ladder[0][1]:,.0f} h promised", "tone": "warn"},
    {"label": "Drafts needing substantial edits", "value": f"{100 * (G['substantial_share'] or 0):.0f}%",
     "sub": "judge's call on generic drafts (paper survey: 88%)", "tone": "neutral"},
]
compare = [
    {"metric": "AI notes needing editing", "paper": "88% reported that generated notes required frequent editing (n=17 survey)",
     "yours": f"{100 * (G['substantial_share'] or 0):.0f}% generic / {100 * (C['substantial_share'] or 0):.0f}% customized drafts judged to need substantial edits",
     "note": "different construct: clinician perception vs LLM judge"},
    {"metric": "Mismatch with specialty documentation", "paper": "mismatch between output and specialty-specific documentation requirements (n=4)",
     "yours": f"format errors per draft {err_types['generic']['format'] / G['n']:.1f} generic vs {err_types['custom']['format'] / C['n']:.1f} customized", "note": ""},
    {"metric": "Inaccurate content", "paper": "inaccurate content information (n=4)",
     "yours": f"inaccuracy + hallucination errors per draft {(err_types['generic']['inaccuracy'] + err_types['generic']['hallucination']) / G['n']:.1f}; planted-fact recall {100 * (G['fact_recall'] or 0):.0f}%",
     "note": "synthetic transcripts"},
    {"metric": "Time savings", "paper": "41% felt they experienced overall time savings; 29% reported reduced documentation time",
     "yours": f"{100 * G['share_saving_time']:.0f}% of generic / {100 * C['share_saving_time']:.0f}% of customized notes faster than {BASE_MIN:g} min from scratch",
     "note": "modelled minutes, your assumptions"},
    {"metric": "Adoption", "paper": "43 enrolled; 21 (49%) used the AI scribe", "yours": "used as model input", "note": "calibration"},
    {"metric": "Utilization among users", "paper": "median 0.94% of encounters (IQR 3.04%), range 0.05-18.4%",
     "yours": f"lognormal σ = {SIGMA:.2f}; mean {100 * E_SHARE:.1f}% per active user", "note": "fitted, capped at 18.4%"},
    {"metric": "Documentation time (EHR)", "paper": "longer clinical notes, greater editing time, slightly more time spent documenting per encounter",
     "yours": f"drafts {G['draft_words']:.0f} words; finalizing a draft {G['scribe_minutes']:.1f} min vs {BASE_MIN:g} min assumed baseline", "note": ""},
]
Path(OUT / "card_data.json").write_text(json.dumps({
    "paper": {"num": 8, "title": "Implementing Ambient Artificial Intelligence Scribes in Hospital-based Specialty Care: A Mixed-Methods Evaluation on Administrative Burden and Clinical Workflows",
              "authors": "Nishila Mehta, Emily Ha, Andrew Gordon, Rodica Balaci, Onil Bhattacharya, Geetha Mukerji", "url": "https://drive.google.com/file/d/1I4e3YIe7SLrZE1yJefyni5q4t2k4JwKW/view?usp=sharing",
              "affiliation": "Women's College Hospital · University of Toronto"},
    "inputs": {"specialty": spec, "encounters": f"{len(encs)}{' (incl. yours)' if byo else ''} synthetic",
               "baseline note": f"{BASE_MIN:g} min", "edit speed": f"{EDIT_SEC:g} s/word", "encounters/month": f"{ENC:g}",
               "patients declining": f"{100 * DECL:.0f}%", "trainee-led": f"{100 * TRAIN:.0f}%", "promise": f"{PROMISE:g} min/note"},
    "tiles": tiles,
    "figures": [{"path": "fig_edit_burden.png", "title": "How much of the scribe's draft did the specialist have to change?",
                 "caption": "Word-level edits (insertions + deletions + substitutions) the simulated specialist made to sign each "
                            "draft, divided by the longer of draft and final note. Synthetic transcripts; LLM scribe and LLM specialist."},
                {"path": "fig_quality.png", "title": "What was wrong with the drafts?",
                 "caption": "Left: PDQI-9-style item scores (LLM judge). Right: errors per draft by type. Orange = generic SOAP, "
                            "blue = specialty-customized."},
                {"path": "fig_hours_ladder.png", "title": "Promise vs implementation reality",
                 "caption": "Clinician-hours saved per month across the clinic. 'Pilot reality' combines the paper's adoption "
                            "funnel and usage distribution with the minutes measured here; each rung removes one barrier."},
                {"path": "fig_funnel.png", "title": "Where the encounters went (paper's numbers)",
                 "caption": "Adoption funnel at the interim analysis. Even after the barriers you assumed, most eligible "
                            "encounters were simply not recorded with the scribe."}],
    "compare": compare, "runbook": {"name": "smash-08-scribe-reality-check", "url": P.get("runbook_url", "")}}, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: edit rate {G['edit_rate']:.2f}->{C['edit_rate']:.2f}; net min {net_g:+.1f}/{net_c:+.1f}; "
    f"hours/month promise {ladder[0][1]:,.0f} vs reality {ladder[1][1]:,.1f} (MC 90% {reality_lo:,.1f}..{reality_hi:,.1f}); "
    f"{res['llm_calls']} LLM calls")
```

### `/app/work/llm.py`

```python
"""Minimal, dependency-free LLM client for SMASH paper-playground runbooks.

Works with whatever keys the Jetty sandbox provides:
  1. OPENROUTER_API_KEY                                   -> OpenRouter
  2. ANTHROPIC_API_KEY with ANTHROPIC_BASE_URL on openrouter (Jetty trial keys) -> OpenRouter
  3. ANTHROPIC_API_KEY                                    -> Anthropic Messages API
  4. OPENAI_API_KEY                                       -> OpenAI
Set SMASH_LLM_MOCK=1 to return deterministic placeholders (offline testing).

    from llm import chat, chat_many, backend
    text = chat("Say hi", system="Be brief", size="small", max_tokens=50)
"""
import concurrent.futures as cf, hashlib, json, os, time, urllib.request
from pathlib import Path

MODELS = {  # size -> (openrouter slug, anthropic id, openai id)
    "small": ("anthropic/claude-haiku-4.5", "claude-haiku-4-5", "gpt-4.1-mini"),
    "large": ("anthropic/claude-sonnet-4.6", "claude-sonnet-4-6", "gpt-4.1"),
}
CACHE = Path(os.environ.get("SMASH_LLM_CACHE", "/app/work/llm_cache.json"))
_cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


def backend():
    if os.environ.get("SMASH_LLM_MOCK"):
        return "mock"
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"
    if os.environ.get("ANTHROPIC_API_KEY") and "openrouter" in os.environ.get("ANTHROPIC_BASE_URL", ""):
        return "openrouter-via-anthropic-key"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    raise RuntimeError("no LLM key found (OPENROUTER_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY)")


def model_name(size="small"):
    b = backend(); i = {"openrouter": 0, "openrouter-via-anthropic-key": 0, "anthropic": 1, "openai": 2}.get(b, 0)
    return MODELS[size][i]


def _post(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def chat(prompt, system="", size="small", max_tokens=800, temperature=0.0, timeout=90, retries=3):
    b = backend(); model = model_name(size)
    key = hashlib.sha256(json.dumps([b, model, system, prompt, max_tokens, temperature]).encode()).hexdigest()
    if key in _cache:
        return _cache[key]
    if b == "mock":
        out = f"[mock {size} reply {key[:8]}]"
    else:
        for attempt in range(retries):
            try:
                if b.startswith("openrouter"):
                    k = os.environ.get("OPENROUTER_API_KEY") or os.environ["ANTHROPIC_API_KEY"]
                    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
                    r = _post("https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {k}"},
                              {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature}, timeout)
                    out = r["choices"][0]["message"]["content"]
                elif b == "anthropic":
                    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
                    body = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
                            "messages": [{"role": "user", "content": prompt}]}
                    if system:
                        body["system"] = system
                    r = _post(f"{base}/v1/messages", {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                                      "anthropic-version": "2023-06-01"}, body, timeout)
                    out = "".join(c.get("text", "") for c in r["content"])
                else:
                    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
                    r = _post("https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                              {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature}, timeout)
                    out = r["choices"][0]["message"]["content"]
                break
            except Exception as e:  # network/rate-limit: back off and retry
                if attempt == retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
    _cache[key] = out
    return out


def chat_many(prompts, system="", size="small", max_tokens=800, temperature=0.0, workers=8):
    """Run many prompts concurrently; returns replies in order. Saves the cache afterwards."""
    with cf.ThreadPoolExecutor(workers) as ex:
        outs = list(ex.map(lambda p: chat(p, system, size, max_tokens, temperature), prompts))
    save_cache()
    return outs


def save_cache():
    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True); CACHE.write_text(json.dumps(_cache))
    except OSError:
        pass


def parse_json(text):
    """Pull the first JSON object/array out of a model reply."""
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1].rsplit("```", 1)[0]
    for o, c in (("{", "}"), ("[", "]")):
        i, j = s.find(o), s.rfind(c)
        if i != -1 and j > i:
            try:
                return json.loads(s[i:j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no JSON in reply: " + text[:200])
```

### `/app/work/render_card.py`

```python
"""Render a SMASH 2026 paper-playground result card (one self-contained HTML file).

usage: python render_card.py card_data.json narrative.json out.html

card_data.json  (written by the experiment script — numbers only)
  paper:   {num, title, authors, affiliation, url?}
  inputs:  {label: value}                         the participant's run settings
  tiles:   [{label, value, sub, tone}]            tone: accent|good|warn|neutral
  figures: [{path, title, caption}]               PNGs, embedded as base64
  compare: [{metric, paper, yours, note}]         paper-vs-your-run table (optional)
  runbook: {name, url}                            fork link (optional)
narrative.json  (written by the agent — words only)
  headline:  one sentence, the finding of THIS run
  idea:      [1-3 bullets] the paper's contribution in plain language
  abstract:  (optional) a verbatim abstract excerpt, shown instead of idea
  findings:  [2-4 short paragraphs] what this run shows, tied to the numbers
  try_next:  [{label, why, params}]               2-3 follow-up runs with exact parameter values
  caveats:   [bullets]
"""
import base64, html, json, sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
narr = json.loads(Path(sys.argv[2]).read_text())
base = Path(sys.argv[1]).parent
e = lambda s: html.escape(str(s))


def md_inline(s):
    """Escape, then allow **bold**, *italic* and `code` only."""
    import re
    s = e(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


p = data["paper"]
tiles = "".join(
    f'<div class="tile {e(t.get("tone", "neutral"))}"><div class="tl">{e(t["label"])}</div>'
    f'<div class="tv">{e(t["value"])}</div><div class="ts">{md_inline(t.get("sub", ""))}</div></div>'
    for t in data.get("tiles", []))
# Columns that fill every row: 4 tiles as 2x2, never 3 + 1 orphan.
n_tiles = len(data.get("tiles", []))
tile_cols = 2 if n_tiles == 4 else min(max(n_tiles, 1), 3)
inputs = "".join(f'<span class="chip"><b>{e(k)}</b> {e(v)}</span>' for k, v in data.get("inputs", {}).items())
figs = ""
for f in data.get("figures", []):
    fp = Path(f["path"]); fp = fp if fp.is_absolute() else base / fp
    if fp.exists():
        b64 = base64.b64encode(fp.read_bytes()).decode()
        figs += (f'<figure><figcaption class="ft">{e(f.get("title", ""))}</figcaption>'
                 f'<img alt="{e(f.get("title", ""))}" src="data:image/png;base64,{b64}">'
                 f'<figcaption>{md_inline(f.get("caption", ""))}</figcaption></figure>')
compare = ""
if data.get("compare"):
    rows = "".join(f'<tr><td>{md_inline(r["metric"])}</td><td>{md_inline(r["paper"])}</td>'
                   f'<td class="y">{md_inline(r["yours"])}</td><td class="n">{md_inline(r.get("note", ""))}</td></tr>'
                   for r in data["compare"])
    compare = (f'<section><h2>Paper vs. your run</h2><div class="tw"><table><thead><tr><th>Metric</th>'
               f'<th>Paper</th><th>Your run</th><th></th></tr></thead><tbody>{rows}</tbody></table></div></section>')
idea = "".join(f"<li>{md_inline(b)}</li>" for b in narr.get("idea", []))
abstract = narr.get("abstract", "")
findings = "".join(f"<p>{md_inline(x)}</p>" for x in narr.get("findings", []))
tries = "".join(
    f'<li><strong>{md_inline(t["label"])}</strong> — {md_inline(t.get("why", ""))}'
    f'<pre>{e(json.dumps(t.get("params", {}), ensure_ascii=False))}</pre></li>' for t in narr.get("try_next", []))
cav = "".join(f"<li>{md_inline(c)}</li>" for c in narr.get("caveats", []))
rb = data.get("runbook", {})
fork = (f'<a class="fork" href="{e(rb["url"])}">Fork this runbook on Jetty →</a>' if rb.get("url") else "")

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMASH 2026 · #{e(p['num'])} · Result card</title>
<style>
:root{{--bg:#f6f4ef;--card:#fff;--ink:#1f2a44;--muted:#5c677d;--line:#e3dfd5;--accent:#d9480f;--good:#2b8a3e;--warn:#e67700;--chip:#efece4}}
@media (prefers-color-scheme:dark){{:root{{--bg:#11151f;--card:#1a2030;--ink:#e8ebf2;--muted:#9aa4b8;--line:#2c3447;--accent:#ff8a4c;--good:#69db7c;--warn:#ffc078;--chip:#232b3d}}
figure img{{background:#fff;border-radius:6px}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:28px 16px 48px}}
.kicker{{font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
h1{{font-size:clamp(22px,4vw,30px);line-height:1.2;margin:10px 0 6px}}.authors{{color:var(--muted);margin:0 0 18px}}.authors a{{color:var(--accent);text-underline-offset:3px}}
.headline{{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:10px;padding:16px 18px;font-size:18px;font-weight:600;margin:0 0 18px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 18px}}.chip{{background:var(--chip);border-radius:999px;padding:4px 10px;font-size:12.5px}}.chip b{{font-weight:600;color:var(--muted);margin-right:4px}}
.tiles{{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:10px;margin:0 0 22px}}
@media (max-width:560px){{.tiles{{grid-template-columns:1fr}}}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}.tl{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.tv{{font-size:26px;font-weight:700;margin:2px 0;font-variant-numeric:tabular-nums}}.ts{{font-size:12.5px;color:var(--muted)}}
.tile.accent .tv{{color:var(--accent)}}.tile.good .tv{{color:var(--good)}}.tile.warn .tv{{color:var(--warn)}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 16px}}
h2{{font-size:16px;margin:0 0 10px}}ul{{padding-left:20px;margin:0}}li{{margin:4px 0}}p{{margin:0 0 10px}}
figure{{margin:0 0 18px}}figure img{{width:100%;height:auto;display:block}}figcaption{{font-size:13px;color:var(--muted);margin-top:6px}}.ft{{font-weight:600;color:var(--ink);font-size:14px;margin:0 0 6px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}}th,td{{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--muted);font-weight:600}}td.y{{font-weight:600}}td.n{{color:var(--muted);font-size:12.5px}}
pre{{background:var(--chip);border-radius:6px;padding:6px 8px;font-size:12px;white-space:pre-wrap;word-break:break-word;margin:4px 0 8px}}code{{background:var(--chip);border-radius:4px;padding:1px 4px;font-size:.92em}}
.fork{{display:inline-block;background:var(--ink);color:var(--bg);text-decoration:none;font-weight:600;border-radius:8px;padding:10px 14px;margin-top:6px}}
footer{{color:var(--muted);font-size:12.5px;margin-top:22px}}
.abs{{margin:0;padding-left:14px;border-left:3px solid var(--accent);color:var(--ink)}}
</style></head><body><main>
<div class="kicker">SMASH 2026 · Paper #{e(p['num'])} · Result card</div>
<h1>{e(p['title'])}</h1><p class="authors">{e(p['authors'])}{(' · ' + e(p['affiliation'])) if p.get('affiliation') else ''}{(f' · <a href="{e(p["url"])}">Read the paper</a>') if p.get('url') else ''}</p>
<div class="headline">{md_inline(narr['headline'])}</div>
<div class="chips">{inputs}</div>
<div class="tiles" style="--cols:{tile_cols}">{tiles}</div>
{f'<section><h2>From the abstract</h2><blockquote class="abs">{e(abstract)}</blockquote></section>' if abstract else f'<section><h2>The idea</h2><ul>{idea}</ul></section>'}
{f'<section><h2>What this run shows</h2>{findings}</section>' if findings else ''}
<section><h2>Evidence</h2>{figs}</section>
{compare}
<section><h2>Try next</h2><ul>{tries}</ul>{fork}</section>
<section><h2>Read this before sharing</h2><ul>{cav}</ul></section>
<footer>Generated by a Jetty runbook built from the authors' SMASH 2026 paper. Numbers on this card come from code run in a sandbox; the words were written by an AI agent reading those numbers. This is an interactive companion, not the authors' own results unless labelled “Paper”.</footer>
</main></body></html>"""
Path(sys.argv[3]).write_text(page)
print(f"wrote {sys.argv[3]} ({len(page) // 1024} KB)")
```

### `/app/work/validate.py`

```python
"""Self-check a SMASH paper-playground run and write validation_report.json (evals v2 shape).

Runs the same checks as the runbook's `## Code Checks` (which Jetty re-runs independently after the agent
exits and substitutes for these entries), adds one `step` entry per runbook step and the agent's checklist
judgements, and prints PASS/FAIL lines.

usage: python validate.py <results_dir> <param,param,...> <budget_sec> [checklist.json]
"""
import html, json, re, sys
from pathlib import Path

R = Path(sys.argv[1])
allowed = set(sys.argv[2].split(","))
budget = float(sys.argv[3])
checklist_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None


def load(name):
    try:
        return json.loads((R / name).read_text())
    except Exception:
        return None


res, cdata, narr = load("results.json"), load("card_data.json"), load("narrative.json")
card = (R / "result_card.html").read_text() if (R / "result_card.html").exists() else ""


def c_outputs_exist():
    missing = [f for f in ["result_card.html", "results.json", "card_data.json", "narrative.json", "summary.md"]
               if not (R / f).exists() or (R / f).stat().st_size == 0]
    return not missing, f"missing or empty: {missing}" if missing else "all 5 outputs present"


def c_results_valid():
    if res is None or cdata is None:
        return False, "results.json or card_data.json does not parse"
    rt = float(res.get("runtime_sec", 0))
    return rt <= budget, f"experiment {rt}s (budget {budget:.0f}s)"


def c_narrative_complete():
    if narr is None:
        return False, "narrative.json does not parse"
    p = []
    if not str(narr.get("headline", "")).strip(): p.append("no headline")
    if len(str(narr.get("headline", "")).split()) > 45: p.append("headline over 45 words")
    if not 1 <= len(narr.get("idea", [])) <= 3: p.append(f"idea has {len(narr.get('idea', []))} bullets, need 1-3")
    if not 1 <= len(narr.get("findings", [])) <= 2: p.append(f"{len(narr.get('findings', []))} findings, need 1-2")
    if any(len(f.split()) > 70 for f in narr.get("findings", [])): p.append("a findings paragraph is over 60 words")
    if not 2 <= len(narr.get("try_next", [])) <= 3: p.append(f"{len(narr.get('try_next', []))} try_next, need 2-3")
    if not 1 <= len(narr.get("caveats", [])) <= 2: p.append(f"{len(narr.get('caveats', []))} caveats, need 1-2")
    return not p, "; ".join(p) or "complete and within the length limits"


def c_try_next_valid():
    if narr is None:
        return False, "narrative.json does not parse"
    bad = sorted({k for t in narr.get("try_next", []) for k in (t.get("params") or {}) if k not in allowed})
    empty = [t.get("label", "?") for t in narr.get("try_next", []) if not t.get("params")]
    ok = not bad and not empty
    return ok, "all try_next parameters are declared" if ok else f"unknown parameters: {bad}; without params: {empty}"


def c_headline_grounded():
    if narr is None or res is None:
        return False, "missing narrative or results"
    blob = json.dumps(res) + json.dumps(cdata or {})
    vals = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", blob)]
    nums = re.findall(r"(?<![\w.−-])[−-]?\d[\d,]*(?:\.\d+)?(?![\w-])", narr.get("headline", ""))
    missing = []
    for n in nums:
        s = n.replace("−", "-").replace(",", ""); v = float(s); dec = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-dec) + 1e-9
        if not any(abs(abs(x) - abs(v)) <= tol or abs(abs(x * 100) - abs(v)) <= max(tol, 0.5) for x in vals):
            missing.append(n)
    return not missing, f"not found in results: {missing}" if missing else f"{len(nums)} headline number(s) grounded"


def c_card_integrity():
    if not card or narr is None:
        return False, "no card or narrative"
    text = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", card)
    plain = html.unescape(re.sub(r"<[^>]+>", "", text))
    p = []
    if card.count("data:image/png;base64") < 1: p.append("no embedded figures")
    if re.search(r"\bNaN\b|\bnan%|\bInfinity\b", text): p.append("NaN/Infinity in card text")
    if len(card) > 5_000_000: p.append(f"card is {len(card) // 1024} KB")
    if re.sub(r"[*`]", "", narr.get("headline", ""))[:40] not in plain: p.append("headline not on card")
    return not p, "; ".join(p) or f"card {len(card) // 1024} KB, {card.count('data:image/png;base64')} figures"


CODE_CHECKS = [  # ids and names match the runbook's ## Code Checks headings
    ("outputs-exist", "Result card, numbers, narrative and summary were written", c_outputs_exist),
    ("results-valid", "Experiment numbers are valid JSON and the experiment stayed within its time budget", c_results_valid),
    ("narrative-complete", "The narrative is complete and within the length limits", c_narrative_complete),
    ("try-next-valid", "Every try-next suggestion uses only this runbook's parameters", c_try_next_valid),
    ("headline-grounded", "Every number in the headline appears in the run's results", c_headline_grounded),
    ("card-integrity", "The card embeds its figures, shows the headline, and contains no NaN", c_card_integrity),
]
STEPS = [  # (id, name, evidence that the step happened)
    ("setup", "Set up the sandbox and parameters", Path("/app/work/params.json").exists() or res is not None),
    ("get-code", "Extract the tested code", Path("/app/work/experiment.py").exists() or res is not None),
    ("experiment", "Run the experiment", res is not None),
    ("interpret", "Write the narrative", narr is not None),
    ("render", "Render the result card and summary", bool(card) and (R / "summary.md").exists()),
]

checks = [{"kind": "step", "id": i, "name": n, "status": "pass" if ok else "fail"} for i, n, ok in STEPS]
for cid, name, fn in CODE_CHECKS:
    try:
        ok, msg = fn()
    except Exception as e:  # a check that crashes is an error, never a silent pass
        ok, msg = None, f"{type(e).__name__}: {e}"
    status = "pass" if ok else ("error" if ok is None else "fail")
    checks.append({"kind": "code_check", "id": cid, "name": name, "status": status, "message": str(msg)[:1000]})
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {msg}")

if checklist_path and checklist_path.exists():
    for item in json.loads(checklist_path.read_text()):
        st = item.get("status", "skipped")
        st = st if st in ("pass", "fail", "skipped", "error") else "skipped"
        checks.append({"kind": "checklist", "id": str(item["id"]), "name": str(item.get("name") or item["id"]),
                       "status": st, "message": str(item.get("message", ""))[:1000]})
        print(f"{'PASS' if st == 'pass' else 'FAIL'} checklist {item['id']}: {item.get('message', '')}")
else:
    print("NOTE no checklist.json given; checklist items will be recorded as not reported")

gating = [c for c in checks if c["kind"] != "step"]
verdict = "fail" if any(c["status"] in ("fail", "error") for c in gating) else ("pass" if gating else "unknown")
(R / "validation_report.json").write_text(json.dumps({"version": 2, "verdict": verdict, "checks": checks}, indent=2))
print(json.dumps({"verdict": verdict, "passed": sum(c["status"] == "pass" for c in gating), "gating_checks": len(gating)}))
```
