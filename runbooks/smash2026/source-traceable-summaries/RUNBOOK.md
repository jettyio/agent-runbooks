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
    skill_name: smash-18-source-traceable-summaries
    confidence: high
---

# The Judge Says 9/10, the Gate Says No: Release Gates for Patient Summaries (SMASH 2026 · Paper #18)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"From Extraction Accuracy to Clinical Usefulness: A Human-Centered Evaluation Framework for Source-Traceable Patient Summaries"** (Alissa Taylor).
Read the paper: https://drive.google.com/file/d/10P_qlRn02fwt-f2id3gu_oRUfPCTcpgr/view?usp=sharing

The paper's claim: extraction accuracy is necessary but not enough. A fact can be extracted correctly and still
mislead if it loses its temporal context, its status (active vs resolved), its negation, or its source. The paper
proposes layered evaluation: **Layer 1** deterministic checks that act as **high-sensitivity release gates** "for
failures that should never be averaged away by a favorable overall score"; **Layer 2** claim-level metrics; Layer 3
human task-based testing. Model-as-judge scores are at most a secondary regression signal. Evaluation uses synthetic
patient packs with **controlled noise** and provenance-aware gold labels.

The participant runs that pipeline on a small, fully synthetic patient pack (patient "SP-0187") with planted noise:
a discontinued medication, a resolved diagnosis, conflicting HbA1c values, a copied-forward medication list,
a letter whose document date differs from the event date, and a negated finding. An LLM writes a cited, structured
summary; the release gates and claim metrics run in code; an LLM judge gives the usual holistic 1–10 score. The run
repeats with other prompt styles and on a ladder of increasingly noisy packs, and asks: **how often would a judge
ship a summary that a deterministic gate blocks?** Participants can also paste their own synthetic notes.
Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment takes ~40 s (18 small LLM calls by default).

### Layer-1 gates implemented (paper's list, as deterministic code)
1 schema validity · 2 valid source identifiers and citation coverage for every claim · 3 preservation of negation ·
4 correct active / resolved / discontinued status · 5 medication start/stop boundaries and current dose (not a
copied-forward one) · 6 event date rather than document date · 7 contradiction surfaced with both sources cited
("provenance when claims are merged") · 8 required intended-use language. Layer 2: gold-claim recall,
governing-source citation, lexical support of each claim by its cited segment, severity-weighted errors.

### Paper statements to quote (the paper reports no numbers; quote exactly)
- "These checks act as high-sensitivity release gates for failures that should never be averaged away by a favorable overall score."
- "A gain in readability should not offset broken evidence links, a known status inversion, or loss of negation."
- "If a claim lacks an accessible source, the presence of other well-supported claims should not compensate for it."
- Model-as-judge scores "should not serve as the sole evidence of clinical acceptability because judge models may share blind spots with the system being evaluated."
- "Errors should be stratified by likely consequence rather than counted equally."

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All computed numbers, summaries, gate reasons (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Summarizer prompt | `{{summarizer_style}}` | `brief` | `brief` (concise, readable, cited), `careful` (explicit rules on status, dates, conflicts, negation, intended use) or `naive` (just "summarize") |
| Summarizer size | `{{summarizer_size}}` | `small` | `small` (Claude Haiku) or `large` (Claude Sonnet; slower and costlier) |
| Judge size | `{{judge_size}}` | `small` | Model used as the holistic 1–10 judge |
| Noise types | `{{noise_types}}` | `all` | `all`, `none`, or a comma list of `discontinued_med, resolved_dx, conflicting_labs, copied_forward, date_mismatch, negation` |
| Compare prompt styles | `{{compare_styles}}` | `true` | Also run the other two prompt styles on the same pack |
| Noise ladder | `{{degradation_ladder}}` | `true` | Also run your prompt on packs with 0, 1, …, 6 noise types (same clinical state) |
| Your notes | `{{custom_notes}}` | — | Paste **synthetic** notes instead (never real patient data): documents separated by lines `=== type \| YYYY-MM-DD`. Without gold labels only the gold-free gates run (schema, citations, negation, intended use) |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). No downloads; the patient pack is generated in code.
LLM access: `llm.py` (embedded) uses the sandbox's OpenRouter/Anthropic/OpenAI key.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json`. If a value still looks like an unsubstituted `{{…}}` placeholder use the table
default; use `""` for blank `custom_notes`. Convert the two switches to JSON booleans. Put `custom_notes` into a
JSON string with proper escaping (write the file with Python `json.dump` if the notes contain quotes or newlines).
If the pasted notes look like real patient data (real names, health-card numbers), do not run them: use the
default pack and say so in the caveats.

```json
{"summarizer_style": "{{summarizer_style}}", "summarizer_size": "{{summarizer_size}}", "judge_size": "{{judge_size}}",
 "noise_types": "{{noise_types}}", "compare_styles": {{compare_styles}}, "degradation_ladder": {{degradation_ladder}},
 "custom_notes": "{{custom_notes}}", "runbook_url": ""}
```

## Step 2: Get the code (extract it, don't retype it)

The tested implementation is embedded in the **Appendix** at the end of this runbook. Do not rewrite, "improve",
or re-derive it. **Always run the command below first, exactly as written.** It copies the files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it won't work: run it and read its output:

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
python3 extract.py experiment.py llm.py render_card.py validate.py
```

If it exits non-zero or prints `MISSING`, write each missing file from the Appendix **exactly as given**, one
heredoc per file (quoted delimiter, e.g. `cat > experiment.py <<'PYEOF'`). If a later step fails, fix only
environment problems (missing package, network retry), never the methodology.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 300 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: ~40 s, ending with a `done:` line (judge score, failed gates, how many variants a judge would ship but a
gate blocks). On an HTTP error run it once more; finished calls are cached in `/app/work/llm_cache.json`.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` (`main`, `style_runs`, `ladder`, `all_runs` with `gate_reasons`, `audit`,
`judge_rationale`) and `card_data.json`, and look at every `fig_*.png`. Write `{{results_dir}}/narrative.json` with
keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3), `caveats` (2–4):

- **headline** (≤ 30 words): the sharpest judge-vs-gate contrast of *this* run with 1–2 numbers from `results.json`,
  ideally from `judged_7plus_but_clinical_gate_failed` ("the judge gave 9/10; the contradiction gate blocked it:
  HbA1c conflict silently resolved"). If none exists, report the main run's judge score and gate result honestly.
- **idea**: (1) extraction accuracy is not clinical usefulness (time, status, negation, contradiction, source);
  (2) objectively testable properties become deterministic release gates that a good average score cannot offset;
  (3) evaluate on synthetic packs with controlled noise and provenance-aware gold labels, with judge scores secondary.
- **findings**: (1) the main summary: judge score vs gates, quoting the gate reasons and the claim-audit verdicts;
  (2) prompt styles: which style passes the gates and how the judge ranked them; (3) the noise ladder: which noise
  type first breaks a gate, and whether the judge score tracks it (check `judge_rationale`: the judge may punish
  messiness of the *record* rather than errors of the *summary*); (4) Layer-2 metrics (recall can be 100% while a
  gate fails: extraction accuracy ≠ usefulness).
- **try_next**: 2–3 runs with exact values using only the keys `summarizer_style, summarizer_size, judge_size,
  noise_types, compare_styles, degradation_ladder, custom_notes`. Good contrasts: `summarizer_style` `careful`;
  `summarizer_size` `large`; a single noise type (e.g. `noise_types` `conflicting_labs`); pasted synthetic notes.
- **caveats**: the pack is synthetic and written for this runbook (not CarePath's Synthea-derived benchmark); the
  gates are simplified lexical/structural checks written for this pack and can misfire on unusual phrasing (the
  claim audit shows what they matched); the judge and summarizer are from the same model family; a single run per
  variant at temperature 0, so scores can move between runs; the paper reports no numbers, so nothing here is a
  reproduction of results.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, main judge score and gate result with reasons, style
comparison, ladder, headline).

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
python3 - "{{results_dir}}" "summarizer_style,summarizer_size,judge_size,noise_types,compare_styles,degradation_ladder,custom_notes" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} summarizer_style,summarizer_size,judge_size,noise_types,compare_styles,degradation_ladder,custom_notes 300 checklist.json
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
"""Source-traceable patient summaries: release gates vs an LLM judge — SMASH 2026 paper #18 (Alissa Taylor, Akinox).

A fixed SYNTHETIC patient pack with planted documentation noise (discontinued medication, resolved vs active
diagnosis, conflicting labs, copied-forward note, document date != event date, negation) and provenance-aware gold
labels. An LLM writes a cited, structured summary; the paper's Layer-1 deterministic release gates and Layer-2
claim metrics are computed in code; an LLM judge gives the usual holistic 1-10 score. The point: a fluent summary
can score well with a judge and still fail a gate that "should never be averaged away".

usage: python experiment.py params.json outdir
"""
import json, re, sys, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e"
NOISE = ["discontinued_med", "resolved_dx", "conflicting_labs", "copied_forward", "date_mismatch", "negation"]
NOISE_LABEL = {"discontinued_med": "discontinued med", "resolved_dx": "resolved diagnosis", "conflicting_labs": "conflicting labs",
               "copied_forward": "copied-forward note", "date_mismatch": "document ≠ event date", "negation": "negated finding"}
GATES = [("schema", "Schema valid"), ("citations", "Citation validity & coverage"), ("negation", "Negation preserved"),
         ("status", "Active/resolved/discontinued status"), ("med_bounds", "Medication start/stop & current dose"),
         ("event_dates", "Event date (not document date)"), ("contradiction", "Conflict surfaced, both sources cited"),
         ("intended_use", "Intended-use language")]


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def s(key, default):
    v = P.get(key, default)
    return default if v is None or (isinstance(v, str) and (v.strip() == "" or v.strip().startswith("{{"))) else v


STYLE = str(s("summarizer_style", "brief")); SIZE = str(s("summarizer_size", "small")); JUDGE = str(s("judge_size", "small"))
nt = str(s("noise_types", "all")).strip().lower()
ON = set(NOISE) if nt in ("all", "") else ({x.strip() for x in nt.split(",")} & set(NOISE) if nt != "none" else set())
COMPARE = str(s("compare_styles", "true")).lower() in ("true", "1", "yes")
LADDER = str(s("degradation_ladder", "true")).lower() in ("true", "1", "yes")
CUSTOM = str(s("custom_notes", "")).strip()

# ---------------------------------------------------------------- the synthetic patient pack (fully fictional)


def build_pack(on):
    """Documents as (id, type, document date, [segments]). Each noise type swaps in a harder version of the same
    underlying clinical state; with it off, the record states that fact cleanly."""
    d = []
    meds_2024 = ("metformin 500 mg twice daily; lisinopril 10 mg daily" if "discontinued_med" in on
                 else "metformin 500 mg twice daily; losartan 50 mg daily")
    d.append(("D1", "Referral letter (GP to endocrinology)", "2024-01-15", [
        "Re: synthetic patient SP-0187, 67-year-old man.",
        "Type 2 diabetes mellitus diagnosed 2016, suboptimally controlled.",
        "Hypertension, on treatment.",
        f"Current medications: {meds_2024}."]))
    d.append(("D2", "Medication reconciliation", "2024-06-10", [
        "Metformin increased from 500 mg to 1000 mg twice daily on 2024-06-10 (pharmacist reconciliation).",
        "No known drug allergies."]))
    if "discontinued_med" in on:
        d.append(("D3", "Progress note (family medicine)", "2024-09-03", [
            "Persistent dry cough for 6 weeks, attributed to ACE inhibitor.",
            "Lisinopril 10 mg daily stopped today, 2024-09-03.",
            "Started losartan 50 mg daily on 2024-09-03."]))
    else:
        d.append(("D3", "Progress note (family medicine)", "2024-09-03", [
            "Blood pressure 132/80 on losartan 50 mg daily; continue."]))
    if "resolved_dx" in on:
        d.append(("D4", "Discharge summary", "2023-03-02", [
            "Admitted 2023-02-24 with right lower lobe community-acquired pneumonia; treated with IV ceftriaxone.",
            "Acute kidney injury on admission (creatinine 168 umol/L), resolved by discharge with IV fluids.",
            "Pneumonia resolved clinically; discharged home 2023-03-02. Follow-up chest X-ray 2023-04-10 clear."]))
    d.append(("D5", "Laboratory report", "2025-02-11", [
        "HbA1c 7.2% (collected 2025-02-11).",
        "eGFR 68 mL/min/1.73m2 (collected 2025-02-11)."]))
    if "negation" in on:
        d.append(("D6", "Imaging report: left leg venous Doppler ultrasound", "2025-02-02", [
            "Indication: left calf swelling after a long flight.",
            "Findings: no evidence of deep vein thrombosis in the left leg.",
            "Impression: negative for DVT."]))
    d.append(("D7", "Endocrinology consult letter", "2025-03-05", [
        ("Most recent HbA1c 8.1%, so glycaemic control has worsened." if "conflicting_labs" in on
         else "Most recent HbA1c 7.2% (2025-02-11)."),
        "Plan: continue metformin 1000 mg twice daily; consider adding an SGLT2 inhibitor at next visit."]))
    if "copied_forward" in on:
        stale = "metformin 500 mg twice daily, lisinopril 10 mg daily" if "discontinued_med" in on else "metformin 500 mg twice daily, losartan 50 mg daily"
        d.append(("D8", "Progress note (family medicine)", "2025-03-20", [
            "Seen for routine follow-up; feels well.",
            f"Medications: {stale}.",
            "Plan: repeat labs in 3 months."]))
    else:
        cur = "metformin 1000 mg twice daily, losartan 50 mg daily"
        d.append(("D8", "Progress note (family medicine)", "2025-03-20", [
            "Seen for routine follow-up; feels well.", f"Medications: {cur}.", "Plan: repeat labs in 3 months."]))
    if "date_mismatch" in on:
        d.append(("D9", "Physiotherapy discharge letter", "2025-04-22", [
            "Patient sustained a fall at home on 2025-01-14 with a left distal radius fracture, treated in a cast.",
            "Completed 8 weeks of physiotherapy; wrist range of motion now near normal."]))
    else:
        d.append(("D9", "Emergency department note", "2025-01-14", [
            "Fall at home today with a left distal radius fracture; cast applied."]))
    return [{"id": i, "type": t, "date": dt, "segments": {f"{i}.{k + 1}": x for k, x in enumerate(seg)}} for i, t, dt, seg in d]


def gold_items(on):
    """Provenance-aware gold labels: concept, expected status, interval, governing source, severity (1-3)."""
    g = [{"key": "t2dm", "label": "Type 2 diabetes", "aliases": ["diabetes", "t2dm"], "status": "active", "src": ["D1.2"], "sev": 2},
         {"key": "htn", "label": "Hypertension", "aliases": ["hypertension", "htn"], "status": "active", "src": ["D1.3"], "sev": 2},
         {"key": "metformin", "label": "Metformin 1000 mg BID (since 2024-06-10)", "aliases": ["metformin"], "status": "active",
          "src": ["D2.1"], "sev": 3, "dose": "1000"},
         {"key": "losartan", "label": "Losartan 50 mg daily" + (" (started 2024-09-03)" if "discontinued_med" in on else ""),
          "aliases": ["losartan"], "status": "active", "src": ["D3.3" if "discontinued_med" in on else "D3.1"], "sev": 2},
         {"key": "hba1c", "label": "HbA1c " + ("7.2% (lab) vs 8.1% (letter): conflict" if "conflicting_labs" in on else "7.2%"),
          "aliases": ["hba1c", "a1c", "glycated"], "status": "conflicting" if "conflicting_labs" in on else "active",
          "src": ["D5.1", "D7.1"] if "conflicting_labs" in on else ["D5.1"], "sev": 2},
         {"key": "fracture", "label": "Fall with L distal radius fracture on 2025-01-14", "aliases": ["fracture", "fall", "radius"],
          "status": "historical", "src": ["D9.1"], "sev": 1, "event_date": "2025-01-14",
          "wrong_date": "2025-04-22" if "date_mismatch" in on else None}]
    if "discontinued_med" in on:
        g.append({"key": "lisinopril", "label": "Lisinopril stopped 2024-09-03 (cough)", "aliases": ["lisinopril", "ace inhibitor"],
                  "status": "discontinued", "src": ["D3.2"], "sev": 3, "stop": "2024-09-03"})
    if "resolved_dx" in on:
        g.append({"key": "pneumonia", "label": "Pneumonia 2023, resolved", "aliases": ["pneumonia"], "status": "resolved", "src": ["D4.1", "D4.3"], "sev": 2})
        g.append({"key": "aki", "label": "Acute kidney injury 2023, resolved", "aliases": ["kidney injury", "aki"], "status": "resolved", "src": ["D4.2"], "sev": 2})
    if "negation" in on:
        g.append({"key": "dvt", "label": "DVT ruled out (Doppler 2025-02-02)", "aliases": ["dvt", "deep vein thrombosis", "thrombosis"],
                  "status": "negated", "src": ["D6.2", "D6.3"], "sev": 3})
    return g


def parse_custom(txt):
    """Paste format: documents separated by lines starting with '===' (optionally '=== type | YYYY-MM-DD')."""
    docs, cur, head = [], [], ("Note", "")
    for line in txt.splitlines() + ["==="]:
        if line.strip().startswith("==="):
            body = " ".join(cur).strip()
            if body:
                segs = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n", body) if x.strip()]
                i = f"D{len(docs) + 1}"
                docs.append({"id": i, "type": head[0], "date": head[1], "segments": {f"{i}.{k + 1}": x for k, x in enumerate(segs)}})
            parts = [x.strip() for x in line.strip("= ").split("|")]
            head = (parts[0] or "Note", parts[1] if len(parts) > 1 else ""); cur = []
        else:
            cur.append(line)
    return docs


def pack_text(pack):
    return "\n\n".join(f"[{d['id']}] {d['type']} | document date {d['date'] or 'unknown'}\n" +
                       "\n".join(f"  ({sid}) {t}" for sid, t in d["segments"].items()) for d in pack)


# ---------------------------------------------------------------- LLM summarizer and judge

SCHEMA = ('{"summary_text": "<the summary a clinician reads>", "claims": [{"text": "<one clinical statement>", '
          '"category": "problem|medication|lab|event|finding", "status": "active|resolved|historical|discontinued|negated|conflicting|uncertain", '
          '"date": "YYYY-MM-DD or empty", "start": "YYYY-MM-DD or empty", "stop": "YYYY-MM-DD or empty", "citations": ["D1.2"]}]}')
STYLES = {
    "careful": ("You write source-traceable patient summaries for clinicians.",
                "Summarize this patient's record for a clinician taking over care. Rules: separate ACTIVE problems from RESOLVED or "
                "HISTORICAL ones; mark stopped medications as discontinued with their stop date and give current doses only from the most "
                "recent authoritative source (beware copied-forward lists); date events by when they happened, not when the document was "
                "written; preserve negations (a ruled-out finding must stay ruled out); if sources conflict, say so and cite both rather "
                "than picking one; cite segment ids for every claim; end the summary_text with an intended-use statement saying it is an "
                "AI-generated summary for clinician review that must be verified against the cited sources."),
    "brief": ("You write concise, readable clinical summaries.",
              "Write a concise, highly readable summary of this patient (under 120 words of summary_text) for a busy clinician. "
              "Cite the segment ids that support each claim."),
    "naive": ("You are a helpful assistant.",
              "Summarize this patient's record: list the problems, medications, recent labs and events. Cite segment ids for each claim."),
}


def summarize_prompts(pack, style):
    sysmsg, task = STYLES[style]
    return sysmsg, (f"{task}\n\nRecord (each segment has an id in parentheses):\n\n{pack_text(pack)}\n\n"
                    f"Use at most 14 claims. Return ONLY a JSON object with this shape (no markdown):\n{SCHEMA}")


def judge_prompt(pack, summ):
    claims = "\n".join(f"- {c.get('text', '')} [{', '.join(map(str, c.get('citations', []) or []))}]" for c in summ.get("claims", []))
    return (f"You are evaluating an AI-generated patient summary.\n\nSOURCE RECORD:\n{pack_text(pack)}\n\nSUMMARY:\n{summ.get('summary_text', '')}"
            f"\n\nCLAIMS WITH CITATIONS:\n{claims}\n\nRate the summary's overall quality for a clinician (accuracy, completeness, "
            'clarity, usefulness) on a 1-10 scale. Return ONLY JSON: {"score": <integer 1-10>, "rationale": "<= 30 words"}')


def safe_json(rep):
    """Parse the model's JSON; if it was cut off mid-claim, keep the complete claims (salvage) rather than discard all."""
    from llm import parse_json
    try:
        d = parse_json(rep)
        return d if isinstance(d, dict) else {}
    except ValueError:
        pass
    i = rep.find("{")
    for j in [m.start() for m in re.finditer(r"\}\s*,?\s*\n", rep)][::-1]:
        try:
            d = json.loads(rep[i:j + 1] + "]}")
            d["_salvaged"] = True
            return d
        except (json.JSONDecodeError, ValueError):
            continue
    return {}


# ---------------------------------------------------------------- Layer 1: deterministic release gates

STATUS_MAP = {"stopped": "discontinued", "ceased": "discontinued", "past": "historical", "previous": "historical", "prior": "historical",
              "ruled out": "negated", "absent": "negated", "negative": "negated", "excluded": "negated", "current": "active",
              "ongoing": "active", "chronic": "active", "conflict": "conflicting", "discrepant": "conflicting"}
NEG = r"\b(no|not|negative|without|ruled out|excluded|denies|absence|absent|free of)\b"
STOP = r"\b(stop\w*|discontinu\w*|ceas\w*|switch\w*|replac\w*|chang\w*|previous\w*|former\w*|prior|no longer|held|withdr\w*)"
RESOLVED = r"\b(resol\w*|histor\w*|hx|prior|previous\w*|past|treated|recover\w*|2023)"
CONFLICT = r"\b(conflict|conflicting|discrepan|differ|inconsisten|versus|vs\.?|whereas|however|but)\b"
INTENDED = r"(verify|verified|verification|clinical judg|not a substitute|clinician review|intended (use|for)|decision support|ai[- ]generated)"


def norm_status(x):
    x = str(x or "").lower().strip()
    return STATUS_MAP.get(x, x)


def clauses(text):
    return [c for c in re.split(r"(?<=[.;!?])\s+|\n+|•|•", text or "") if c.strip()]


def mentions(t, aliases):
    t = t.lower()
    return any(re.search(r"\b" + re.escape(a) + r"\b", t) for a in aliases)


def evaluate(summ, pack, gold, custom=False):
    seg_text = {sid: t for d in pack for sid, t in d["segments"].items()}
    claims = summ.get("claims") if isinstance(summ.get("claims"), list) else []
    text = str(summ.get("summary_text", ""))
    res = {k: {"pass": True, "applicable": True, "why": []} for k, _ in GATES}

    def fail(k, why):
        res[k]["pass"] = False; res[k]["why"].append(why)
    ok_schema = bool(text) and bool(claims) and all(isinstance(c, dict) and c.get("text") for c in claims)
    if not ok_schema:
        fail("schema", "missing summary_text or claims")
    for c in claims:
        cits = [str(x).strip("[]() ") for x in (c.get("citations") or [])] if isinstance(c, dict) else []
        if not cits:
            fail("citations", f"uncited claim: {str(c.get('text', ''))[:60]}")
        bad = [x for x in cits if x not in seg_text]
        if bad:
            fail("citations", f"invalid source id {bad[0]}")
    res["intended_use"]["pass"] = bool(re.search(INTENDED, text, re.I))
    if not res["intended_use"]["pass"]:
        res["intended_use"]["why"].append("no intended-use / verify-against-source statement")
    rel = lambda g: ([c for c in claims if isinstance(c, dict) and mentions(str(c.get("text", "")), g["aliases"])],
                     [cl for cl in clauses(text) if mentions(cl, g["aliases"])])
    audit = []
    if custom:  # gold-free negation check: phrases negated in the source must not be asserted in the summary
        negs = set()
        for t in seg_text.values():
            for m in re.finditer(r"\b(?:no evidence of|negative for|no|denies|without|ruled out)\s+([a-z][a-z \-]{3,40}?)(?=[.,;]|\s(?:in|on|at|and|or)\b|$)", t.lower()):
                term = m.group(1).strip()
                if len(term) > 3 and term not in ("known drug allergies", "change", "changes"):
                    negs.add(term)
        for term in negs:
            for cl in clauses(text):
                if term in cl.lower() and not re.search(NEG, cl.lower()):
                    fail("negation", f"'{term}' asserted without negation")
        for k in ("status", "med_bounds", "event_dates", "contradiction"):
            res[k]["applicable"] = False
        return res, audit, {}
    G = {g["key"]: g for g in gold}
    res["negation"]["applicable"] = "dvt" in G
    res["contradiction"]["applicable"] = G["hba1c"]["status"] == "conflicting"
    res["event_dates"]["applicable"] = G["fracture"]["wrong_date"] is not None
    res["status"]["applicable"] = any(k in G for k in ("lisinopril", "pneumonia", "aki"))
    res["med_bounds"]["applicable"] = "lisinopril" in G or "copied_forward" in ON_EVAL
    covered, supported_hits = 0, 0
    for g in gold:
        cs, cls = rel(g)
        said = "; ".join([f"{c.get('text', '')} [{norm_status(c.get('status'))}]" for c in cs][:2]) or ("; ".join(cls[:1]) or "— not mentioned")
        verdict = "ok"
        mentioned = bool(cs or cls)
        covered += mentioned
        cits = {str(x) for c in cs for x in (c.get("citations") or [])}
        if cs and any(seg in cits for seg in g["src"]):
            supported_hits += 1
        st = [norm_status(c.get("status")) for c in cs]
        if g["key"] == "dvt" and mentioned:
            if any(norm_status(c.get("status")) != "negated" and not re.search(NEG, str(c.get("text", "")).lower()) for c in cs) \
                    or any(not re.search(NEG, cl.lower()) for cl in cls):
                fail("negation", "DVT asserted although the Doppler was negative"); verdict = "NEGATION LOST"
        if g["key"] in ("pneumonia", "aki") and mentioned:
            if any(norm_status(c.get("status")) == "active" and not re.search(RESOLVED, str(c.get("text", "")).lower()) for c in cs) \
                    or any(not re.search(RESOLVED, cl.lower()) for cl in cls):
                fail("status", f"{g['label'].split(' 2023')[0]} presented as active"); verdict = "STATUS INVERSION"
        if g["key"] == "lisinopril" and mentioned:
            if any(norm_status(c.get("status")) == "active" and not re.search(STOP, str(c.get("text", "")).lower()) for c in cs) \
                    or any(not re.search(STOP, cl.lower()) for cl in cls):
                fail("status", "lisinopril presented as a current medication"); verdict = "STATUS INVERSION"
            elif not any(g["stop"] in (str(c.get("stop", "")) + str(c.get("text", ""))) or re.search(r"sep(tember)?\.? 2024|2024-09", str(c.get("text", "")).lower()) for c in cs) \
                    and not any(re.search(r"2024-09-03|sep(tember)?\.? (3,? )?2024", cl.lower()) for cl in cls):
                fail("med_bounds", "lisinopril stop date missing"); verdict = "STOP DATE MISSING"
        if g["key"] == "metformin" and "copied_forward" in ON_EVAL and mentioned:
            bad = [x for x in [str(c.get("text", "")) for c in cs if norm_status(c.get("status")) in ("active", "")] + cls
                   if re.search(r"\b500\s*mg", x.lower()) and not re.search(r"1,?000\s*mg|1 ?g\b|2,?000\s*mg", x.lower())
                   and not re.search(r"increas|previous|from 500|conflict|discrepan|lists|listed|documented|copied|outdated|stale|however", x.lower())]
            if bad:
                fail("med_bounds", "stale copied-forward dose (metformin 500 mg) given as current"); verdict = "STALE DOSE"
        if g["key"] == "fracture" and g["wrong_date"] and mentioned:
            dates = [str(c.get("date", "")) for c in cs] + [cl for cl in cls]
            if any(g["wrong_date"] in x for x in dates) and not any(g["event_date"] in x or re.search(r"jan(uary)?\.? (14,? )?2025", x.lower()) for x in dates):
                fail("event_dates", "fracture dated by the letter (2025-04-22), not the fall (2025-01-14)"); verdict = "WRONG EVENT DATE"
        if g["key"] == "hba1c" and g["status"] == "conflicting":
            alltxt = " ".join([str(c.get("text", "")) for c in cs] + cls)
            both_vals = "7.2" in alltxt and "8.1" in alltxt
            both_src = any(x.startswith("D5") for x in cits) and any(x.startswith("D7") for x in cits)
            flagged = any(x == "conflicting" for x in st) or re.search(CONFLICT, alltxt.lower())
            if not mentioned:
                fail("contradiction", "HbA1c conflict omitted"); verdict = "CONFLICT OMITTED"
            elif not (both_vals and flagged):
                fail("contradiction", "conflicting HbA1c silently resolved to one value"); verdict = "SILENTLY RESOLVED"
            elif not both_src:
                fail("contradiction", "conflict shown but not both sources cited"); verdict = "ONE SOURCE CITED"
        if not mentioned:
            verdict = "omitted"
        audit.append({"item": g["label"], "expected": g["status"], "said": said[:110], "verdict": verdict, "severity": g["sev"]})
    # Layer 2: claim metrics
    sup = 0
    for c in claims:
        if not isinstance(c, dict):
            continue
        words = {w for w in re.findall(r"[a-z0-9.]{4,}", str(c.get("text", "")).lower())}
        segs = " ".join(seg_text.get(str(x), "") for x in (c.get("citations") or [])).lower()
        if words and segs and len([w for w in words if w in segs]) / len(words) >= 0.3:
            sup += 1
    sev_fail = sum(a["severity"] for a in audit if a["verdict"] not in ("ok", "omitted"))
    l2 = {"n_claims": len(claims), "gold_recall": covered / len(gold), "gold_supported_by_governing_source": supported_hits / len(gold),
          "supported_claim_rate": sup / len(claims) if claims else 0.0, "unsupported_claim_rate": 1 - sup / len(claims) if claims else 1.0,
          "severity_weighted_errors": sev_fail, "omitted_items": sum(a["verdict"] == "omitted" for a in audit)}
    return res, audit, l2


ON_EVAL = set()


def run_variants(variants):
    """variants: list of (name, style, noise_set or None for custom)."""
    from llm import chat_many
    packs, golds, prompts, systems = [], [], [], []
    for name, style, on in variants:
        pack = parse_custom(CUSTOM) if on is None else build_pack(on)
        packs.append(pack); golds.append(None if on is None else gold_items(on))
    by_style = {}
    for i, (name, style, on) in enumerate(variants):
        by_style.setdefault(style, []).append(i)
    summ_raw = [None] * len(variants)
    for style, idx in by_style.items():
        sysmsg = summarize_prompts(packs[idx[0]], style)[0]
        reps = chat_many([summarize_prompts(packs[i], style)[1] for i in idx], system=sysmsg, size=SIZE, max_tokens=3200, workers=8)
        for i, r in zip(idx, reps):
            summ_raw[i] = r
    summs = [safe_json(r) for r in summ_raw]
    log(f"{len(variants)} summaries written")
    jreps = chat_many([judge_prompt(p, sm) for p, sm in zip(packs, summs)], system="You are an expert clinical documentation reviewer.",
                      size=JUDGE, max_tokens=200, workers=8)
    out = []
    global ON_EVAL
    for (name, style, on), pack, gold, sm, jr in zip(variants, packs, golds, summs, jreps):
        ON_EVAL = set(on or [])
        gates, audit, l2 = evaluate(sm, pack, gold or [], custom=on is None)
        jd = safe_json(jr)
        try:
            score = int(round(float(jd.get("score"))))
        except (TypeError, ValueError):
            m = re.search(r"\b(10|[1-9])\b", jr); score = int(m.group(1)) if m else None
        app = [k for k, _ in GATES if gates[k]["applicable"]]
        failed = [k for k in app if not gates[k]["pass"]]
        out.append({"name": name, "style": style, "noise": sorted(on) if on is not None else "custom", "judge_score": score,
                    "judge_rationale": jd.get("rationale", ""), "gates": gates, "gates_applicable": len(app),
                    "gates_failed": failed, "released": not failed, "audit": audit, "layer2": l2,
                    "summary_text": sm.get("summary_text", ""), "n_claims": len(sm.get("claims") or [])})
    return out, len(variants) * 2


def main():
    import llm
    custom = bool(CUSTOM)
    main_v = ("main", STYLE, None if custom else set(ON))
    variants = [main_v]
    if COMPARE:
        variants += [(f"style:{st}", st, None if custom else set(ON)) for st in STYLES if st != STYLE]
    ladder_sets = []
    if LADDER and not custom:
        cum = []
        for k in NOISE:
            ladder_sets.append(set(cum)); cum.append(k)
        ladder_sets.append(set(NOISE))
        for j, st in enumerate(ladder_sets):
            if st != set(ON):
                variants.append((f"ladder:{j}", STYLE, st))
    log(f"{len(variants)} variants (summarizer {SIZE}, judge {JUDGE}, style {STYLE}, noise {sorted(ON) if not custom else 'custom notes'})")
    runs, calls = run_variants(variants)
    main_r = runs[0]
    style_runs = [main_r] + [r for r in runs if r["name"].startswith("style:")]
    ladder = []
    if LADDER and not custom:
        for j, st in enumerate(ladder_sets):
            r = main_r if st == set(ON) else next(x for x in runs if x["name"] == f"ladder:{j}")
            ladder.append({"n_noise": len(st), "added": NOISE[j - 1] if j else "none", "judge_score": r["judge_score"],
                           "gates_failed": r["gates_failed"], "gates_applicable": r["gates_applicable"],
                           "gold_recall": r["layer2"].get("gold_recall"), "severity_weighted_errors": r["layer2"].get("severity_weighted_errors")})
    judged_high_but_blocked = [r for r in runs if (r["judge_score"] or 0) >= 7 and not r["released"]]
    content = lambda r: [g for g in r["gates_failed"] if g not in ("intended_use", "schema")]
    judged_high_content = [r for r in runs if (r["judge_score"] or 0) >= 7 and content(r)]
    res = {"params": P, "backend": llm.backend(), "summarizer_model": llm.model_name(SIZE), "judge_model": llm.model_name(JUDGE),
           "llm_calls": calls, "noise_on": sorted(ON) if not custom else "custom", "main": main_r, "style_runs": style_runs,
           "ladder": ladder, "n_variants": len(runs), "n_judged_7plus": sum((r["judge_score"] or 0) >= 7 for r in runs),
           "n_judged_7plus_but_gate_failed": len(judged_high_but_blocked),
           "n_judged_7plus_but_clinical_gate_failed": len(judged_high_content),
           "judged_7plus_but_clinical_gate_failed": [{"name": r["name"], "judge_score": r["judge_score"], "failed": content(r)} for r in judged_high_content],
           "judge_gate_agreement": float(np.mean([((r["judge_score"] or 0) >= 7) == r["released"] for r in runs])),
           "all_runs": [dict({k: r[k] for k in ("name", "style", "noise", "judge_score", "judge_rationale", "gates_failed", "released", "layer2", "audit", "summary_text")},
                             gate_reasons={g: r["gates"][g]["why"] for g in r["gates_failed"]}) for r in runs]}
    figures(res); card(res)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=list))
    log(f"done: main ({STYLE}) judge {main_r['judge_score']}/10, gates failed {main_r['gates_failed'] or 'none'}; "
        f"{res['n_judged_7plus_but_gate_failed']}/{res['n_variants']} variants judged >=7 yet blocked; {calls} LLM calls")


# ---------------------------------------------------------------- figures and card

def figures(res):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    rows = res["style_runs"]
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 0.9 + 0.62 * len(rows)), gridspec_kw={"width_ratios": [1, 1.5]})
    ax = axs[0]
    for i, r in enumerate(rows[::-1]):
        sc = r["judge_score"] or 0
        ax.barh(i, sc, color=ACC if not r["released"] else GOOD, height=0.55)
        ax.text(sc + 0.2, i, f"{sc}/10", va="center", fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{r['style']}{' (yours)' if r['name'] == 'main' else ''}" for r in rows[::-1]], fontsize=9)
    ax.set_xlim(0, 11.5); ax.set_xlabel("LLM-judge score"); ax.set_title("Judge says…", fontsize=9, loc="left")
    ax = axs[1]
    for i, r in enumerate(rows[::-1]):
        for j, (k, _) in enumerate(GATES):
            gk = r["gates"][k]
            col = "#dee2e6" if not gk["applicable"] else (GOOD if gk["pass"] else ACC)
            ax.add_patch(plt.Rectangle((j, i - 0.3), 0.85, 0.6, color=col))
        ax.text(len(GATES) + 0.1, i, "RELEASE" if r["released"] else "BLOCKED", va="center", fontsize=8,
                color=GOOD if r["released"] else ACC, fontweight="bold")
    ax.set_xlim(0, len(GATES) + 1.9); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xticks(np.arange(len(GATES)) + 0.42); ax.set_xticklabels([str(j + 1) for j in range(len(GATES))], fontsize=8)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_xlabel("Layer-1 release gate (see list below)")
    ax.set_title("…release gates say (green pass, orange fail, grey n/a)", fontsize=8, loc="left")
    fig.tight_layout(); fig.savefig(OUT / "fig_judge_vs_gates.png", dpi=160); plt.close(fig)

    if res["ladder"]:
        L = res["ladder"]; x = np.arange(len(L))
        fig, ax = plt.subplots(figsize=(6.4, 3.1))
        ax.plot(x, [(l["judge_score"] or 0) / 10 for l in L], "o-", color=MUTED, label="judge score / 10")
        ax.plot(x, [l["gold_recall"] for l in L], "s-", color=BLUE, label="gold-claim recall")
        ax.plot(x, [1 - len([g for g in l["gates_failed"] if g != "intended_use"]) / max(l["gates_applicable"] - 1, 1) for l in L], "D-", color=ACC,
                label="clinical gates passed (share)")
        for xi, l in zip(x, L):
            if l["gates_failed"]:
                ax.text(xi, 0.02, "\n".join(g.replace("_", " ") for g in l["gates_failed"]), ha="center", va="bottom", fontsize=6, color=ACC)
        ax.set_xticks(x); ax.set_xticklabels(["clean"] + ["+ " + NOISE_LABEL[l["added"]] for l in L[1:]], rotation=25, ha="right", fontsize=7.5)
        ax.set_ylim(0, 1.08); ax.legend(frameon=False, fontsize=7.5, loc="upper right", bbox_to_anchor=(1, 1.18), ncol=3)
        ax.set_ylabel("score"); ax.set_title(f"Same clinical state, more documentation noise ({STYLE} prompt)", fontsize=9, loc="left", pad=18)
        fig.tight_layout(); fig.savefig(OUT / "fig_degradation.png", dpi=160); plt.close(fig)

    A = res["main"]["audit"]
    if A:
        import textwrap
        wrapped = [(textwrap.wrap(a["item"], 34), textwrap.wrap(a["said"], 52)[:2], a["verdict"]) for a in A]
        heights = [max(len(w[0]), len(w[1]), 1) for w in wrapped]
        tot = sum(h * 0.45 + 0.35 for h in heights) + 1.3
        fig, ax = plt.subplots(figsize=(6.4, 0.3 + 0.3 * tot)); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(tot, 0)
        xs = [0.0, 0.37, 0.84]
        for x, h in zip(xs, ["Gold item (governing source)", "Summary says [status]", "Verdict"]):
            ax.text(x, 0.6, h, fontsize=7.5, fontweight="bold", va="center")
        y = 1.3
        for (it, sd, v), h in zip(wrapped, heights):
            ax.axhline(y - 0.15, color="#dee2e6", lw=0.6)
            ax.text(xs[0], y, "\n".join(it), fontsize=7, va="top", linespacing=1.25)
            ax.text(xs[1], y, "\n".join(sd), fontsize=7, va="top", color="#343a40", linespacing=1.25)
            ax.text(xs[2], y, v, fontsize=7, va="top", fontweight="bold", color=GOOD if v == "ok" else (MUTED if v == "omitted" else ACC))
            y += h * 0.45 + 0.35
        fig.tight_layout(pad=0.3); fig.savefig(OUT / "fig_claim_audit.png", dpi=160); plt.close(fig)


def card(res):
    m = res["main"]; L2 = m["layer2"]
    names = dict(GATES)
    failed_names = [names[k] for k in m["gates_failed"]]
    tiles = [{"label": "LLM-judge score", "value": f"{m['judge_score']}/10" if m["judge_score"] is not None else "n/a",
              "sub": f"{res['judge_model']} · holistic quality, as many pipelines report it", "tone": "neutral"},
             {"label": "Release gates", "value": "PASSED" if m["released"] else f"FAILED {len(m['gates_failed'])} of {m['gates_applicable']}",
              "sub": ("all applicable Layer-1 checks pass" if m["released"] else "; ".join(m["gates"][k]["why"][0] for k in m["gates_failed"] if m["gates"][k]["why"])[:160]),
              "tone": "good" if m["released"] else "accent"}]
    if L2:
        tiles.append({"label": "Gold claims covered", "value": f"{L2['gold_recall']:.0%}",
                      "sub": f"{L2['n_claims']} claims · {L2['unsupported_claim_rate']:.0%} not lexically supported by their cited segment · "
                             f"severity-weighted errors {L2['severity_weighted_errors']}", "tone": "neutral"})
    ex = res["judged_7plus_but_clinical_gate_failed"]

    def disp(n):
        if n.startswith("ladder:"):
            j = int(n.split(":")[1]); return f"{STYLE} prompt on the pack with {j} noise type{'s' if j != 1 else ''}" + (f" (up to {NOISE_LABEL[NOISE[j - 1]]})" if j else "")
        return n.replace("style:", "") + " prompt" if n != "main" else "your run"
    tiles.append({"label": "Judged ≥ 7/10 yet a clinical gate failed", "value": f"{res['n_judged_7plus_but_clinical_gate_failed']} of {res['n_variants']}",
                  "sub": (f"e.g. {disp(ex[0]['name'])}: judge {ex[0]['judge_score']}/10, failed {', '.join(ex[0]['failed'])} · " if ex else "")
                         + f"{res['n_judged_7plus_but_gate_failed']} counting the intended-use gate",
                  "tone": "warn" if ex else "good"})
    inputs = {"summarizer": f"{res['summarizer_model']} · {STYLE} prompt", "judge": res["judge_model"],
              "noise": ", ".join(NOISE_LABEL[k] for k in res["noise_on"]) if isinstance(res["noise_on"], list) and res["noise_on"] else ("custom notes" if CUSTOM else "none"),
              "variants": res["n_variants"], "LLM calls": res["llm_calls"]}
    compare = [
        {"metric": "Release gates vs averaged scores", "paper": "“A gain in readability should not offset broken evidence links, a known status inversion, or loss of negation.”",
         "yours": f"{STYLE}: judge {m['judge_score']}/10, gates " + ("passed" if m["released"] else "FAILED (" + ", ".join(failed_names) + ")"), "note": "framework claim; no paper numbers"},
        {"metric": "Model-as-judge", "paper": "should not serve as the sole evidence of clinical acceptability because judge models may share blind spots with the system being evaluated",
         "yours": f"judge (≥7) and gates agreed on {res['judge_gate_agreement']:.0%} of {res['n_variants']} summaries", "note": "same model family judges itself"},
        {"metric": "Missing sources", "paper": "“If a claim lacks an accessible source, the presence of other well-supported claims should not compensate for it.”",
         "yours": "citation gate " + ("passed" if m["gates"]["citations"]["pass"] else "FAILED: " + m["gates"]["citations"]["why"][0]), "note": ""},
        {"metric": "Severity", "paper": "“Errors should be stratified by likely consequence rather than counted equally.”",
         "yours": f"severity-weighted errors {L2.get('severity_weighted_errors', 'n/a')} (gold severities 1–3)" if L2 else "custom notes: no gold labels", "note": ""},
        {"metric": "Controlled noise", "paper": "duplicate and copied-forward statements, missing fields, conflicting sources, resolved-versus-active ambiguity, medication changes, and differences between document date and clinical-event date",
         "yours": f"{len(res['noise_on']) if isinstance(res['noise_on'], list) else 'custom'} noise types planted; ladder of {len(res['ladder'])} packs" if res["ladder"] else "custom notes (gold-free gates only)", "note": "Synthea-style pack written for this runbook"}]
    figs = [{"path": "fig_judge_vs_gates.png", "title": "Would a judge ship it, and would the release gates?",
             "caption": "Left: holistic LLM-judge score for each prompt style on the same pack. Right: the paper's Layer-1 checks — "
                        + "; ".join(f"{j + 1} {n}" for j, (_, n) in enumerate(GATES)) + "."}]
    if (OUT / "fig_claim_audit.png").exists():
        figs.append({"path": "fig_claim_audit.png", "title": "Claim-level audit against provenance-aware gold labels",
                     "caption": "Each planted fact, what your summary said about it (status in brackets), and the deterministic verdict. "
                                "Capitalised verdicts are gate failures; 'omitted' only lowers recall."})
    if (OUT / "fig_degradation.png").exists():
        figs.append({"path": "fig_degradation.png", "title": "Does quality degrade as documentation noise is added?",
                     "caption": "The same underlying clinical state presented with one more noise type at a time (the paper's controlled-noise design). "
                                "Failed gates are listed under each point."})
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 18, "title": "From Extraction Accuracy to Clinical Usefulness: A Human-Centered Evaluation Framework for Source-Traceable Patient Summaries",
                  "authors": "Alissa Taylor", "url": "https://drive.google.com/file/d/10P_qlRn02fwt-f2id3gu_oRUfPCTcpgr/view?usp=sharing", "affiliation": "Akinox Solutions (CarePath)"},
        "inputs": inputs, "tiles": tiles, "figures": figs, "compare": compare,
        "runbook": {"name": "smash-18-source-traceable-summaries", "url": P.get("runbook_url", "")}}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
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
