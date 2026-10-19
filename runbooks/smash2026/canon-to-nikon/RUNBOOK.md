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
    skill_name: smash-06-canon-to-nikon
    confidence: high
---

# Canon or Nikon? Camera Shift and Who Gets Missed in Retinal AI Screening (SMASH 2026 · Paper #6)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"From Canon to Nikon: Camera Domain Shift and Potential Equity Implications in Retinal AI"** (Lisa Y.W. Tang).
Read the paper: https://drive.google.com/file/d/1cEMU7Sho9vz6uA6rD2xq78R9KDpaOwuK/view?usp=sharing

The paper's claims: in the Brazilian BRSET cohort (8,524 patients), a classifier trained on frozen RETFound-Green
embeddings of **Canon CR-2** images and tested on **Nikon NF5050** images loses performance on some retinal tasks and
not others. The loss depends far more on the **task** than on the input resolution or downstream classifier, and
Nikon images are more than twice as likely to be **inadequate** although the Nikon camera costs much less. That is a
cost–quality trade-off with equity consequences.

BRSET is credentialed, so this runbook uses the **paper's own published numbers**: all 240 internal/external cells of
Table 4 are transcribed verbatim, along with Table 1's quality rates and the footnoted camera prices. The participant chooses a task, classifier,
resolution and a screening program (budget, sites, patients, prevalence, operating point). The run:
1. **Explorer**: compares internal and external performance across all 12 tasks and decomposes the gap's variance into task, classifier and resolution.
2. **Screening calculator** (this runbook's extension): for the budget, compares all-Canon, all-Nikon and the best
   mix of cameras by referable cases missed per year (unscreened + ungradable + false negatives), and computes the **equity gap**,
   meaning how much likelier a diseased patient at a Nikon site is to be missed than one at a Canon site.
3. **Synthetic mechanism demo**: simulated embeddings in which the "Nikon camera" remixes colour/optical features.
   It shows why tasks whose signal lives in camera-sensitive features break, and why cleaner (higher-resolution)
   features do not close the gap.

Output: a shareable **result card**. Target wall-clock: **under 4 minutes.** The experiment takes about 1 second.

### Calculator model (state it on the card)
- A Canon-trained model runs at every site. Canon sites see the **internal** AUROC and Nikon sites the **external** AUROC (Table 4).
- Sensitivity at the chosen specificity follows from an equal-variance binormal ROC: `d' = √2·Φ⁻¹(AUROC)`, `sens = Φ(d' − Φ⁻¹(spec))`.
- Inadequate images (Canon 8.79%, Nikon 18.60%): a fraction `recapture_pct` are retaken and graded; the rest are never graded.
- Prices: Canon CR-2 R$95,000, Nikon NF5050 R$35,000 (paper footnote 1). Sites without a camera are unscreened.
- The "best mix" is an exhaustive search over the number of Canon and Nikon sites within the budget that minimises missed cases.

### Paper headline numbers (quote exactly)
- Inadequate images: Canon CR **8.79%**, Nikon NF5050 **18.60%** (Table 1; Cramér's V 0.142, p < 0.001).
  Image field 4.76% vs **15.84%** (Table 1); the text says "16.5% vs. 4.8%" (OR = 3.95).
- Table 2 (best classifier): DR **0.940 → 0.946**, scar 0.964 → 0.955, hemorrhage **0.804 → 0.569**,
  hypertensive retinopathy **0.864 → 0.690**, DR staging (QWK) **0.692 → 0.527**, AMD 0.976 → 0.909, nevus 0.840 → 0.795.
- Figure 2 caption: hemorrhage and hypertensive retinopathy degrade by "∆ AUROC=0.15–0.28".
- "neither higher input resolution nor classifier choice consistently mitigated cross-camera variation."
- Known inconsistencies in the paper, which the card states: the cost wording ("approximately half as much" in the abstract,
  "1.5 times more" in the introduction, while R$95,000 vs R$35,000 is 2.71×); image field 15.84% vs 16.5%; illumination
  Cramér's V 0.028 (table) vs 0.023 (text).

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All computed numbers (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Task | `{{task}}` | `Diabetic Retinopathy` | One of: DR Staging (ICDR), Diabetic Retinopathy, AMD, Hemorrhage, Hypertensive Retinopathy, Increased Cup/Disc, Macular Edema, Myopic Fundus, Nevus, Other, Scar, Vascular Occlusion |
| Classifier | `{{classifier}}` | `best` | `best` (the paper's Table 2 choice for the task) or `SVM`, `LR`, `HGB`, `kNN`, `RF` |
| Resolution | `{{resolution}}` | `best` | `best` (Table 2) or `224`, `392`, `672`, `952` px |
| Budget (R$) | `{{budget_brl}}` | `1900000` | Camera budget for the screening program, in Brazilian reais |
| Sites | `{{n_sites}}` | `40` | Screening sites that need a camera |
| Patients per site | `{{patients_per_site}}` | `1000` | Patients screened per site per year |
| Prevalence (%) | `{{prevalence_pct}}` | `10` | Share of screened patients who have the condition and should be referred |
| Specificity | `{{specificity}}` | `0.90` | Operating point for the AI referral decision |
| Re-imaged if inadequate (%) | `{{recapture_pct}}` | `50` | Share of inadequate photos that are retaken and graded |
| Synthetic shift strength | `{{shift_strength}}` | `1.0` | Camera-shift strength in the synthetic mechanism demo (0 = none, 3 = severe) |
| Seed | `{{seed}}` | `7` | Random seed (synthetic demo only) |

## Dependencies

numpy, scikit-learn and matplotlib (preinstalled in `python312-uv`). No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, sklearn, matplotlib" 2>/dev/null || uv pip install --system -q numpy scikit-learn matplotlib
```

Write `/app/work/params.json`. If a value still looks like an unsubstituted `{{…}}` placeholder, use the table
default. `task`, `classifier` and `resolution` are strings; the rest are numbers. The script clamps out-of-range
numbers itself and lists each clamp in `results.json → caveats_from_inputs`. Copy those entries into the caveats.

```json
{"task": "{{task}}", "classifier": "{{classifier}}", "resolution": "{{resolution}}", "budget_brl": {{budget_brl}},
 "n_sites": {{n_sites}}, "patients_per_site": {{patients_per_site}}, "prevalence_pct": {{prevalence_pct}},
 "specificity": {{specificity}}, "recapture_pct": {{recapture_pct}}, "shift_strength": {{shift_strength}},
 "seed": {{seed}}, "runbook_url": ""}
```

## Step 2: Get the code (extract it, don't retype it)

The tested implementation, including the transcribed Table 4, is embedded in the **Appendix** at the end of this runbook. Do not
rewrite, "improve", or re-derive it. **Always run the command below first, exactly as written.** It copies the files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it won't work: run it and read its output:

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
python3 extract.py experiment.py render_card.py validate.py
```

If it exits non-zero or prints `MISSING`, write each missing file from the Appendix **exactly as given**, one
heredoc per file (quoted delimiter, e.g. `cat > experiment.py <<'PYEOF'`). If a later step fails, fix only
environment problems (missing package), never the methodology or the transcribed numbers.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 240 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: about 1 second. It ends with a `done:` line giving the task's internal → external score, missed cases per year for
all-Canon, all-Nikon and the best mix, the equity ratio, and the most camera-fragile task.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): a finding for **this participant's budget and task**, with 1–2 numbers copied from
  `results.json`. Examples: missed cases per year under all-Nikon vs all-Canon (`calculator.programs.*.missed`,
  rounded to integers), or the equity ratio (`calculator.equity_miss_ratio`) for a fragile task. Not a method description.
- **idea**: (1) the same model trained on one camera and tested on another; (2) the damage is task-specific; (3) resolution or
  classifier changes do not fix it, so programs must evaluate per camera.
- **findings**: (1) the chosen task's internal → external score (`selected`) and where it ranks among the 12 tasks
  (`per_task`, `most_fragile_task`); (2) variance shares (`gap_variance_share`) and the resolution check
  (`resolution_952_vs_224_shrinks_gap` / `widens_gap` counts out of 11); (3) the program comparison at this budget
  (`calculator.programs`: sites covered, missed, inadequate images; `best_mix` composition; CI range from
  `programs_ci_low/high`); (4) whether the answer flips across tasks (`tasks_where_all_nikon_misses_fewer`, `all_tasks_calculator`).
  Every number must come from `results.json`. Do not round 0.940 to 0.94 in one place and leave it unrounded elsewhere.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `task, classifier, resolution, budget_brl, n_sites,
  patients_per_site, prevalence_pct, specificity, recapture_pct, shift_strength, seed`. Good contrasts: a fragile task
  (`Hemorrhage` or `Hypertensive Retinopathy`); a large budget (`budget_brl` ≥ 3800000, where all-Canon covers every site);
  `recapture_pct` 0; a different classifier (`kNN`) for DR staging.
- **caveats**: the numbers are transcribed from the paper, not recomputed, and no images were used; the calculator is this runbook's
  extension, with its stated assumptions; camera and image quality are confounded and the case mix differs between cohorts; the paper's
  internal inconsistencies. Add any `caveats_from_inputs`.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, the task's score change, the three programs' missed cases, the equity ratio, the headline).

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
python3 - "{{results_dir}}" 120 <<'PY'
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
python3 - "{{results_dir}}" "task,classifier,resolution,budget_brl,n_sites,patients_per_site,prevalence_pct,specificity,recapture_pct,shift_strength,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} task,classifier,resolution,budget_brl,n_sites,patients_per_site,prevalence_pct,specificity,recapture_pct,shift_strength,seed 120 checklist.json
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
"""Canon -> Nikon camera-shift explorer and screening-program calculator — SMASH 2026 paper #6 (Lisa Y.W. Tang).

The paper's raw data (BRSET) is credentialed, so this runbook works from the paper's OWN published numbers:
  1. Table 4 (transcribed verbatim: 12 tasks x 5 classifiers x 4 resolutions, internal Canon test vs external
     Nikon cohort, with 95% bootstrap CIs) -> which tasks are camera-fragile, and does resolution/classifier help?
  2. Table 1 image-quality rates + the paper's camera prices -> a screening-program calculator: for a budget,
     number of sites and a task, compare all-Canon, all-Nikon and mixed programs (coverage, ungradable images,
     detected and missed referrals, equity gap between Canon and Nikon sites).
  3. A synthetic domain-shift demo (simulated embeddings, NOT RETFound-Green) showing why tasks whose signal
     lives in camera-sensitive features degrade, and why higher resolution does not close the gap.

usage: python experiment.py params.json outdir
"""
import json, sys, time
from pathlib import Path
from statistics import NormalDist

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
ND = NormalDist()


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


# ------------------------------------------------------------------ the paper's numbers (verbatim)
# Table 4: Task|Alg|  per resolution 224 ; 392 ; 672 ; 952:  internal lo hi external lo hi
# (QWK for DR Staging, AUROC otherwise). "0.65674" is printed that way in the paper.
TABLE4 = """
DR Staging (ICDR)|SVM|0.611 0.508 0.682 0.669 0.619 0.728 ; 0.635 0.549 0.725 0.705 0.657 0.752 ; 0.662 0.581 0.739 0.716 0.671 0.760 ; 0.538 0.452 0.635 0.657 0.610 0.701
DR Staging (ICDR)|LR|0.579 0.524 0.629 0.601 0.551 0.652 ; 0.65674 0.606 0.699 0.579 0.538 0.632 ; 0.637 0.580 0.699 0.503 0.469 0.550 ; 0.587 0.523 0.656 0.549 0.513 0.596
DR Staging (ICDR)|HGB|0.642 0.549 0.715 0.580 0.525 0.634 ; 0.692 0.615 0.765 0.527 0.478 0.577 ; 0.574 0.499 0.672 0.350 0.284 0.410 ; 0.516 0.415 0.607 0.292 0.207 0.359
DR Staging (ICDR)|kNN|0.487 0.390 0.590 0.276 0.215 0.353 ; 0.469 0.372 0.584 0.229 0.166 0.291 ; 0.329 0.216 0.443 0.130 0.076 0.195 ; 0.296 0.179 0.407 0.112 0.061 0.164
DR Staging (ICDR)|RF|0.301 0.192 0.409 0.065 0.026 0.107 ; 0.262 0.165 0.386 0.074 0.031 0.116 ; 0.203 0.087 0.310 0.018 -0.001 0.043 ; 0.142 0.051 0.250 0.019 0.000 0.044
Diabetic Retinopathy|SVM|0.887 0.847 0.915 0.893 0.872 0.911 ; 0.933 0.905 0.954 0.930 0.915 0.946 ; 0.934 0.906 0.958 0.936 0.918 0.949 ; 0.935 0.910 0.953 0.912 0.893 0.926
Diabetic Retinopathy|LR|0.893 0.859 0.922 0.906 0.886 0.924 ; 0.933 0.907 0.956 0.940 0.926 0.954 ; 0.940 0.916 0.963 0.946 0.932 0.957 ; 0.938 0.912 0.957 0.930 0.914 0.943
Diabetic Retinopathy|HGB|0.900 0.869 0.926 0.897 0.878 0.919 ; 0.926 0.903 0.948 0.933 0.915 0.948 ; 0.919 0.890 0.941 0.924 0.907 0.941 ; 0.911 0.890 0.932 0.907 0.893 0.924
Diabetic Retinopathy|kNN|0.817 0.778 0.853 0.796 0.763 0.821 ; 0.837 0.800 0.871 0.829 0.802 0.856 ; 0.808 0.765 0.853 0.794 0.767 0.822 ; 0.770 0.723 0.815 0.770 0.745 0.795
Diabetic Retinopathy|RF|0.894 0.864 0.918 0.891 0.871 0.911 ; 0.913 0.883 0.939 0.931 0.917 0.945 ; 0.908 0.886 0.936 0.927 0.912 0.941 ; 0.889 0.863 0.914 0.893 0.877 0.908
AMD|SVM|0.925 0.887 0.959 0.906 0.870 0.941 ; 0.948 0.912 0.973 0.888 0.844 0.928 ; 0.971 0.958 0.984 0.889 0.842 0.932 ; 0.965 0.936 0.985 0.890 0.829 0.935
AMD|LR|0.941 0.910 0.968 0.907 0.873 0.937 ; 0.962 0.939 0.979 0.901 0.865 0.941 ; 0.975 0.958 0.989 0.915 0.873 0.951 ; 0.976 0.961 0.987 0.909 0.857 0.948
AMD|HGB|0.958 0.939 0.973 0.821 0.751 0.870 ; 0.960 0.938 0.978 0.839 0.779 0.883 ; 0.972 0.956 0.984 0.819 0.768 0.875 ; 0.967 0.949 0.982 0.831 0.772 0.891
AMD|kNN|0.794 0.719 0.847 0.671 0.614 0.725 ; 0.857 0.786 0.905 0.741 0.682 0.806 ; 0.899 0.851 0.946 0.704 0.638 0.762 ; 0.849 0.802 0.899 0.737 0.672 0.795
AMD|RF|0.943 0.916 0.962 0.790 0.711 0.855 ; 0.954 0.930 0.974 0.829 0.761 0.877 ; 0.958 0.933 0.980 0.813 0.744 0.866 ; 0.958 0.938 0.973 0.804 0.715 0.865
Hemorrhage|SVM|0.782 0.619 0.888 0.586 0.454 0.710 ; 0.709 0.559 0.797 0.568 0.453 0.700 ; 0.779 0.657 0.867 0.555 0.432 0.685 ; 0.705 0.560 0.808 0.572 0.470 0.697
Hemorrhage|LR|0.794 0.619 0.906 0.601 0.478 0.733 ; 0.754 0.599 0.840 0.580 0.456 0.707 ; 0.804 0.670 0.891 0.569 0.451 0.716 ; 0.728 0.565 0.841 0.594 0.491 0.723
Hemorrhage|HGB|0.705 0.506 0.824 0.682 0.552 0.784 ; 0.757 0.537 0.887 0.610 0.511 0.738 ; 0.738 0.584 0.884 0.676 0.579 0.794 ; 0.701 0.485 0.864 0.674 0.540 0.775
Hemorrhage|kNN|0.622 0.519 0.733 0.551 0.480 0.624 ; 0.596 0.478 0.694 0.583 0.499 0.665 ; 0.500 0.463 0.550 0.534 0.478 0.612 ; 0.533 0.469 0.620 0.569 0.502 0.648
Hemorrhage|RF|0.785 0.621 0.907 0.749 0.670 0.806 ; 0.785 0.593 0.907 0.727 0.630 0.823 ; 0.725 0.516 0.884 0.696 0.558 0.824 ; 0.707 0.560 0.848 0.746 0.627 0.846
Hypertensive Retinopathy|SVM|0.703 0.597 0.805 0.530 0.470 0.579 ; 0.793 0.719 0.877 0.523 0.462 0.567 ; 0.776 0.682 0.857 0.567 0.507 0.618 ; 0.776 0.688 0.864 0.532 0.478 0.586
Hypertensive Retinopathy|LR|0.734 0.645 0.836 0.568 0.511 0.621 ; 0.840 0.774 0.914 0.564 0.502 0.609 ; 0.822 0.739 0.901 0.599 0.546 0.648 ; 0.803 0.721 0.879 0.552 0.494 0.601
Hypertensive Retinopathy|HGB|0.818 0.747 0.889 0.664 0.625 0.708 ; 0.826 0.741 0.891 0.663 0.601 0.710 ; 0.799 0.723 0.856 0.673 0.617 0.715 ; 0.761 0.696 0.832 0.634 0.586 0.698
Hypertensive Retinopathy|kNN|0.646 0.575 0.732 0.547 0.503 0.607 ; 0.673 0.607 0.762 0.568 0.530 0.607 ; 0.616 0.554 0.698 0.517 0.466 0.567 ; 0.617 0.545 0.710 0.502 0.462 0.551
Hypertensive Retinopathy|RF|0.797 0.694 0.870 0.690 0.629 0.753 ; 0.864 0.809 0.909 0.690 0.635 0.745 ; 0.820 0.731 0.875 0.622 0.579 0.672 ; 0.794 0.725 0.848 0.628 0.587 0.679
Increased Cup/Disc|SVM|0.853 0.836 0.869 0.829 0.817 0.841 ; 0.871 0.855 0.888 0.850 0.836 0.863 ; 0.865 0.848 0.879 0.844 0.827 0.855 ; 0.859 0.838 0.872 0.843 0.829 0.855
Increased Cup/Disc|LR|0.854 0.838 0.872 0.839 0.828 0.850 ; 0.870 0.854 0.887 0.856 0.843 0.869 ; 0.868 0.851 0.882 0.852 0.837 0.864 ; 0.862 0.841 0.874 0.846 0.831 0.857
Increased Cup/Disc|HGB|0.804 0.781 0.823 0.749 0.730 0.767 ; 0.813 0.790 0.830 0.793 0.777 0.807 ; 0.818 0.800 0.835 0.783 0.766 0.799 ; 0.819 0.799 0.836 0.781 0.762 0.795
Increased Cup/Disc|kNN|0.737 0.710 0.760 0.683 0.662 0.703 ; 0.729 0.700 0.751 0.699 0.676 0.714 ; 0.735 0.715 0.758 0.678 0.658 0.695 ; 0.719 0.694 0.739 0.664 0.642 0.684
Increased Cup/Disc|RF|0.782 0.759 0.801 0.746 0.730 0.766 ; 0.790 0.773 0.808 0.784 0.767 0.801 ; 0.793 0.771 0.808 0.782 0.765 0.798 ; 0.792 0.771 0.808 0.783 0.767 0.798
Macular Edema|SVM|0.881 0.820 0.949 0.961 0.941 0.978 ; 0.897 0.815 0.969 0.984 0.975 0.991 ; 0.916 0.856 0.973 0.983 0.976 0.989 ; 0.917 0.867 0.970 0.979 0.965 0.989
Macular Edema|LR|0.906 0.853 0.962 0.968 0.948 0.985 ; 0.913 0.839 0.974 0.987 0.980 0.994 ; 0.927 0.875 0.978 0.990 0.986 0.993 ; 0.928 0.883 0.977 0.982 0.970 0.992
Macular Edema|HGB|0.946 0.919 0.969 0.946 0.929 0.959 ; 0.934 0.895 0.971 0.965 0.951 0.978 ; 0.945 0.909 0.976 0.962 0.949 0.974 ; 0.939 0.911 0.966 0.963 0.953 0.974
Macular Edema|kNN|0.809 0.724 0.878 0.851 0.816 0.888 ; 0.844 0.781 0.893 0.901 0.871 0.936 ; 0.765 0.678 0.847 0.842 0.808 0.892 ; 0.750 0.671 0.814 0.786 0.752 0.840
Macular Edema|RF|0.942 0.917 0.964 0.936 0.916 0.959 ; 0.952 0.928 0.975 0.952 0.931 0.965 ; 0.948 0.920 0.970 0.954 0.936 0.969 ; 0.926 0.889 0.955 0.954 0.935 0.969
Myopic Fundus|SVM|0.960 0.923 0.986 0.975 0.965 0.983 ; 0.974 0.953 0.991 0.978 0.966 0.989 ; 0.990 0.984 0.994 0.972 0.959 0.986 ; 0.991 0.986 0.994 0.975 0.963 0.984
Myopic Fundus|LR|0.970 0.944 0.990 0.985 0.979 0.991 ; 0.981 0.965 0.992 0.983 0.972 0.991 ; 0.989 0.983 0.994 0.978 0.958 0.992 ; 0.989 0.984 0.993 0.977 0.968 0.989
Myopic Fundus|HGB|0.981 0.970 0.991 0.965 0.942 0.986 ; 0.986 0.978 0.993 0.990 0.984 0.994 ; 0.982 0.973 0.989 0.975 0.955 0.989 ; 0.983 0.971 0.990 0.972 0.952 0.989
Myopic Fundus|kNN|0.905 0.838 0.960 0.878 0.835 0.925 ; 0.890 0.826 0.955 0.864 0.817 0.927 ; 0.892 0.827 0.951 0.882 0.841 0.924 ; 0.892 0.827 0.950 0.835 0.782 0.888
Myopic Fundus|RF|0.980 0.971 0.990 0.975 0.955 0.991 ; 0.983 0.975 0.991 0.989 0.982 0.994 ; 0.983 0.975 0.991 0.986 0.979 0.993 ; 0.981 0.972 0.989 0.981 0.969 0.990
Nevus|SVM|0.721 0.614 0.854 0.724 0.632 0.815 ; 0.685 0.578 0.803 0.751 0.654 0.839 ; 0.822 0.749 0.878 0.771 0.682 0.861 ; 0.830 0.712 0.893 0.795 0.710 0.885
Nevus|LR|0.724 0.610 0.847 0.738 0.659 0.831 ; 0.708 0.601 0.827 0.754 0.662 0.842 ; 0.832 0.772 0.894 0.775 0.692 0.858 ; 0.840 0.729 0.903 0.795 0.711 0.886
Nevus|HGB|0.521 0.380 0.643 0.617 0.517 0.703 ; 0.582 0.435 0.694 0.683 0.582 0.781 ; 0.607 0.503 0.731 0.666 0.570 0.746 ; 0.526 0.364 0.646 0.591 0.490 0.687
Nevus|kNN|0.553 0.480 0.658 0.520 0.461 0.593 ; 0.473 0.424 0.549 0.538 0.469 0.605 ; 0.514 0.456 0.602 0.546 0.477 0.607 ; 0.490 0.439 0.562 0.593 0.508 0.671
Nevus|RF|0.548 0.396 0.659 0.610 0.493 0.720 ; 0.493 0.387 0.592 0.644 0.544 0.740 ; 0.563 0.423 0.670 0.634 0.529 0.725 ; 0.539 0.401 0.647 0.548 0.451 0.650
Other|SVM|0.808 0.770 0.842 0.695 0.659 0.732 ; 0.789 0.725 0.828 0.720 0.692 0.750 ; 0.796 0.748 0.832 0.695 0.663 0.731 ; 0.808 0.757 0.840 0.712 0.680 0.747
Other|LR|0.822 0.785 0.852 0.729 0.694 0.762 ; 0.804 0.750 0.845 0.749 0.721 0.781 ; 0.812 0.768 0.847 0.727 0.698 0.758 ; 0.828 0.784 0.858 0.740 0.708 0.774
Other|HGB|0.796 0.753 0.827 0.697 0.669 0.724 ; 0.785 0.751 0.819 0.722 0.700 0.745 ; 0.797 0.766 0.832 0.736 0.706 0.768 ; 0.803 0.767 0.832 0.732 0.706 0.765
Other|kNN|0.673 0.620 0.720 0.595 0.564 0.630 ; 0.671 0.623 0.716 0.625 0.599 0.657 ; 0.660 0.606 0.703 0.614 0.581 0.641 ; 0.615 0.563 0.670 0.606 0.577 0.636
Other|RF|0.790 0.750 0.824 0.732 0.700 0.761 ; 0.789 0.759 0.822 0.735 0.709 0.761 ; 0.782 0.745 0.816 0.746 0.722 0.778 ; 0.798 0.761 0.826 0.749 0.718 0.780
Scar|SVM|0.927 0.849 0.979 0.961 0.943 0.976 ; 0.948 0.895 0.977 0.947 0.916 0.973 ; 0.955 0.920 0.977 0.943 0.908 0.969 ; 0.942 0.892 0.973 0.953 0.924 0.976
Scar|LR|0.945 0.887 0.989 0.958 0.937 0.979 ; 0.964 0.926 0.986 0.955 0.923 0.977 ; 0.959 0.915 0.982 0.957 0.925 0.977 ; 0.952 0.910 0.982 0.957 0.934 0.978
Scar|HGB|0.925 0.861 0.974 0.938 0.911 0.961 ; 0.927 0.838 0.971 0.910 0.867 0.939 ; 0.928 0.876 0.963 0.930 0.892 0.956 ; 0.925 0.837 0.974 0.930 0.892 0.960
Scar|kNN|0.769 0.675 0.857 0.815 0.767 0.863 ; 0.781 0.683 0.864 0.816 0.759 0.854 ; 0.754 0.677 0.841 0.781 0.731 0.827 ; 0.737 0.661 0.820 0.768 0.718 0.822
Scar|RF|0.921 0.854 0.963 0.920 0.892 0.948 ; 0.923 0.833 0.968 0.897 0.844 0.932 ; 0.919 0.827 0.969 0.917 0.869 0.945 ; 0.920 0.843 0.967 0.928 0.888 0.957
Vascular Occlusion|SVM|0.913 0.834 0.968 0.935 0.889 0.978 ; 0.929 0.865 0.968 0.919 0.831 0.985 ; 0.913 0.824 0.975 0.932 0.870 0.982 ; 0.872 0.773 0.946 0.921 0.861 0.973
Vascular Occlusion|LR|0.923 0.853 0.967 0.943 0.906 0.980 ; 0.950 0.904 0.978 0.930 0.857 0.988 ; 0.917 0.833 0.970 0.943 0.886 0.985 ; 0.894 0.809 0.955 0.934 0.877 0.978
Vascular Occlusion|HGB|0.938 0.892 0.973 0.814 0.716 0.937 ; 0.949 0.914 0.990 0.878 0.800 0.960 ; 0.902 0.824 0.970 0.784 0.665 0.897 ; 0.794 0.653 0.907 0.791 0.693 0.902
Vascular Occlusion|kNN|0.833 0.714 0.934 0.778 0.679 0.906 ; 0.831 0.722 0.932 0.769 0.647 0.891 ; 0.808 0.683 0.906 0.732 0.645 0.820 ; 0.740 0.607 0.849 0.769 0.665 0.878
Vascular Occlusion|RF|0.941 0.863 0.990 0.902 0.826 0.966 ; 0.954 0.913 0.992 0.906 0.835 0.971 ; 0.920 0.840 0.987 0.934 0.887 0.973 ; 0.930 0.862 0.977 0.868 0.767 0.941
"""
TASKS = ["DR Staging (ICDR)", "Diabetic Retinopathy", "AMD", "Hemorrhage", "Hypertensive Retinopathy",
         "Increased Cup/Disc", "Macular Edema", "Myopic Fundus", "Nevus", "Other", "Scar", "Vascular Occlusion"]
ALGS, RES = ["SVM", "LR", "HGB", "kNN", "RF"], [224, 392, 672, 952]
T4 = {}
for line in TABLE4.strip().splitlines():
    tk, alg, cells = line.split("|")
    for r, c in zip(RES, cells.split(";")):
        v = [float(x) for x in c.split()]
        T4[(tk, alg, r)] = {"internal": v[0], "int_ci": v[1:3], "external": v[3], "ext_ci": v[4:6]}
assert len(T4) == 240
# Table 2: best classifier/resolution per task (selected by the authors on internal validation data)
TABLE2 = {"DR Staging (ICDR)": ("HGB", 392), "Scar": ("LR", 392), "Diabetic Retinopathy": ("LR", 672),
          "Hemorrhage": ("LR", 672), "AMD": ("LR", 952), "Nevus": ("LR", 952), "Other": ("LR", 952),
          "Hypertensive Retinopathy": ("RF", 392), "Macular Edema": ("RF", 392), "Vascular Occlusion": ("RF", 392),
          "Increased Cup/Disc": ("SVM", 392), "Myopic Fundus": ("SVM", 952)}
# Table 1 (image quality) and footnote 1 (refurbished prices)
INADEQ = {"Canon": 0.0879, "Nikon": 0.1860}
PRICE = {"Canon": 95000, "Nikon": 35000}
BINARY = [t for t in TASKS if t != "DR Staging (ICDR)"]


def pick(val, options, default):
    s = str(val).strip().lower()
    if not s or s.startswith("{{"):
        return default, False
    for o in options:
        if s == str(o).lower():
            return o, True
    for o in options:
        if s in str(o).lower() or str(o).lower().split()[0] in s:
            return o, True
    return default, False


ALIAS = {"dr": "Diabetic Retinopathy", "hr": "Hypertensive Retinopathy", "hypertensive": "Hypertensive Retinopathy",
         "cup": "Increased Cup/Disc", "glaucoma": "Increased Cup/Disc", "edema": "Macular Edema", "dme": "Macular Edema",
         "myopia": "Myopic Fundus", "rvo": "Vascular Occlusion", "occlusion": "Vascular Occlusion",
         "haemorrhage": "Hemorrhage", "staging": "DR Staging (ICDR)", "icdr": "DR Staging (ICDR)"}
caveats = []
traw = str(P.get("task", "Diabetic Retinopathy")).strip()
TASK = ALIAS.get(traw.lower()) or pick(traw, TASKS, None)[0]
if TASK is None:
    caveats.append(f"task '{traw}' not recognised; used Diabetic Retinopathy"); TASK = "Diabetic Retinopathy"
ALG, ok = pick(P.get("classifier", "best"), ALGS, TABLE2[TASK][0])
RESO = TABLE2[TASK][1]
try:
    rv = int(float(str(P.get("resolution", "best"))))
    RESO = rv if rv in RES else RESO
    if rv not in RES:
        caveats.append(f"resolution {rv} not in {RES}; used {RESO}")
except ValueError:
    pass
CONFIG_IS_TABLE2 = (ALG, RESO) == TABLE2[TASK]


def num(k, d, lo, hi):
    try:
        v = float(P.get(k, d))
    except (TypeError, ValueError):
        v = d
    if not lo <= v <= hi:
        caveats.append(f"{k}={v} clamped to [{lo}, {hi}]"); v = min(max(v, lo), hi)
    return v


BUDGET = num("budget_brl", 1900000, 35000, 100_000_000)
NSITES = int(num("n_sites", 40, 1, 500))
PPS = int(num("patients_per_site", 1000, 10, 100000))
PREV = num("prevalence_pct", 10, 0.1, 60) / 100
SPEC = num("specificity", 0.90, 0.5, 0.995)
RECAP = num("recapture_pct", 50, 0, 100) / 100
SHIFT = num("shift_strength", 1.0, 0, 3)
SEED = int(num("seed", 7, 0, 10**6))
CALC_TASK = TASK if TASK in BINARY else "Diabetic Retinopathy"
if TASK not in BINARY:
    caveats.append("DR Staging is scored with QWK, not AUROC; the screening calculator uses the binary "
                   "Diabetic Retinopathy task instead")
cell = T4[(TASK, ALG, RESO)]
ccell = T4[(CALC_TASK, ALG, RESO)]
log(f"task {TASK} | {ALG} @ {RESO}px: internal {cell['internal']:.3f} -> external {cell['external']:.3f}"
    f" ({'Table 2 selection' if CONFIG_IS_TABLE2 else 'custom configuration'})")

# ------------------------------------------------------------------ 1. explorer over the paper's Table 4
delta = {k: v["internal"] - v["external"] for k, v in T4.items()}
per_task = []
for t in TASKS:
    a, r = (ALG, RESO)
    v = T4[(t, a, r)]; v2 = T4[(t,) + TABLE2[t]]
    ds = [delta[(t, al, re)] for al in ALGS for re in RES]
    per_task.append({"task": t, "metric": "QWK" if t not in BINARY else "AUROC",
                     "internal": v["internal"], "external": v["external"], "delta": v["internal"] - v["external"],
                     "ci_overlap": not (v["ext_ci"][1] < v["int_ci"][0] or v["int_ci"][1] < v["ext_ci"][0]),
                     "table2": {"alg": TABLE2[t][0], "res": TABLE2[t][1], "internal": v2["internal"], "external": v2["external"]},
                     "delta_min": min(ds), "delta_max": max(ds), "delta_mean": float(np.mean(ds))})
fragile = sorted([p for p in per_task if p["task"] in BINARY], key=lambda p: -p["delta"])

# variance decomposition of the internal-external gap (11 binary tasks x 5 classifiers x 4 resolutions)
D = np.array([[[delta[(t, a, r)] for r in RES] for a in ALGS] for t in BINARY])
gm = D.mean()
ss = {"task": D.shape[1] * D.shape[2] * ((D.mean((1, 2)) - gm) ** 2).sum(),
      "classifier": D.shape[0] * D.shape[2] * ((D.mean((0, 2)) - gm) ** 2).sum(),
      "resolution": D.shape[0] * D.shape[1] * ((D.mean((0, 1)) - gm) ** 2).sum()}
ss_tot = ((D - gm) ** 2).sum(); ss["interactions/other"] = ss_tot - sum(ss.values())
var_share = {k: float(v / ss_tot) for k, v in ss.items()}
# does going from 224 to 952 px shrink the gap for the Table-2 classifier?
res_helps = [t for t in BINARY if delta[(t, TABLE2[t][0], 952)] < delta[(t, TABLE2[t][0], 224)] - 0.01]
res_hurts = [t for t in BINARY if delta[(t, TABLE2[t][0], 952)] > delta[(t, TABLE2[t][0], 224)] + 0.01]
# is there a classifier that removes the gap? best-case gap per task over all 20 configurations
best_case = {t: min(delta[(t, a, r)] for a in ALGS for r in RES) for t in BINARY}
lr_range = {t: [min(delta[(t, "LR", r)] for r in RES), max(delta[(t, "LR", r)] for r in RES)]
            for t in ["Hemorrhage", "Hypertensive Retinopathy"]}
log(f"variance of internal-external gap: task {var_share['task']:.0%}, classifier {var_share['classifier']:.0%}, "
    f"resolution {var_share['resolution']:.0%}")

# ------------------------------------------------------------------ 2. screening-program calculator


def sens_at(auc, spec):
    """Equal-variance binormal ROC: d' = sqrt(2) * z(AUC); sensitivity at a fixed specificity."""
    auc = min(max(auc, 0.5001), 0.9999)
    return ND.cdf(np.sqrt(2) * ND.inv_cdf(auc) - ND.inv_cdf(spec))


def site_rates(cam, auc):
    """Per screened patient: graded fraction, detection prob among diseased, false referrals."""
    g = 1 - INADEQ[cam] * (1 - RECAP)                 # inadequate images not recaptured are never graded
    se = sens_at(auc, SPEC)
    return {"graded": g, "sens": se, "detect_given_disease": g * se, "false_ref": (1 - PREV) * g * (1 - SPEC),
            "miss_given_disease": 1 - g * se}


def program(n_canon, n_nikon, auc_int, auc_ext):
    pts = {"Canon": n_canon * PPS, "Nikon": n_nikon * PPS}
    unc = (NSITES - n_canon - n_nikon) * PPS
    rc, rn = site_rates("Canon", auc_int), site_rates("Nikon", auc_ext)
    det = PREV * (pts["Canon"] * rc["detect_given_disease"] + pts["Nikon"] * rn["detect_given_disease"])
    diseased = PREV * NSITES * PPS
    ungr = pts["Canon"] * INADEQ["Canon"] + pts["Nikon"] * INADEQ["Nikon"]
    fr = pts["Canon"] * rc["false_ref"] + pts["Nikon"] * rn["false_ref"]
    return {"canon_sites": n_canon, "nikon_sites": n_nikon, "uncovered_sites": NSITES - n_canon - n_nikon,
            "cost_brl": n_canon * PRICE["Canon"] + n_nikon * PRICE["Nikon"], "screened": pts["Canon"] + pts["Nikon"],
            "unscreened": unc, "inadequate_images": ungr, "diseased": diseased, "detected": det, "missed": diseased - det,
            "missed_unscreened": PREV * unc, "false_referrals": fr}


def best_mix(budget, auc_int, auc_ext):
    best = None
    for c in range(0, min(NSITES, int(budget // PRICE["Canon"])) + 1):
        m = min(NSITES - c, int((budget - c * PRICE["Canon"]) // PRICE["Nikon"]))
        pr = program(c, m, auc_int, auc_ext)
        if best is None or pr["missed"] < best["missed"] - 1e-9:
            best = pr
    return best


def programs(budget, auc_int, auc_ext):
    return {"all_canon": program(min(NSITES, int(budget // PRICE["Canon"])), 0, auc_int, auc_ext),
            "all_nikon": program(0, min(NSITES, int(budget // PRICE["Nikon"])), auc_int, auc_ext),
            "best_mix": best_mix(budget, auc_int, auc_ext)}


AI, AE = ccell["internal"], ccell["external"]
progs = programs(BUDGET, AI, AE)
prog_lo = programs(BUDGET, ccell["int_ci"][0], ccell["ext_ci"][0])
prog_hi = programs(BUDGET, ccell["int_ci"][1], ccell["ext_ci"][1])
rc, rn = site_rates("Canon", AI), site_rates("Nikon", AE)
equity_ratio = rn["miss_given_disease"] / rc["miss_given_disease"]
# same calculator for every binary task (same classifier/resolution rule: Table 2 selection unless overridden)
all_tasks_calc = []
for t in BINARY:
    a, r = (ALG, RESO) if not CONFIG_IS_TABLE2 else TABLE2[t]
    v = T4[(t, a, r)]; pp = programs(BUDGET, v["internal"], v["external"])
    rc_t, rn_t = site_rates("Canon", v["internal"]), site_rates("Nikon", v["external"])
    all_tasks_calc.append({"task": t, "alg": a, "res": r, "missed_all_canon": pp["all_canon"]["missed"],
                           "missed_all_nikon": pp["all_nikon"]["missed"], "missed_best_mix": pp["best_mix"]["missed"],
                           "equity_ratio": rn_t["miss_given_disease"] / rc_t["miss_given_disease"],
                           "nikon_sens": rn_t["sens"], "canon_sens": rc_t["sens"]})
nikon_wins = [x["task"] for x in all_tasks_calc if x["missed_all_nikon"] < x["missed_all_canon"]]
budgets = np.linspace(0, NSITES * PRICE["Canon"] * 1.05, 60)
sweep = {k: [programs(b, AI, AE)[k]["missed"] for b in budgets] for k in ["all_canon", "all_nikon", "best_mix"]}
full_cov_nikon = NSITES * PRICE["Nikon"]; full_cov_canon = NSITES * PRICE["Canon"]
log(f"budget R${BUDGET:,.0f}: missed/yr all-Canon {progs['all_canon']['missed']:.0f}, all-Nikon "
    f"{progs['all_nikon']['missed']:.0f}, best mix {progs['best_mix']['missed']:.0f}; equity ratio {equity_ratio:.2f}")

# ------------------------------------------------------------------ 3. synthetic domain-shift demo
rng = np.random.default_rng(SEED)
DC, DA = 12, 36                                     # camera-sensitive ("colour/optics") vs anatomical feature dims
Qm, _ = np.linalg.qr(rng.normal(size=(DC, DC)))
u_cam = rng.normal(size=DC); u_cam /= np.linalg.norm(u_cam)
u_ana = rng.normal(size=DA); u_ana /= np.linalg.norm(u_ana)
mix = min(1.0, 0.6 * SHIFT)
A = (1 - mix) * np.eye(DC) + mix * Qm


def make(n, camera, frac, noise, r):
    y = (r.random(n) < 0.2).astype(int)
    X = r.normal(0, noise, (n, DC + DA))
    w = np.r_[np.sqrt(frac) * u_cam, np.sqrt(1 - frac) * u_ana]
    s = np.ones(n)
    field_fail = r.random(n) < (0.0476 if camera == "Canon" else 0.1584)   # Table 1 image-field rates
    s[field_fail] = 0.3                                                       # lesion partly outside the field
    X += (2.4 * y * s)[:, None] * w
    if camera == "Nikon":
        X[:, :DC] = X[:, :DC] @ A.T + 0.6 * SHIFT * r.normal(size=(n, DC)) + 0.8 * SHIFT
    return X, y


demo = []
fracs = np.linspace(0, 1, 11)
for label, noise in [("224 px (noisier features)", 1.0), ("952 px (cleaner features)", 0.7)]:
    for f in fracs:
        r = np.random.default_rng([SEED, int(noise * 10)])   # common random numbers across the sweep
        Xtr, ytr = make(3000, "Canon", f, noise, r); Xte, yte = make(2000, "Canon", f, noise, r)
        Xn, yn = make(4000, "Nikon", f, noise, r)
        clf = LogisticRegression(max_iter=500).fit(Xtr, ytr)
        demo.append({"resolution": label, "camera_sensitive_fraction": float(f),
                     "internal": float(roc_auc_score(yte, clf.decision_function(Xte))),
                     "external": float(roc_auc_score(yn, clf.decision_function(Xn)))})
log(f"synthetic demo: {len(demo)} train/test fits (shift strength {SHIFT})")

# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#868e96"

# fig 1: internal vs external per task (chosen classifier/resolution)
fig, ax = plt.subplots(figsize=(6.4, 4.0))
order = sorted(per_task, key=lambda p: p["delta"])
for i, p in enumerate(order):
    v = T4[(p["task"], ALG, RESO)]
    c = ACC if p["delta"] >= 0.05 else (BLUE if p["delta"] <= -0.02 else MUTED)
    ax.plot([v["internal"], v["external"]], [i, i], color=c, lw=2, alpha=0.7)
    ax.errorbar(v["internal"], i, xerr=[[v["internal"] - v["int_ci"][0]], [v["int_ci"][1] - v["internal"]]],
                fmt="o", mfc="white", mec=INK, ecolor=MUTED, ms=5, capsize=0, lw=0.8)
    ax.errorbar(v["external"], i, xerr=[[v["external"] - v["ext_ci"][0]], [v["ext_ci"][1] - v["external"]]],
                fmt="o", color=c, ecolor=c, ms=5, capsize=0, lw=0.8)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([("▶ " if p["task"] == TASK else "") + p["task"] + (" (QWK)" if p["metric"] == "QWK" else "")
                    for p in order], fontsize=8.5)
ax.set_xlabel(f"○ internal (Canon test) → ● external (Nikon)  ·  {ALG}, {RESO} px")
ax.axvline(0.5, color=MUTED, ls=":", lw=1)
fig.tight_layout(); fig.savefig(OUT / "fig_tasks.png", dpi=160); plt.close(fig)

# fig 2: gap heatmap over all 220 binary configurations
fig, ax = plt.subplots(figsize=(6.4, 3.6))
M = np.array([[delta[(t, a, r)] for a in ALGS for r in RES] for t in BINARY])
im = ax.imshow(M, cmap="RdBu_r", vmin=-0.3, vmax=0.3, aspect="auto")
ax.set_yticks(range(len(BINARY))); ax.set_yticklabels(BINARY, fontsize=8)
ax.set_xticks(range(20)); ax.set_xticklabels([str(r) for a in ALGS for r in RES], fontsize=6.5, rotation=90)
for j, a in enumerate(ALGS):
    ax.text(j * 4 + 1.5, -0.9, a, ha="center", fontsize=8.5, fontweight="bold")
    if j:
        ax.axvline(j * 4 - 0.5, color="white", lw=2)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("internal − external AUROC", fontsize=8)
ax.set_xlabel("classifier × input resolution (px)")
fig.tight_layout(); fig.savefig(OUT / "fig_gap_heatmap.png", dpi=160); plt.close(fig)

# fig 3: missed referrals vs budget
fig, ax = plt.subplots(figsize=(6.4, 3.5))
bk = budgets / 1e6
ax.plot(bk, sweep["all_canon"], color=INK, lw=2, label="all Canon CR-2 (R$95k each)")
ax.plot(bk, sweep["all_nikon"], color=ACC, lw=2, label="all Nikon NF5050 (R$35k each)")
ax.plot(bk, sweep["best_mix"], color=BLUE, lw=1.5, ls="--", label="best mix")
ax.axvline(BUDGET / 1e6, color=MUTED, ls=":", lw=1.2); ax.text(BUDGET / 1e6, ax.get_ylim()[1] * 0.99, " your budget", fontsize=8, va="top", color=MUTED)
ax.set_xlabel("Equipment budget (R$ millions)"); ax.set_ylabel("Missed referable cases / year")
ax.set_title(f"{CALC_TASK}: {NSITES} sites × {PPS:,} patients, prevalence {100 * PREV:g}%, spec {SPEC:.2f}", fontsize=9)
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
fig.tight_layout(); fig.savefig(OUT / "fig_program.png", dpi=160); plt.close(fig)

# fig 4: synthetic demo
fig, ax = plt.subplots(figsize=(6.4, 3.0))
for label, ls in [("224 px (noisier features)", "-"), ("952 px (cleaner features)", "--")]:
    rows = [d for d in demo if d["resolution"] == label]
    xs = [d["camera_sensitive_fraction"] for d in rows]
    ax.plot(xs, [d["internal"] for d in rows], ls, color=INK, lw=1.5, label=f"internal (Canon) · {label}")
    ax.plot(xs, [d["external"] for d in rows], ls, color=ACC, lw=1.8, label=f"external (Nikon) · {label}")
ax.set_xlabel("Share of the disease signal carried by camera-sensitive (colour/optical) features")
ax.set_ylabel("AUROC (synthetic)"); ax.set_ylim(0.45, 1.0); ax.axhline(0.5, color=MUTED, ls=":", lw=1)
ax.legend(frameon=False, fontsize=7, loc="lower left")
fig.tight_layout(); fig.savefig(OUT / "fig_shift_demo.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ results + card
ac, an, bm = progs["all_canon"], progs["all_nikon"], progs["best_mix"]
res = {"params": P, "caveats_from_inputs": caveats, "task": TASK, "calculator_task": CALC_TASK, "classifier": ALG,
       "resolution": RESO, "config_is_table2": CONFIG_IS_TABLE2,
       "selected": {"internal": cell["internal"], "external": cell["external"], "delta": cell["internal"] - cell["external"],
                    "int_ci": cell["int_ci"], "ext_ci": cell["ext_ci"]},
       "per_task": per_task, "most_fragile_task": fragile[0]["task"], "most_fragile_delta": fragile[0]["delta"],
       "gap_variance_share": var_share, "resolution_952_vs_224_shrinks_gap": res_helps,
       "resolution_952_vs_224_widens_gap": res_hurts, "best_case_gap_any_config": best_case,
       "lr_gap_range_hemorrhage_hypertensive": lr_range,
       "constants": {"inadequate_canon": INADEQ["Canon"], "inadequate_nikon": INADEQ["Nikon"],
                     "price_canon_brl": PRICE["Canon"], "price_nikon_brl": PRICE["Nikon"],
                     "price_ratio": PRICE["Canon"] / PRICE["Nikon"], "inadequacy_ratio": INADEQ["Nikon"] / INADEQ["Canon"]},
       "calculator": {"budget_brl": BUDGET, "n_sites": NSITES, "patients_per_site": PPS, "prevalence": PREV,
                      "specificity": SPEC, "recapture": RECAP, "auroc_canon_sites": AI, "auroc_nikon_sites": AE,
                      "canon_site": rc, "nikon_site": rn, "equity_miss_ratio": equity_ratio,
                      "programs": progs, "programs_ci_low": prog_lo, "programs_ci_high": prog_hi,
                      "missed_saved_nikon_vs_canon": ac["missed"] - an["missed"],
                      "full_coverage_cost_nikon": full_cov_nikon, "full_coverage_cost_canon": full_cov_canon},
       "all_tasks_calculator": all_tasks_calc, "tasks_where_all_nikon_misses_fewer": nikon_wins,
       "synthetic_demo": demo, "shift_strength": SHIFT}
better = "all-Nikon" if an["missed"] < ac["missed"] else "all-Canon"
tiles = [
    {"label": f"{TASK}: Canon → Nikon", "value": f"{cell['internal']:.3f} → {cell['external']:.3f}",
     "sub": f"{'QWK' if TASK not in BINARY else 'AUROC'}, {ALG} @ {RESO} px (paper Table 4); "
            f"gap {cell['internal'] - cell['external']:+.3f}", "tone": "warn" if cell["internal"] - cell["external"] >= 0.05 else "good"},
    {"label": "Missed cases / yr: all-Canon vs all-Nikon", "value": f"{ac['missed']:,.0f} vs {an['missed']:,.0f}",
     "sub": f"R${BUDGET / 1e6:.2f}M buys {ac['canon_sites']} Canon or {an['nikon_sites']} Nikon sites of {NSITES} "
            f"({CALC_TASK})", "tone": "accent"},
    {"label": "Equity gap at Nikon sites", "value": f"{equity_ratio:.2f}×",
     "sub": f"risk that a diseased patient is missed at a Nikon vs a Canon site: {100 * rn['miss_given_disease']:.0f}% vs "
            f"{100 * rc['miss_given_disease']:.0f}% (sensitivity {rn['sens']:.2f} vs {rc['sens']:.2f} at spec {SPEC:.2f}; "
            f"{100 * INADEQ['Nikon']:.2f}% vs {100 * INADEQ['Canon']:.2f}% inadequate images)",
     "tone": "warn" if equity_ratio > 1.2 else "neutral"},
    {"label": "What drives the gap?", "value": f"task {100 * var_share['task']:.0f}%",
     "sub": f"share of variance in the internal−external gap across 220 configurations; classifier "
            f"{100 * var_share['classifier']:.0f}%, resolution {100 * var_share['resolution']:.0f}%", "tone": "neutral"},
]
t2 = T4[(TASK,) + TABLE2[TASK]]
compare = [
    {"metric": f"{TASK} internal → external (Table 2: {TABLE2[TASK][0]}, {TABLE2[TASK][1]} px)",
     "paper": f"{t2['internal']:.3f} → {t2['external']:.3f}",
     "yours": f"{cell['internal']:.3f} → {cell['external']:.3f} ({ALG}, {RESO} px)",
     "note": "transcribed, not recomputed" + ("" if CONFIG_IS_TABLE2 else "; your configuration differs from Table 2")},
    {"metric": "Inadequate images, Canon vs Nikon (Table 1)", "paper": "8.79% vs 18.60%", "yours": "8.79% vs 18.60%",
     "note": "calculator input; discussion rounds to 8.8% vs 18.6%"},
    {"metric": "Image-field abnormality, Nikon", "paper": "15.84% (Table 1) / 16.5% (text)", "yours": "15.84% (used in demo)",
     "note": "paper is internally inconsistent"},
    {"metric": "Illumination Cramér's V", "paper": "0.028 (Table 1) / 0.023 (text)", "yours": "—", "note": "inconsistent in paper; not used"},
    {"metric": "Camera price ratio", "paper": "\"approximately half\" (abstract); \"1.5 times more\" (intro); R$95,000 vs R$35,000",
     "yours": f"{PRICE['Canon'] / PRICE['Nikon']:.2f}× (from the quoted prices)", "note": "calculator uses the prices"},
    {"metric": "Hemorrhage / hypertensive ΔAUROC (LR, all resolutions)", "paper": "∆ AUROC=0.15–0.28 (Fig. 2 caption)",
     "yours": f"{min(lr_range['Hemorrhage'][0], lr_range['Hypertensive Retinopathy'][0]):.3f}–"
              f"{max(lr_range['Hemorrhage'][1], lr_range['Hypertensive Retinopathy'][1]):.3f} from Table 4",
     "note": "hemorrhage at 952 px is 0.134"},
    {"metric": "Resolution / classifier fix the gap?", "paper": "neither ... consistently mitigated cross-camera variation",
     "yours": f"952 vs 224 px shrinks the gap for {len(res_helps)}/11 tasks, widens it for {len(res_hurts)}/11",
     "note": "Table-2 classifier per task"},
]
Path(OUT / "card_data.json").write_text(json.dumps({
    "paper": {"num": 6, "title": "From Canon to Nikon: Camera Domain Shift and Potential Equity Implications in Retinal AI",
              "authors": "Lisa Y.W. Tang", "url": "https://drive.google.com/file/d/1cEMU7Sho9vz6uA6rD2xq78R9KDpaOwuK/view?usp=sharing", "affiliation": ""},
    "inputs": {"task": TASK, "classifier @ resolution": f"{ALG} @ {RESO} px", "budget": f"R${BUDGET:,.0f}",
               "sites × patients/yr": f"{NSITES} × {PPS:,}", "prevalence": f"{100 * PREV:g}%", "specificity": SPEC,
               "re-imaged if inadequate": f"{100 * RECAP:g}%", "synthetic shift": SHIFT},
    "tiles": tiles,
    "figures": [{"path": "fig_tasks.png", "title": "Which tasks survive the camera change?",
                 "caption": "The paper's own internal (Canon) and external (Nikon) estimates with 95% bootstrap CIs. "
                            "Orange = external drops ≥ 0.05; blue = external is higher (different case mix). ▶ = your task."},
                {"path": "fig_gap_heatmap.png", "title": "Does a different classifier or resolution fix it?",
                 "caption": "Internal − external AUROC for all 220 binary configurations in Table 4. Rows (tasks) differ far "
                            "more than columns (classifier × resolution)."},
                {"path": "fig_program.png", "title": "Your screening program: coverage vs camera quality",
                 "caption": "Missed referable cases per year (unscreened + ungradable + false negatives). Canon sites use the "
                            "internal AUROC, Nikon sites the external one. A modelling illustration built on the paper's numbers."},
                {"path": "fig_shift_demo.png", "title": "Why some tasks break: a synthetic mechanism",
                 "caption": "Simulated embeddings (not RETFound-Green). The Nikon 'camera' remixes colour/optical features. "
                            "Tasks whose signal lives there degrade; cleaner (higher-resolution) features lift both lines but keep the gap."}],
    "compare": compare, "runbook": {"name": "smash-06-canon-to-nikon", "url": P.get("runbook_url", "")}}, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: {TASK} {cell['internal']:.3f}->{cell['external']:.3f}; missed/yr Canon {ac['missed']:.0f} vs Nikon "
    f"{an['missed']:.0f} vs best mix {bm['missed']:.0f} ({bm['canon_sites']}C+{bm['nikon_sites']}N); "
    f"equity ratio {equity_ratio:.2f}; most fragile {fragile[0]['task']} ({fragile[0]['delta']:.3f})")
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
