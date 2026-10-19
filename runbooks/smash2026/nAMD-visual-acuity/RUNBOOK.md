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
    skill_name: smash-05-namd-visual-acuity
    confidence: high
---

# Will This Eye Gain 10 Letters? A Glass-Box nAMD Prognosis You Can Read (SMASH 2026 · Paper #5)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Visual Acuity Improvement Prediction in Neovascular Age-Related Macular Degeneration"** (Hadi Moazen, Mélanie Hébert, Alaa Eddine Ayadi, Ali Dirani, Audrey Durand).
Read the paper: https://drive.google.com/file/d/1h81k0dJvGwdnHFxP-kYIcjuwFZgX_n1d/view

The paper's claim: instead of an end-to-end deep network on OCT scans, **extract clinical OCT biomarkers automatically
with deep learning** (CST, SRF, IRF/IRC, PED, VMT), add baseline best-corrected visual acuity (BCVA), and feed them to an
**Explainable Boosting Machine (EBM)**, a glass-box additive model. This predicts a ≥ 10-letter gain one year after
anti-VEGF loading better than end-to-end ResNet18 (AUC 0.77 vs 0.57), matches an EBM trained on human-measured
biomarkers, and lets physicians read exactly why each prediction was made.

The participant describes **their own hypothetical patient** (baseline BCVA, CST, and which fluid/structure biomarkers
are present) and chooses how error-prone the automated extraction is. The run builds a **simulated** cohort matching
the paper's reported marginals, fits the glass box (EBM) on measured and on automated (noisy) biomarkers plus a
gradient-boosting black box with 5-fold CV, then explains the participant's patient term by term and shows **how much
the prediction moves if the automated pipeline misreads one biomarker**. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment takes about 10–20 s.

**The CHU de Québec cohort is private. Every patient in this run is simulated; effects are hand-specified and
plausible, not estimated from the authors' data. Simulated data. Not for clinical use, not for counselling a real
patient.**

### How the simulation is built
- Marginals from the paper (§2), n = 1203 eyes: BCVA 64 [53, 70] letters (quantile-matched), CST 289 [245, 349] µm
  (lognormal), SRF 43%, IRF 34%, PED 48%, VMT 17%; biomarkers mildly correlated with CST; IRF and thick CST go with
  worse BCVA.
- Outcome (assumed mechanism): 1-year letter gain = intercept + more room to gain at lower BCVA (plateau below 45 letters)
  + SRF (favourable) − IRF − PED − VMT + thicker CST (slightly favourable) + a CST × BCVA interaction + a 30% "strong
  responder" subgroup + noise, with a ceiling on achievable BCVA. The intercept is calibrated so 25% gain ≥ 10 letters.
- "Automated" biomarkers: each binary biomarker is flipped with probability (1 − the paper's extraction accuracy) ×
  `automation_error_scale` (accuracies SRF 0.91, IRF/IRC 0.88, PED 0.89, VMT 0.82); CST gets Gaussian error `cst_error_um`.
- Models (paper §3–4): EBM (`interpret-core`, 5 pairwise interactions, 8 outer bags) on measured and on automated
  biomarkers; scikit-learn histogram gradient boosting as a stand-in for XGBoost; a BCVA-only logistic regression as a
  floor. 5-fold stratified CV; the decision threshold is the training prevalence (equivalent to class-weighting).
  If `interpret` cannot be installed, the script falls back to a transparent binned additive logistic model (the card
  then says "Additive GAM"). The end-to-end ResNet18 baseline needs OCT images and is not reproduced.

### Paper headline numbers (quote exactly)
- Table 1 (≥ 10-letter gain at one year): ResNet18 AUC **0.57 ± 0.05** (sensitivity 0.15 ± 0.04); XGBoost
  **0.74 ± 0.06** (sens 0.73 ± 0.01, spec 0.63 ± 0.04, F1 0.53 ± 0.03); EBM **0.77 ± 0.07** (sens 0.75 ± 0.08,
  spec 0.61 ± 0.03, F1 0.54 ± 0.02, accuracy 0.65 ± 0.03).
- EBM on human-measured biomarkers: AUC = 0.77, the same as on automated biomarkers (Figure 2b).
- Biomarker extraction accuracy: SRF 0.91, IRF/IRC 0.88, PED 0.89, VMT 0.82; CST "average error of 0.1437 µm".
- Most important predictors: "baseline VA, CST, and the interaction between these two features"; improvement starts to
  decline above 50 letters, with a sharp drop above 75 (ceiling effect).
- Cohort: 1203 eyes; 299 (25%) gained ≥ 10 letters; median gain 2 [-3, 10]; BCVA at one year 68 [57, 76].
- Internal inconsistencies worth knowing: XGBoost AUC is 0.74 in Table 1 but 0.75 in the Figure 2a legend; the CST
  error of 0.1437 µm is implausibly small for OCT (the text also says CST is measured "in nanometers"), so this
  runbook uses a participant-set CST error (default 20 µm); "2.67 times more patients who did not see an improvement"
  implies ~27% improvers, vs 25% reported.

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
| Patient: baseline BCVA | `{{patient_bcva}}` | `50` | Your hypothetical patient's baseline acuity in ETDRS letters (cohort median 64) |
| Patient: CST | `{{patient_cst}}` | `380` | Central subfield thickness in µm (cohort median 289) |
| Patient: SRF | `{{patient_srf}}` | `1` | Subretinal fluid present (1) or absent (0) |
| Patient: IRF/IRC | `{{patient_irf}}` | `1` | Intraretinal fluid / cysts present (1) or absent (0) |
| Patient: PED | `{{patient_ped}}` | `0` | Pigment epithelial detachment present (1) or absent (0) |
| Patient: VMT | `{{patient_vmt}}` | `0` | Vitreomacular adhesion/traction present (1) or absent (0) |
| Automation error scale | `{{automation_error_scale}}` | `1` | Multiplies the paper's biomarker error rates (0 = perfect extraction, 1 = paper, 3 = much worse) |
| CST error | `{{cst_error_um}}` | `20` | SD of the automated CST measurement error in µm |
| Cohort size | `{{n_patients}}` | `1203` | Simulated eyes (paper: 1203) |
| Seed | `{{seed}}` | `5` | Random seed |

## Dependencies

numpy, scikit-learn, matplotlib (preinstalled in `python312-uv`) plus **interpret-core** (the EBM; one ~15 MB wheel).
No data downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, sklearn, matplotlib" 2>/dev/null || uv pip install --system -q numpy scikit-learn matplotlib
python -c "from interpret.glassbox import ExplainableBoostingClassifier" 2>/dev/null || uv pip install --system -q interpret-core
python -c "from interpret.glassbox import ExplainableBoostingClassifier; print('EBM OK')" || echo "EBM unavailable: the script will use its transparent fallback"
```

Write `/app/work/params.json` (JSON numbers; if a value still looks like an unsubstituted `{{…}}` placeholder use the
table default):

```json
{"patient_bcva": {{patient_bcva}}, "patient_cst": {{patient_cst}}, "patient_srf": {{patient_srf}},
 "patient_irf": {{patient_irf}}, "patient_ped": {{patient_ped}}, "patient_vmt": {{patient_vmt}},
 "automation_error_scale": {{automation_error_scale}}, "cst_error_um": {{cst_error_um}},
 "n_patients": {{n_patients}}, "seed": {{seed}}, "runbook_url": ""}
```

Validate before running: clamp `patient_bcva` to [5, 88], `patient_cst` to [150, 700]; biomarkers must be 0 or 1
(round anything else); clamp `automation_error_scale` to [0, 4], `cst_error_um` to [0, 150], `n_patients` to
[300, 5000]. Record any correction as a caveat.

## Step 2: Get the code (extract it, don't retype it)

The tested implementation of the method is embedded in the **Appendix** at the end of this runbook. Do not
rewrite, "improve", or re-derive it. **Always run the command below first, exactly as written.** It copies the
files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is
far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it
won't work: run it and read its output.

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
environment problems (missing package, network retry), never the methodology.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 240 python experiment.py params.json {{results_dir}}
```

Expected: 10–20 s. Ends with a `done:` line (patient probability, the four AUCs, the most damaging misread).

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): this run's most striking result with 1–2 numbers copied from `results.json`, usually the
  patient's predicted chance (`patient.p_gain_10plus`, as a %) and how far one misread biomarker moves it
  (`patient.worst_misread`). Say "simulated" in the headline.
- **idea**: (1) extract interpretable OCT biomarkers automatically instead of predicting end-to-end from images;
  (2) a glass-box additive model (EBM) keeps the physician able to check every term; (3) automated biomarkers predict
  as well as human-measured ones in the paper.
- **findings**: (1) the patient: probability, the largest contributions from `patient.contributions` (logits; positive =
  towards a ≥ 10-letter gain) and what they mean clinically (e.g. lower baseline BCVA = more room to gain);
  `similar_observed_rate` if not null; (2) misreads: which biomarker error moves the prediction most and by how much;
  (3) the models: glass box on automated vs measured vs gradient boosting vs BCVA alone (`models`, AUC mean ± SD) vs
  the paper's Table 1; note when the margin over BCVA-alone is small; (4) the BCVA shape function vs the paper's
  Figure 3b. Be explicit that the effects were specified by the simulation, so the model "recovering" them is a
  demonstration of interpretability, not evidence about real patients.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `patient_bcva, patient_cst, patient_srf,
  patient_irf, patient_ped, patient_vmt, automation_error_scale, cst_error_um, n_patients, seed`. Good contrasts: a
  patient near the ceiling (`patient_bcva` 78); a much worse extraction pipeline (`automation_error_scale` 3); perfect
  extraction (`automation_error_scale` 0, `cst_error_um` 0).
- **caveats** (2–4): simulated cohort with hand-specified effects (only the marginals come from the paper); not for
  clinical use; the end-to-end ResNet18 and the real DL extraction pipeline are not run (extraction errors are simulated
  from the reported accuracies); the CST error is the participant's setting because the paper's 0.1437 µm looks like a
  units slip.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: patient, predicted chance, top contributions, worst misread, AUC table,
headline, "simulated, not for clinical use").

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
python3 - "{{results_dir}}" 240 <<'PY'
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
python3 - "{{results_dir}}" "patient_bcva,patient_cst,patient_srf,patient_irf,patient_ped,patient_vmt,automation_error_scale,cst_error_um,n_patients,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} patient_bcva,patient_cst,patient_srf,patient_irf,patient_ped,patient_vmt,automation_error_scale,cst_error_um,n_patients,seed 240 checklist.json
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
"""Glass-box nAMD prognosis lab — SMASH 2026 paper #5 (Moazen, Ayadi, Durand, Hébert, Dirani).

The paper predicts a >= 10-letter visual-acuity gain one year after anti-VEGF loading in neovascular AMD from
baseline BCVA plus five OCT biomarkers (CST, SRF, IRF/IRC, PED, VMT) extracted automatically by deep-learning
models, using an Explainable Boosting Machine (EBM) so physicians can inspect every feature's contribution.

The CHU de Québec cohort is private. This script SIMULATES a cohort of 1,203 eyes whose marginals match the paper
(BCVA 64 [53, 70], CST 289 [245, 349] µm, SRF 43%, IRF 34%, PED 48%, VMT 17%, 25% gaining >= 10 letters) with
plausible, hand-specified effects, then:
  1. fits an EBM on the "human-measured" biomarkers and on "automated" biomarkers (corrupted at the paper's
     extraction accuracies), plus a gradient-boosting black box (stand-in for XGBoost), all with 5-fold CV;
  2. shows the EBM's global importances and baseline-BCVA shape function;
  3. explains the participant's own hypothetical patient term by term (waterfall) and shows how much the
     prediction moves if the automated pipeline misreads one biomarker.
SIMULATED DATA. NOT FOR CLINICAL USE.

usage: python experiment.py params.json outdir
"""
import json, sys, time, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.ensemble import HistGradientBoostingClassifier

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SEED = int(P["seed"]); rng = np.random.default_rng(SEED)
N = int(P["n_patients"]); ERR = float(P["automation_error_scale"]); CST_ERR = float(P["cst_error_um"])
FEATS = ["BCVA", "CST", "SRF", "IRF", "PED", "VMT"]
PREV = {"SRF": .43, "IRF": .34, "PED": .48, "VMT": .17}       # paper §2
ACC = {"SRF": .91, "IRF": .88, "PED": .89, "VMT": .82}         # paper §4.1, automated extraction accuracy
PATIENT = np.array([[float(P["patient_bcva"]), float(P["patient_cst"])] +
                    [float(int(P[f"patient_{k.lower()}"])) for k in ["SRF", "IRF", "PED", "VMT"]]])

try:
    from interpret.glassbox import ExplainableBoostingClassifier
    HAVE_EBM = True
except Exception:                     # transparent fallback: binned additive logistic model (stated on the card)
    HAVE_EBM = False


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def ndtri(p):
    """Inverse standard-normal CDF (Acklam's rational approximation; scalar p in (0, 1))."""
    a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.3577518672690, -30.66479806614716, 2.506628277459239]
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
    if p < 0.02425:
        q = np.sqrt(-2 * np.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - 0.02425:
        return -ndtri(1 - p)
    q = p - 0.5; r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def mean_gain(va, cst, srf, irf, ped, vmt):
    """Hand-specified (assumed) expected 1-year letter gain: more room to gain at lower BCVA (plateau below 45),
    SRF favourable, IRF/PED/VMT unfavourable, thicker CST slightly favourable, CST x BCVA interaction."""
    return (0.4 * (60 - np.maximum(va, 45)) + 4 * srf - 3 * irf - 1.5 * ped - 2 * vmt
            + 0.015 * (cst - 289) + 0.0006 * (cst - 289) * (60 - va))


def cohort(n, r, c0):
    zc = r.standard_normal(n)
    load = np.array([.35, .3, .2, 0.0])                                   # biomarker <-> CST association (assumed)
    lat = zc[:, None] * load + r.standard_normal((n, 4)) * np.sqrt(1 - load ** 2)
    srf, irf, ped, vmt = [(lat[:, j] > ndtri(1 - PREV[k])).astype(float) for j, k in enumerate(PREV)]
    cst = 289 * np.exp(0.262 * zc)                                        # lognormal: quartiles ~245 / 289 / 345
    u_va = -0.25 * zc - 0.35 * lat[:, 1] + r.standard_normal(n)           # thicker retina, IRF -> worse BCVA
    u = (np.argsort(np.argsort(u_va)) + 0.5) / n
    va = np.round(np.interp(u, [0, .01, .05, .25, .5, .75, .95, .99, 1], [5, 20, 35, 53, 64, 70, 78, 83, 88]))
    resp = r.random(n) < 0.3                                              # a subgroup of strong responders
    final = np.minimum(va + c0 + mean_gain(va, cst, srf, irf, ped, vmt) + 7 * r.standard_normal(n) + 9.5 * resp,
                       88 + 3 * r.standard_normal(n))                     # ceiling on achievable BCVA
    gain = final - va
    return np.c_[va, cst, srf, irf, ped, vmt], gain, final


# calibrate the intercept so that 25% of eyes gain >= 10 letters (paper: 299 (25%))
lo, hi = -15.0, 15.0
for _ in range(30):
    mid = (lo + hi) / 2; _, g, _ = cohort(100_000, np.random.default_rng(12345), mid)
    lo, hi = (mid, hi) if (g >= 10).mean() < 0.25 else (lo, mid)
C0 = (lo + hi) / 2
X, gain, final = cohort(N, rng, C0)
y = (gain >= 10).astype(int)
q = lambda v: [float(x) for x in np.percentile(v, [50, 25, 75])]
log(f"synthetic cohort n={N}: BCVA {q(X[:, 0])}, CST {np.round(q(X[:, 1]), 0).tolist()}, gain {np.round(q(gain), 1).tolist()}, "
    f">=10 letters {100 * y.mean():.1f}%")


def automate(Xin, r):
    """Corrupt biomarkers as an automated extraction pipeline would: binary flips at (1 - accuracy) x scale,
    CST with Gaussian error of cst_error_um."""
    Xa = Xin.copy()
    for j, k in enumerate(["SRF", "IRF", "PED", "VMT"], start=2):
        flip = r.random(len(Xa)) < min(0.5, (1 - ACC[k]) * ERR)
        Xa[flip, j] = 1 - Xa[flip, j]
    Xa[:, 1] = Xa[:, 1] + CST_ERR * r.standard_normal(len(Xa))
    return Xa


Xa = automate(X, np.random.default_rng(SEED + 7))
flip_rate = {k: float((Xa[:, j] != X[:, j]).mean()) for j, k in enumerate(FEATS) if j >= 2}


class BinnedGAM:
    """Fallback glass box: one-hot quantile bins per feature + BCVA x CST bins, L2 logistic regression."""
    def fit(self, Xf, yf):
        from sklearn.linear_model import LogisticRegression
        self.edges = [np.unique(np.quantile(Xf[:, j], np.linspace(0, 1, 11))[1:-1]) if j < 2 else np.array([0.5]) for j in range(Xf.shape[1])]
        self.m = LogisticRegression(C=1.0, max_iter=2000).fit(self._z(Xf), yf); return self

    def _z(self, Xf):
        cols = []
        for j, e in enumerate(self.edges):
            b = np.digitize(Xf[:, j], e); cols.append(np.eye(len(e) + 1)[b])
        bi = np.digitize(Xf[:, 0], self.edges[0][::3]) * 10 + np.digitize(Xf[:, 1], self.edges[1][::3])
        cols.append((bi[:, None] == np.arange(100)).astype(float))
        return np.hstack(cols)

    def predict_proba(self, Xf):
        return self.m.predict_proba(self._z(Xf))


def make_glassbox():
    if HAVE_EBM:
        return ExplainableBoostingClassifier(feature_names=FEATS, interactions=5, outer_bags=8, random_state=SEED)
    return BinnedGAM()


def cv(model_fn, Xf):
    """5-fold CV (paper: 5-fold). Threshold = training prevalence (equivalent to class-weighting the loss)."""
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED); pred = np.zeros(len(y)); per = []
    for tr, te in skf.split(Xf, y):
        m = model_fn().fit(Xf[tr], y[tr]); p = m.predict_proba(Xf[te])[:, 1]; pred[te] = p
        yhat = p >= y[tr].mean(); yt = y[te]
        tp = (yhat & (yt == 1)).sum(); fp = (yhat & (yt == 0)).sum(); fn = (~yhat & (yt == 1)).sum(); tn = (~yhat & (yt == 0)).sum()
        per.append({"auc": roc_auc_score(yt, p), "acc": (tp + tn) / len(yt), "sens": tp / max(tp + fn, 1),
                    "spec": tn / max(tn + fp, 1), "f1": 2 * tp / max(2 * tp + fp + fn, 1)})
    agg = {k: [float(np.mean([d[k] for d in per])), float(np.std([d[k] for d in per]))] for k in per[0]}
    return agg, pred


models = {}
GBN = "EBM" if HAVE_EBM else "Additive GAM"
K_MEAS, K_AUTO = f"{GBN}, measured biomarkers", f"{GBN}, automated biomarkers (proposed)"
models[K_MEAS] = cv(make_glassbox, X)
log(f"{GBN} measured: AUC {models[K_MEAS][0]['auc'][0]:.3f}")
models[K_AUTO] = cv(make_glassbox, Xa)
log(f"{GBN} automated: AUC {models[K_AUTO][0]['auc'][0]:.3f}")
models["Gradient boosting, automated"] = cv(lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                                                   random_state=SEED), Xa)
models["BCVA only (logistic)"] = cv(lambda: __import__("sklearn.linear_model", fromlist=["x"]).LogisticRegression(), X[:, :1])
log("cross-validation finished: " + "; ".join(f"{k} {v[0]['auc'][0]:.3f}" for k, v in models.items()))

# ---------------------------------------------------------------- final glass box (proposed pipeline) + patient
gb = make_glassbox().fit(Xa, y)
p_patient = float(gb.predict_proba(PATIENT)[0, 1])
if HAVE_EBM:
    ex = gb.explain_local(PATIENT).data(0)
    contrib = [(n, float(s)) for n, s in zip(ex["names"], ex["scores"])]
    intercept = float(np.ravel(gb.intercept_)[0])
    importances = sorted(zip(gb.term_names_, [float(v) for v in gb.term_importances()]), key=lambda t: -t[1])
    gx = np.arange(5, 89); grid = np.repeat(np.median(Xa, 0)[None], len(gx), 0); grid[:, 0] = gx
    exg = gb.explain_local(grid); jb = list(gb.term_names_).index("BCVA")
    shape = [float(exg.data(i)["scores"][jb]) for i in range(len(gx))]          # BCVA main-effect term only
else:
    base = gb.predict_proba(np.median(Xa, 0)[None])[0, 1]; intercept = float(np.log(base / (1 - base)))
    contrib = []
    for j, n in enumerate(FEATS):
        z = np.median(Xa, 0)[None].copy(); z[0, j] = PATIENT[0, j]; pz = gb.predict_proba(z)[0, 1]
        contrib.append((n, float(np.log(pz / (1 - pz)) - intercept)))
    importances = sorted([(n, abs(c)) for n, c in contrib], key=lambda t: -t[1])
    gx = np.arange(5, 89); grid = np.repeat(np.median(Xa, 0)[None], len(gx), 0); grid[:, 0] = gx
    pg = gb.predict_proba(grid)[:, 1]; shape = [float(v) for v in np.log(pg / (1 - pg)) - intercept]
logit = intercept + sum(c for _, c in contrib)

# what if the automated pipeline misreads one of this patient's biomarkers?
misread = []
for j, k in enumerate(["SRF", "IRF", "PED", "VMT"], start=2):
    z = PATIENT.copy(); z[0, j] = 1 - z[0, j]
    misread.append({"biomarker": k, "read_as": int(z[0, j]), "p": float(gb.predict_proba(z)[0, 1])})
for d in (-CST_ERR * 2, CST_ERR * 2):
    z = PATIENT.copy(); z[0, 1] += d
    misread.append({"biomarker": f"CST {'+' if d > 0 else '−'}{abs(d):.0f} µm", "read_as": float(z[0, 1]), "p": float(gb.predict_proba(z)[0, 1])})
worst_mis = max(misread, key=lambda m: abs(m["p"] - p_patient))
# similar synthetic patients: observed rate among neighbours (sanity check for the participant's prediction)
nb = (np.abs(X[:, 0] - PATIENT[0, 0]) <= 5) & (np.abs(X[:, 1] - PATIENT[0, 1]) <= 50)
nb_rate = float(y[nb].mean()) if nb.sum() >= 30 else None

res = {"params": P, "glassbox": "EBM (interpret)" if HAVE_EBM else "binned additive logistic (fallback)",
       "intercept_c0": C0, "cohort": {"n": N, "bcva_median_iqr": q(X[:, 0]), "cst_median_iqr": q(X[:, 1]),
       "prevalence": {k: float(X[:, j].mean()) for j, k in enumerate(FEATS) if j >= 2},
       "gain_median_iqr": q(gain), "final_bcva_median_iqr": q(final), "pct_gain_10plus": float(100 * y.mean()),
       "neg_to_pos_ratio": float((1 - y.mean()) / y.mean())},
       "automation_flip_rate": flip_rate,
       "models": {k: v[0] for k, v in models.items()},
       "patient": {"features": dict(zip(FEATS, PATIENT[0].tolist())), "p_gain_10plus": p_patient, "logit": logit,
                   "intercept": intercept, "contributions": contrib, "misread": misread, "worst_misread": worst_mis,
                   "similar_synthetic_eyes": int(nb.sum()), "similar_observed_rate": nb_rate},
       "importances": importances}
auc_e = models[K_AUTO][0]["auc"][0]; auc_m = models[K_MEAS][0]["auc"][0]
auc_g = models["Gradient boosting, automated"][0]["auc"][0]; auc_v = models["BCVA only (logistic)"][0]["auc"][0]

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC_, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#adb5bd", "#2b8a3e"

fig, ax = plt.subplots(figsize=(6.4, 3.8))
for (name, (agg, pred)), col, ls in zip(models.items(), [INK, ACC_, BLUE, MUTED], ["-", "-", "--", ":"]):
    fpr, tpr, _ = roc_curve(y, pred)
    ax.plot(fpr, tpr, color=col, ls=ls, lw=1.8, label=f"{name} (AUC {agg['auc'][0]:.2f})")
ax.plot([0, 1], [0, 1], color=MUTED, lw=0.8)
ax.set_xlabel("false positive rate"); ax.set_ylabel("true positive rate")
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "fig_roc.png", dpi=160); plt.close(fig)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1, 1.25]})
top = importances[:8][::-1]
a1.barh([t[0] for t in top], [t[1] for t in top], color=[ACC_ if "BCVA" in t[0] else BLUE for t in top])
a1.set_xlabel("mean |score| (logits)", fontsize=9); a1.tick_params(axis="y", labelsize=8)
a1.set_title("global importance", fontsize=9)
a2.plot(gx, shape, color=INK, lw=1.8); a2.axhline(0, color=MUTED, lw=0.8)
a2.axvline(PATIENT[0, 0], color=ACC_, lw=1, ls=":"); a2.text(PATIENT[0, 0] + 1, max(shape) * 0.9, "your patient", color=ACC_, fontsize=8)
a2b = a2.twinx(); a2b.hist(X[:, 0], bins=30, color=MUTED, alpha=0.35); a2b.set_yticks([]); a2b.spines["right"].set_visible(False)
a2.set_zorder(a2b.get_zorder() + 1); a2.patch.set_visible(False)
a2.set_xlabel("baseline BCVA (ETDRS letters)", fontsize=9); a2.set_ylabel("score (logits)", fontsize=9)
a2.set_title("BCVA shape function (grey = density)", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "fig_glassbox.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.4))
items = [("baseline (intercept)", intercept)] + sorted(contrib, key=lambda t: -abs(t[1]))
cum = 0.0
for i, (n, v) in enumerate(items):
    start = 0 if i == 0 else cum; end = v if i == 0 else cum + v
    col = MUTED if i == 0 else (GOOD if v > 0 else ACC_)
    ax.barh(len(items) - i, end - start, left=start, color=col, height=0.6)
    ax.text(max(start, end) + 0.05, len(items) - i, f"{v:+.2f}", va="center", fontsize=8)
    cum = end
ax.axvline(logit, color=INK, lw=1, ls="--")
ax.set_yticks(range(len(items), 0, -1)); ax.set_yticklabels([n for n, _ in items], fontsize=8)
ax.set_xlabel(f"log-odds of gaining ≥10 letters  →  final {logit:+.2f} = {100 * p_patient:.0f}% chance")
lo_, hi_ = ax.get_xlim(); ax.set_xlim(lo_, hi_ + 0.4)
fig.tight_layout(); fig.savefig(OUT / "fig_waterfall.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.6))
labs = [f"{m['biomarker']} read as {m['read_as']}" if isinstance(m["read_as"], int) else f"{m['biomarker']}" for m in misread]
ax.barh(range(len(misread))[::-1], [100 * m["p"] for m in misread], color=BLUE, height=0.6)
ax.axvline(100 * p_patient, color=ACC_, lw=1.5); ax.text(100 * p_patient + 0.5, len(misread) - 0.4, "correct read", color=ACC_, fontsize=8)
ax.set_yticks(range(len(misread))[::-1]); ax.set_yticklabels(labs, fontsize=8)
ax.set_xlabel("predicted chance of ≥10-letter gain (%)"); ax.set_xlim(0, max(100 * max(m["p"] for m in misread), 100 * p_patient) * 1.25)
fig.tight_layout(); fig.savefig(OUT / "fig_misread.png", dpi=160); plt.close(fig)

# ---------------------------------------------------------------- card
pt = res["patient"]["features"]
desc = (f"BCVA {pt['BCVA']:.0f}, CST {pt['CST']:.0f} µm, " + ", ".join(f"{k} {'+' if pt[k] else '−'}" for k in ["SRF", "IRF", "PED", "VMT"]))
topc = max(contrib, key=lambda t: abs(t[1]))
tiles = [
    {"label": "Your patient's predicted chance", "value": f"{100 * p_patient:.0f}%",
     "sub": f"of gaining ≥10 letters at 1 year ({desc}); cohort base rate {100 * y.mean():.0f}%", "tone": "accent"},
    {"label": "Biggest single reason", "value": f"{topc[0]} {topc[1]:+.2f}", "sub": "logit contribution in the glass-box model", "tone": "neutral"},
    {"label": "If the AI misreads one biomarker", "value": f"{100 * p_patient:.0f}% → {100 * worst_mis['p']:.0f}%",
     "sub": f"worst case: {worst_mis['biomarker']} misread", "tone": "warn"},
    {"label": "Glass box vs black box", "value": f"{auc_e:.2f} vs {auc_g:.2f}",
     "sub": f"CV AUC, EBM vs gradient boosting on automated biomarkers (measured: {auc_m:.2f}; BCVA alone: {auc_v:.2f})", "tone": "good"},
]
me = models[K_AUTO][0]; mg = models["Gradient boosting, automated"][0]
f = lambda m, k: f"{m[k][0]:.2f} ± {m[k][1]:.2f}"
compare = [
    {"metric": "EBM (automated biomarkers) AUC ROC", "paper": "0.77 ± 0.07", "yours": f(me, "auc"), "note": "synthetic cohort"},
    {"metric": "EBM sensitivity / specificity", "paper": "0.75 ± 0.08 / 0.61 ± 0.03", "yours": f"{f(me, 'sens')} / {f(me, 'spec')}", "note": "threshold = prevalence"},
    {"metric": "EBM F1", "paper": "0.54 ± 0.02", "yours": f(me, "f1"), "note": ""},
    {"metric": "XGBoost AUC ROC", "paper": "0.74 ± 0.06", "yours": f(mg, "auc"), "note": "sklearn gradient boosting stand-in"},
    {"metric": "EBM on measured vs automated biomarkers", "paper": "AUC = 0.77 vs 0.77",
     "yours": f"{auc_m:.2f} vs {auc_e:.2f}", "note": f"error scale ×{ERR:g}, CST error {CST_ERR:g} µm"},
    {"metric": "Top features", "paper": "baseline VA, CST, and the interaction between these two features",
     "yours": ", ".join(t[0] for t in importances[:3]), "note": "built into the simulation"},
    {"metric": "Eyes gaining ≥10 letters", "paper": "299 (25%)", "yours": f"{int(y.sum())} ({100 * y.mean():.0f}%)", "note": "calibrated"},
    {"metric": "Median letters gained", "paper": "2 [-3, 10]", "yours": f"{q(gain)[0]:.0f} [{q(gain)[1]:.0f}, {q(gain)[2]:.0f}]", "note": "approximate match"},
    {"metric": "BCVA at one year", "paper": "68 [57, 76]", "yours": f"{q(final)[0]:.0f} [{q(final)[1]:.0f}, {q(final)[2]:.0f}]", "note": "not matched exactly"},
]
card = {"paper": {"num": 5, "title": "Visual Acuity Improvement Prediction in Neovascular Age-Related Macular Degeneration",
                  "authors": "Hadi Moazen, Mélanie Hébert, Alaa Eddine Ayadi, Ali Dirani, Audrey Durand", "url": "https://drive.google.com/file/d/1h81k0dJvGwdnHFxP-kYIcjuwFZgX_n1d/view",
                  "affiliation": "Université Laval · CHU de Québec – Université Laval"},
        "inputs": {"your patient": desc, "automation error": f"×{ERR:g} paper's error rates", "CST error": f"{CST_ERR:g} µm",
                   "cohort": f"{N:,} simulated eyes", "model": res["glassbox"], "seed": SEED,
                   "data": "SIMULATED, not for clinical use"},
        "tiles": tiles,
        "figures": [
            {"path": "fig_waterfall.png", "title": "Why this prediction? Every term, in log-odds",
             "caption": "The glass-box model adds one score per feature (and per learned interaction) to a baseline. Green pushes "
                        "towards a ≥10-letter gain, orange away from it. Model trained on a simulated cohort."},
            {"path": "fig_misread.png", "title": "What if the automated pipeline gets one biomarker wrong?",
             "caption": "Your patient's prediction when one binary biomarker is flipped, or CST is mis-measured by ±2× the CST error."},
            {"path": "fig_glassbox.png", "title": "What did the model learn?",
             "caption": "Left: global term importances. Right: the baseline-BCVA shape function (compare the paper's Figure 3b); "
                        "the effects were specified by this simulation, so the plot shows the EBM recovering them."},
            {"path": "fig_roc.png", "title": "Glass box vs black box, measured vs automated",
             "caption": "Out-of-fold ROC curves (5-fold CV) on the simulated cohort."}],
        "compare": compare, "runbook": {"name": "smash-05-namd-visual-acuity", "url": P.get("runbook_url", "")}}
(OUT / "card_data.json").write_text(json.dumps(card, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: patient p = {p_patient:.3f}; AUC EBM measured {auc_m:.3f} / automated {auc_e:.3f} / GBM {auc_g:.3f} / BCVA-only {auc_v:.3f}; "
    f"worst misread {worst_mis['biomarker']} -> {worst_mis['p']:.3f}")
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
