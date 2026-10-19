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
    skill_name: smash-09-low-confidence-profiles
    confidence: high
---

# Hidden Shift Finder: Missed by the Population Test, Found in a Profile (SMASH 2026 · Paper #9)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Diagnosing Low-Confidence Patient Profiles via Localized Harmful Covariate Shift Detection"** (Olivier Lefebvre, Hakima Laribi, Dan Poenaru, Martin Vallières).
Read the paper: https://doi.org/10.48550/arXiv.2610.19178

The paper's claim: population-level reliability checks can miss harm that is concentrated in some patients. It
combines **MED3pa** (per-patient confidence + an interpretable tree that groups patients into low-confidence
*profiles*) with **Detectron** (a learned test for *harmful covariate shift*, HCS) run **inside each profile**. In
MIMIC-IV, removing patients under 50 from training was **not detected at the population level for any task**, yet
was localized to specific degraded profiles (30-day readmission: a profile covering 17.68% of patients, AUC
0.80 → 0.64). Sex and race shifts were detected almost everywhere, so they gave little guidance on *who* is affected.

MIMIC-IV cannot be used here, so the participant picks a **synthetic MIMIC-like cohort with known mechanisms**
(default) or the public **UCI Diabetes 130-US hospitals** data, chooses which subgroup to remove from training, and the
run executes the whole pipeline, then repeats it for all three shift types (the paper's localized-vs-broad contrast).
Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment itself takes about 15–30 s.

### The method as in the paper (§2), and what is simplified
- Patient-level 50/50 split into training (P) and testing (Q). For each shift, the subgroup is **removed from the
  training half only**: `age<50`, `sex` (female patients removed, sex ≠ male), or `race` (non-White removed).
  Q is identical across conditions. BaseModel: MLP (here sklearn, 32 hidden units).
- Q is split in half: **MED3pa** learns on the first half and profiles are evaluated on the second. Confidence =
  regressor predicting per-patient correctness `1 − |y − p̂|`; a depth-limited regression tree on those
  predictions gives interpretable rule-based profiles (leaves). *Simplified*: MED3pa's IPC/APC models are reduced to
  one gradient-boosting regressor + one regression tree; profiles are the leaves.
- **Detectron** per profile S (paper §2): `P_S` is split in half, `P_S^r` held out as reference, the rest joins all
  out-of-profile training-distribution cases in `P_S^t`. An ensemble of constrained disagreement classifiers (CDCs),
  each **initialised from the BaseModel**, is trained to agree with the BaseModel on `P_S^t` and to disagree on
  `Q_S` and `P_S^r`; cases a CDC disagrees on are rejected and the next CDC trains on the rest. HCS if
  significantly more `Q_S` than `P_S^r` cases are rejected (one-sided test, α = 0.05). Only profiles with ≥ 5% of
  patients are tested. *Simplified*: CDCs are fine-tuned copies of the sklearn MLP (3 epochs; each disagreement case
  weighted like 4 agreement cases); the test is a one-sided Fisher exact test on rejection counts (exact under no
  shift, because `Q_S` and `P_S^r` go through identical treatment), repeated with fresh subsamples and CDCs, HCS if
  the **median** p < α. Training-distribution performance is measured on held-out training-distribution patients
  (not the BaseModel's own fitting data).

### Paper headline numbers (quote exactly; MIMIC-IV)
- Age shift: **not detected at the population level for any of the three tasks**; localized profiles detected.
- 30-day readmission, age shift: profile covering **17.68%** (hemoglobin ≤ 10.91 g/dL, length of stay ≤ 5 days, no
  specified malignant neoplasm); mean age **73.3 → 67.8**; AUC **0.80 → 0.64**, balanced accuracy 0.72 → 0.58,
  sensitivity 0.67 → 0.42, specificity 0.77 → 0.75.
- 48-h mortality, age shift: one profile covering 8.76% (GCS-Motor ≤ 5 and age ≤ 66). 48-h live discharge: GCS-Verbal ≤ 3
  profile, sensitivity decreased to zero; no HCS in profiles covering 39.2%.
- Sex shift: detected in all profiles (live discharge, mortality), AUC and sensitivity down ≈ 0.05–0.07; readmission:
  all but two profiles (≈ 23.8% of patients), which still collapsed (AUC and sensitivity ≈ −0.25).
- Race shift: HCS detected in every profile across all three tasks.

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
| Dataset | `{{dataset}}` | `synthetic` | `synthetic` (100,000-patient MIMIC-like readmission cohort with known mechanisms) or `diabetes130` (UCI Diabetes 130-US hospitals, real, ~3 MB download) |
| Removed subgroup | `{{removed_subgroup}}` | `age<50` | Subgroup removed from training only: `age<50`, `sex` (female removed), `race` (non-White removed) |
| Outcome | `{{outcome}}` | `readmit_any` | `diabetes130` only: `readmit_any` or `readmit_30` (30-day) |
| Tree depth | `{{tree_depth}}` | `3` | Depth of MED3pa's profile tree (2–4); deeper = more, smaller profiles |
| CDCs | `{{n_cdc}}` | `5` | Constrained disagreement classifiers per Detectron test (2–10) |
| Detectron sample | `{{detectron_n}}` | `500` | Max deployment (and reference) cases per Detectron test (50–1000) |
| Detectron repeats | `{{detectron_repeats}}` | `5` | Independent repeats per test; HCS if median p < α (1–9) |
| Min profile share | `{{min_profile_share}}` | `0.05` | Smallest profile tested (paper: 5% of the population) |
| α | `{{alpha}}` | `0.05` | False-positive rate for declaring HCS (paper: 0.05) |
| Seed | `{{seed}}` | `0` | Seed for the split, models and (synthetic) cohort |

## Dependencies

numpy, pandas, scikit-learn, scipy, matplotlib (preinstalled in `python312-uv`; scipy ships with scikit-learn).
`diabetes130` downloads ~3 MB from the UCI repository.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, pandas, sklearn, scipy, matplotlib" 2>/dev/null || uv pip install --system -q numpy pandas scikit-learn scipy matplotlib
```

Write `/app/work/params.json` (numbers as JSON numbers; if a value still looks like an unsubstituted `{{…}}`
placeholder, use the default from the table; `n_patients` is a fixed budget setting, do not change it):

```json
{"dataset": "{{dataset}}", "removed_subgroup": "{{removed_subgroup}}", "outcome": "{{outcome}}",
 "tree_depth": {{tree_depth}}, "n_cdc": {{n_cdc}}, "detectron_n": {{detectron_n}},
 "detectron_repeats": {{detectron_repeats}}, "min_profile_share": {{min_profile_share}}, "alpha": {{alpha}},
 "seed": {{seed}}, "n_patients": 100000, "runbook_url": ""}
```

Validate before running: `dataset` ∈ {`synthetic`, `diabetes130`}; `removed_subgroup` ∈ {`age<50`, `sex`, `race`};
`outcome` ∈ {`readmit_any`, `readmit_30`}. Clamp `tree_depth` to [2, 4], `n_cdc` to [2, 10], `detectron_n` to
[50, 1000], `detectron_repeats` to [1, 9], `min_profile_share` to [0.02, 0.2], `alpha` to [0.001, 0.2]. Record every
correction as a caveat.

## Step 2: Get the code (extract it, don't retype it)

The tested implementation of the method is embedded in the **Appendix** at the end of this runbook. Do not
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
environment problems (missing package, network retry), never the methodology.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 300 python experiment.py params.json {{results_dir}}
```

Expected: 15–40 s. Prints one line per shift type and ends with a `done:` line. If the `diabetes130` download fails,
retry once; if it fails again, rerun with `"dataset": "synthetic"` and record the substitution as a caveat.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Then write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the localization result of *this* run with 1–2 numbers from `results.json`. If
  `localized` is true: the population-level test missed the shift (its median `p_value`) but a profile was flagged,
  with its AUC change (`headline_profile.train_dist.auc` → `headline_profile.test.auc`) and share. If the population
  test also fired, or nothing was flagged, say that plainly.
- **idea**: plain language: a model can be fine on average and unreliable for some patients; MED3pa finds
  interpretable low-confidence patient groups; Detectron, run inside each group, tests whether a harmful shift between
  training and deployment patients plausibly explains that group's problem.
- **findings**: (1) population vs profile verdicts (`population.detectron`, each profile's `status` and `detectron`);
  (2) the flagged profile: its rule, share, share of the removed subgroup (`subgroup_share_test`), mean age training →
  deployment, AUC / sensitivity / specificity vs the paper's 0.80 → 0.64 etc.; (3) the three-shift contrast
  (`contrast`): age localized vs sex/race broad, as in the paper; (4) the paper's caution: HCS without degradation, or
  degradation without HCS, can both happen; check the profiles in `fig_profiles.png` for such cases.
- Never call a group "biased" or a model "unfair"; describe reliability and shift.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `dataset, removed_subgroup, outcome,
  tree_depth, n_cdc, detectron_n, detectron_repeats, min_profile_share, alpha, seed`. Good contrasts: the real data
  (`dataset` `diabetes130`), a broad shift (`removed_subgroup` `sex`), a smaller Detectron sample (`detectron_n`
  100, where power drops), a deeper tree (`tree_depth` 4).
- **caveats**: synthetic cohort with planted mechanisms (or Diabetes-130 rather than MIMIC-IV); MED3pa and Detectron
  are faithful simplifications (sklearn MLP CDCs, Fisher test, median of repeats); results vary with seed, so a
  borderline p-value deserves a second seed; HCS is a diagnostic signal, not proof that the shift caused the error.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: dataset and removed subgroup, population verdict, flagged profiles with
rules and AUC change, three-shift contrast, headline).

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
python3 - "{{results_dir}}" "dataset,removed_subgroup,outcome,tree_depth,n_cdc,detectron_n,detectron_repeats,min_profile_share,alpha,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} dataset,removed_subgroup,outcome,tree_depth,n_cdc,detectron_n,detectron_repeats,min_profile_share,alpha,seed 300 checklist.json
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
"""Low-confidence profiles + localized harmful-covariate-shift detection — SMASH 2026 paper #9
(Lefebvre, Laribi, Poenaru, Vallières).

Pipeline (paper §2): remove one subgroup from the BaseModel's training data only; train an MLP BaseModel;
MED3pa-style per-patient confidence (regressor on per-patient correctness) + depth-limited regression tree
-> interpretable profiles; Detectron (ensemble of constrained disagreement classifiers, CDCs, initialised
from the BaseModel) at population level and inside every profile covering >= 5% of patients, alpha = 0.05.
Extension: the same pipeline for all three injected shifts (age / sex / race), localized vs broad.

usage: python experiment.py params.json outdir
"""
import copy, io, json, sys, time, urllib.request, warnings, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore")
T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
DATASET = P["dataset"]; SHIFT = P["removed_subgroup"]; DEPTH = int(P["tree_depth"])
N_CDC = int(P["n_cdc"]); N_DET = int(P["detectron_n"]); MIN_SHARE = float(P["min_profile_share"])
ALPHA = float(P["alpha"]); SEED = int(P["seed"]); N_REP = int(P.get("detectron_repeats", 5)); OUTCOME = P.get("outcome", "readmit_any")
N_SYN = int(P.get("n_patients", 100000))
CDC_EPOCHS, CDC_WEIGHT = 3, 4          # CDC fine-tuning epochs; each disagreement case counts like 4 agreement cases
SHIFTS = {"age<50": "patients under 50", "sex": "female patients (sex != male)", "race": "non-White patients"}
INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e"


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


# ------------------------------------------------------------------ data
def synthetic(n, seed):
    """MIMIC-like 30-day readmission world with known mechanisms (all synthetic):
    - patients under 55 are over-represented among chronically anaemic patients, and in that group readmission is
      driven by a lab value (lab_1) that is uninformative for everyone else: a localized mechanism;
    - sex and race each modify several effects for everyone: broad mechanisms."""
    r = np.random.default_rng(10_000 + seed)
    age = np.clip(r.normal(64, 16, n), 18, 95)
    young = age < 50
    female = r.binomial(1, 0.48, n); nonwhite = r.binomial(1, 0.30, n)
    anaemic = r.binomial(1, np.where(young, 0.50, 0.16))
    hb = 13.4 - 1.1 * female - 0.4 * nonwhite - 2.6 * anaemic + r.normal(0, 1.3, n)
    los = np.round(np.exp(r.normal(1.45, 0.55, n)), 0).clip(1, 40)
    wbc = np.exp(r.normal(2.2, 0.33, n))
    creat = np.exp(r.normal(0.0, 0.35, n)) + 0.25 * nonwhite
    prior = r.poisson(np.where(young & (anaemic == 1), 1.6, 0.8))
    malig = r.binomial(1, 0.16, n)
    z = r.standard_normal((n, 4))
    zs = lambda v: (v - v.mean()) / v.std()
    lin = (-1.25 + 0.30 * prior + 0.45 * (los > 7) + 0.55 * malig + 0.45 * zs(creat) - 0.30 * (hb - 12)
           + 0.012 * (age - 64)
           + female * (0.55 * zs(wbc) - 0.35 * zs(np.log(los)) + 0.25)                          # broad (sex)
           + nonwhite * (0.55 * zs(creat) + 0.30 * prior - 0.3))                               # broad (race)
    # localized mechanism: in younger (< 55), chronically anaemic patients readmission is driven by a lab value (lab_1)
    # that carries no signal for anyone else; removing patients under 50 leaves only a thin slice (50-54) to learn it from
    lin = np.where(anaemic == 1, 0.7 * lin + 0.3, lin)                 # anaemic patients: noisier outcome for everyone
    lin = np.where(young & (anaemic == 1), -0.1 + 2.4 * z[:, 0], lin)
    y = r.binomial(1, 1 / (1 + np.exp(-lin)))
    X = pd.DataFrame({"age": np.round(age), "female": female, "non_white": nonwhite, "hemoglobin": np.round(hb, 1),
                      "length_of_stay": los, "wbc": np.round(wbc, 1), "creatinine": np.round(creat, 2),
                      "prior_admissions": prior, "malignancy": malig,
                      **{f"lab_{i + 1}": np.round(z[:, i], 2) for i in range(4)}})
    return X, y, "30-day readmission (synthetic MIMIC-like cohort)"


def diabetes130():
    url = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
    with urllib.request.urlopen(url, timeout=120) as resp:
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
    df = pd.read_csv(z.open([n for n in z.namelist() if n.endswith("diabetic_data.csv")][0]), na_values="?", low_memory=False)
    df = df[df["gender"].isin(["Male", "Female"])].drop_duplicates("patient_nbr").reset_index(drop=True)
    num = ["time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications", "number_outpatient",
           "number_emergency", "number_inpatient", "number_diagnoses"]
    cat = ["admission_type_id", "discharge_disposition_id", "admission_source_id", "A1Cresult", "insulin", "change",
           "diabetesMed"]
    X = pd.concat([pd.DataFrame({"age": df["age"].str.extract(r"\[(\d+)")[0].astype(int) + 5,
                                 "female": (df["gender"] == "Female").astype(int),
                                 "non_white": (df["race"].fillna("Unknown") != "Caucasian").astype(int)}),
                   df[num], pd.get_dummies(df[cat].astype(str), drop_first=True).astype(int)], axis=1)
    if OUTCOME == "readmit_30":
        y, lab = (df["readmitted"] == "<30").astype(int).values, "30-day readmission (UCI Diabetes 130-US hospitals)"
    else:
        y, lab = (df["readmitted"] != "NO").astype(int).values, "any readmission (UCI Diabetes 130-US hospitals)"
    return X, y, lab


def in_subgroup(X, shift):
    return {"age<50": X["age"].values < 50, "sex": X["female"].values == 1, "race": X["non_white"].values == 1}[shift]


# ------------------------------------------------------------------ metrics
def perf(y, p, tau):
    out = {"n": int(len(y)), "prevalence": float(y.mean()) if len(y) else None}
    if len(y) < 20 or y.min() == y.max():
        return {**out, "auc": None, "sens": None, "spec": None, "bal_acc": None}
    yh = p >= tau
    se = float(np.mean(yh[y == 1])); sp = float(np.mean(~yh[y == 0]))
    return {**out, "auc": float(roc_auc_score(y, p)), "sens": se, "spec": sp, "bal_acc": (se + sp) / 2}


def rules_of(tree, names):
    """Human-readable rule for every leaf of a fitted sklearn tree."""
    t = tree.tree_; out = {}

    def walk(node, conds):
        if t.children_left[node] == -1:
            out[node] = conds; return
        f, th = names[t.feature[node]], t.threshold[node]
        fmt = (lambda op: f"{f} = {'0' if op == '≤' else '1'}") if set(np.unique(XQA[:, t.feature[node]])) <= {0, 1} else \
              (lambda op: f"{f} {op} {th:.4g}")
        walk(t.children_left[node], conds + [fmt("≤")]); walk(t.children_right[node], conds + [fmt(">")])
    walk(0, [])
    simp = {}
    for leaf, conds in out.items():   # merge repeated bounds on the same feature
        keep = {}
        for c in conds:
            key = c.split(" ")[0] + (" ≤" if " ≤ " in c else " >" if " > " in c else " =")
            if key.endswith("≤") and key in keep:
                keep[key] = c if float(c.split()[-1]) < float(keep[key].split()[-1]) else keep[key]
            elif key.endswith(">") and key in keep:
                keep[key] = c if float(c.split()[-1]) > float(keep[key].split()[-1]) else keep[key]
            else:
                keep[key] = c
        simp[leaf] = " & ".join(keep.values()) or "all patients"
    return simp


# ------------------------------------------------------------------ Detectron
def detectron(base, Z, yhat, q_idx, ps_idx, pcal_idx, rng):
    """Repeat the Detectron test N_REP times (fresh subsamples and CDCs); HCS if the median p-value < alpha."""
    reps = [detectron_once(base, Z, yhat, q_idx, ps_idx, pcal_idx, rng) for _ in range(N_REP)]
    if reps[0] is None:
        return None
    pv = [r["p_value"] for r in reps]
    med = float(np.median(pv))
    return {"n": reps[0]["n"], "repeats": N_REP, "p_value": med, "p_values": pv, "hcs": bool(med < ALPHA),
            "share_of_repeats_hcs": float(np.mean([p_ < ALPHA for p_ in pv])),
            "rate_Q": float(np.mean([r["rate_Q"] for r in reps])), "rate_Pr": float(np.mean([r["rate_Pr"] for r in reps]))}


def detectron_once(base, Z, yhat, q_idx, ps_idx, pcal_idx, rng):
    """Profile-level Detectron (paper §2). P_S is split in half: P_S^r (reference) and the rest, which joins all
    out-of-profile training-distribution cases in P_S^t. Each CDC starts as a copy of the BaseModel, is trained to
    agree with the BaseModel's labels on P_S^t and to disagree on the not-yet-rejected cases of Q_S and P_S^r;
    disagreeing cases are rejected and the next CDC trains on the rest. HCS if CDCs reject significantly more of Q_S
    than of P_S^r (one-sided Fisher exact test; Q_S and P_S^r are treated identically, so the test is exact under
    no shift)."""
    n = int(min(len(q_idx), len(ps_idx) // 2, N_DET))
    if n < 10:
        return None
    perm = rng.permutation(ps_idx); pr = perm[:n]
    pt = np.setdiff1d(pcal_idx, pr)
    qs = rng.choice(q_idx, n, replace=False)
    D = np.r_[qs, pr]; isq = np.r_[np.ones(n, bool), np.zeros(n, bool)]
    rej = np.zeros(2 * n, bool); per_round = []
    for _ in range(N_CDC):
        rem = ~rej
        Xd = np.r_[Z[pt], np.repeat(Z[D[rem]], CDC_WEIGHT, 0)]
        yd = np.r_[yhat[pt], np.repeat(1 - yhat[D[rem]], CDC_WEIGHT)]
        cdc = copy.deepcopy(base)
        for _ in range(CDC_EPOCHS):
            o = rng.permutation(len(yd)); cdc.partial_fit(Xd[o], yd[o])
        dis = (cdc.predict(Z[D]) != yhat[D]) & rem
        rej |= dis
        per_round.append([int(rej[isq].sum()), int(rej[~isq].sum())])
    kq, kp = int(rej[isq].sum()), int(rej[~isq].sum())
    pval = float(fisher_exact([[kq, n - kq], [kp, n - kp]], alternative="greater")[1])
    return {"n": n, "rejected_Q": kq, "rejected_Pr": kp, "rate_Q": kq / n, "rate_Pr": kp / n, "p_value": pval,
            "hcs": bool(pval < ALPHA), "per_round": per_round}


# ------------------------------------------------------------------ one full pipeline
def pipeline(X, y, shift, seed, full=True):
    global XQA
    rng = np.random.default_rng(seed)
    sub = in_subgroup(X, shift)
    idx = rng.permutation(len(y)); half = len(y) // 2
    Pall, Q = idx[:half], idx[half:]                       # patient-level 50/50 split (one row per patient)
    Pk = Pall[~sub[Pall]]                                  # injected shift: subgroup removed from training only
    Pfit, Pcal = Pk[:int(0.7 * len(Pk))], Pk[int(0.7 * len(Pk)):]   # Pcal: held-out training-distribution cases
    QA, QB = Q[:len(Q) // 2], Q[len(Q) // 2:]              # MED3pa learns on QA, profiles evaluated on QB
    sc = StandardScaler().fit(X.values[Pfit]); Z = sc.transform(X.values).astype(np.float64)
    base = MLPClassifier((32,), alpha=1e-3, max_iter=40, random_state=seed).fit(Z[Pfit], y[Pfit])
    p = base.predict_proba(Z)[:, 1]
    tau = float(y[Pfit].mean()); yhat = (p >= tau).astype(int)
    res = {"shift": shift, "n_train": int(len(Pfit)), "n_removed": int(sub[Pall].sum()), "tau": tau,
           "subgroup_share_test": float(sub[Q].mean())}
    res["population"] = {"train_dist": perf(y[Pcal], p[Pcal], tau), "test": perf(y[QB], p[QB], tau),
                         "test_subgroup": perf(y[QB][sub[QB]], p[QB][sub[QB]], tau),
                         "test_rest": perf(y[QB][~sub[QB]], p[QB][~sub[QB]], tau)}
    if full:   # reference: same BaseModel recipe trained WITHOUT removing the subgroup
        Pr_full = Pall[:len(Pfit)]
        ref = MLPClassifier((32,), alpha=1e-3, max_iter=40, random_state=seed).fit(Z[Pr_full], y[Pr_full])
        res["population"]["test_no_shift_model"] = perf(y[QB], ref.predict_proba(Z[QB])[:, 1], float(y[Pr_full].mean()))
    # MED3pa: individual confidence = predicted correctness 1 - |y - p|, then an interpretable regression tree
    ipc_target = 1 - np.abs(y - p)
    feats_ipc = np.c_[X.values, p]
    ipc = HistGradientBoostingRegressor(max_iter=150, max_depth=4, random_state=seed).fit(feats_ipc[QA], ipc_target[QA])
    conf = ipc.predict(feats_ipc)
    XQA = X.values[QA]
    tree = DecisionTreeRegressor(max_depth=DEPTH, min_samples_leaf=max(20, int(np.ceil(0.03 * len(QA)))),
                                 random_state=seed).fit(X.values[QA], conf[QA])
    leaf = tree.apply(X.values)
    rules = rules_of(tree, list(X.columns))
    res["population"]["detectron"] = detectron(base, Z, yhat, QB, Pcal, Pcal, rng)
    profiles = []
    for lf in sorted(np.unique(leaf[QA]), key=lambda l: conf[QB][leaf[QB] == l].mean() if (leaf[QB] == l).any() else 1):
        qs, ps = QB[leaf[QB] == lf], Pcal[leaf[Pcal] == lf]
        share = float(np.mean(leaf[Q] == lf))
        pr = {"leaf": int(lf), "rule": rules[lf], "share": share, "confidence": float(conf[qs].mean()) if len(qs) else None,
              "subgroup_share_test": float(sub[qs].mean()) if len(qs) else 0.0,
              "train_dist": perf(y[ps], p[ps], tau), "test": perf(y[qs], p[qs], tau),
              "mean_age_train": float(X["age"].values[ps].mean()) if len(ps) else None,
              "mean_age_test": float(X["age"].values[qs].mean()) if len(qs) else None}
        a0, a1 = pr["train_dist"]["auc"], pr["test"]["auc"]
        pr["auc_drop"] = (a0 - a1) if (a0 is not None and a1 is not None) else None
        if share < MIN_SHARE:
            pr["detectron"], pr["status"] = None, f"< {MIN_SHARE:.0%} of patients: not tested"
        elif len(ps) < 20:
            pr["detectron"], pr["status"] = None, "no training-distribution patients: shifted by construction"
        else:
            pr["detectron"] = detectron(base, Z, yhat, qs, ps, Pcal, rng)
            pr["status"] = ("HCS detected" if pr["detectron"]["hcs"] else "no HCS") if pr["detectron"] else "too few cases"
        profiles.append(pr)
    res["profiles"] = profiles
    tested = [x for x in profiles if x["detectron"]]
    flagged = [x for x in tested if x["detectron"]["hcs"]]
    res["n_profiles"] = len(profiles); res["n_tested"] = len(tested); res["n_flagged"] = len(flagged)
    res["share_flagged"] = float(sum(x["share"] for x in flagged))
    res["share_tested"] = float(sum(x["share"] for x in tested))
    res["population_hcs"] = bool(res["population"]["detectron"]["hcs"])
    return res


def main():
    if DATASET == "diabetes130":
        log("downloading UCI Diabetes 130-US hospitals (~3 MB)")
        X, y, outcome = diabetes130()
    else:
        X, y, outcome = synthetic(N_SYN, SEED)
    log(f"{DATASET}: {len(y):,} patients, outcome prevalence {y.mean():.3f}, {X.shape[1]} features")
    main_res = pipeline(X, y, SHIFT, SEED)
    log(f"main pipeline ({SHIFT}): {main_res['n_profiles']} profiles, {main_res['n_flagged']}/{main_res['n_tested']} "
        f"tested profiles flagged; population HCS {main_res['population_hcs']}")
    contrast = {}
    for sh in SHIFTS:
        r = main_res if sh == SHIFT else pipeline(X, y, sh, SEED, full=False)
        d = r["population"]["detectron"]
        contrast[sh] = {"population_hcs": r["population_hcs"], "population_p": d["p_value"], "n_tested": r["n_tested"],
                        "n_flagged": r["n_flagged"], "share_flagged": r["share_flagged"], "share_tested": r["share_tested"],
                        "pop_auc_train_dist": r["population"]["train_dist"]["auc"], "pop_auc_test": r["population"]["test"]["auc"]}
        log(f"contrast {sh}: population HCS {r['population_hcs']} (p={d['p_value']:.3g}); flagged "
            f"{r['n_flagged']}/{r['n_tested']} profiles = {r['share_flagged']:.0%} of patients")
    res = {"params": P, "dataset": DATASET, "outcome": outcome, "n_patients": int(len(y)), "prevalence": float(y.mean()),
           **main_res, "contrast": contrast}
    flagged = [x for x in main_res["profiles"] if x["detectron"] and x["detectron"]["hcs"]]
    cand = [x for x in flagged if x["auc_drop"] is not None] or [x for x in main_res["profiles"] if x["auc_drop"] is not None]
    worst = max(cand, key=lambda x: x["auc_drop"]) if cand else None
    res["headline_profile"] = worst
    res["localized"] = bool((not main_res["population_hcs"]) and len(flagged) > 0)
    figures(res)
    card(res)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=float))
    w = worst
    log(f"done: population HCS {main_res['population_hcs']}; flagged {len(flagged)} profiles"
        + (f"; worst flagged/degraded profile '{w['rule']}' AUC {w['train_dist']['auc']:.2f} -> {w['test']['auc']:.2f}" if w else ""))


# ------------------------------------------------------------------ figures and card
ABBR = {"hemoglobin": "Hb", "creatinine": "creat", "prior_admissions": "prior adm.", "length_of_stay": "LOS",
        "number_inpatient": "n_inpatient", "number_diagnoses": "n_diagnoses", "num_medications": "n_meds",
        "time_in_hospital": "LOS", "num_lab_procedures": "n_labs"}


def short(rule, n=58):
    for k, v in ABBR.items():
        rule = rule.replace(k, v)
    return rule if len(rule) <= n else rule[:n - 1] + "…"


def figures(res):
    plt.rcParams.update({"font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
    prof = [x for x in res["profiles"] if x["train_dist"]["auc"] is not None and x["test"]["auc"] is not None]
    # Fig 1: per-profile AUC, training distribution vs deployment, with HCS status
    fig, ax = plt.subplots(figsize=(6.4, 0.9 + 0.48 * max(len(prof), 1) + 0.5))
    for i, x in enumerate(prof):
        a0, a1 = x["train_dist"]["auc"], x["test"]["auc"]
        st = x["status"]
        col = ACC if st == "HCS detected" else (INK if st == "no HCS" else MUTED)
        ax.annotate("", (a1, i), (a0, i), arrowprops=dict(arrowstyle="->", color=col, lw=1.8))
        ax.plot(a0, i, "o", color=MUTED, ms=5)
        tag = {"HCS detected": "HCS ✔", "no HCS": "no HCS"}.get(st, "not tested")
        ax.text(1.005, i, f"{x['share']:.0%} · {tag} · {res['shift']} {x['subgroup_share_test']:.0%}",
                transform=ax.get_yaxis_transform(), va="center", fontsize=7.5, color=col)
    ax.set_yticks(range(len(prof))); ax.set_yticklabels([short(x["rule"], 44) for x in prof], fontsize=7)
    ax.invert_yaxis()
    allv = [v for x in prof for v in (x["train_dist"]["auc"], x["test"]["auc"])]
    ax.set_xlim(min(allv) - 0.02, max(allv) + 0.02)
    pop = res["population"]
    ax.axvline(pop["test"]["auc"], color=MUTED, ls=":", lw=1)
    ax.set_xlabel("AUC: training distribution (grey dot) → deployment (arrow head)")
    ax.set_title(f"Lowest confidence first. Population AUC {pop['train_dist']['auc']:.2f} → {pop['test']['auc']:.2f}, "
                 f"population Detectron: {'HCS' if res['population_hcs'] else 'no HCS'}", fontsize=8.5, loc="left")
    fig.tight_layout(); fig.savefig(OUT / "fig_profiles.png", dpi=160, bbox_inches="tight"); plt.close(fig)

    # Fig 2: Detectron disagreement rates (Q_S vs P_S^r) for population + tested profiles
    tests = [("Population", res["population"]["detectron"])] + \
            [(short(x["rule"], 40), x["detectron"]) for x in res["profiles"] if x["detectron"]]
    fig, ax = plt.subplots(figsize=(6.4, 0.8 + 0.42 * len(tests) + 0.4))
    for i, (lab, d) in enumerate(tests):
        ax.barh(i - 0.18, d["rate_Q"], height=0.34, color=ACC if d["hcs"] else BLUE, label="deployment cases Q_S" if i == 0 else None)
        ax.barh(i + 0.18, d["rate_Pr"], height=0.34, color=MUTED, label="reference training cases P_S^r" if i == 0 else None)
        ax.text(max(d["rate_Q"], d["rate_Pr"]) + 0.01, i, f"median p = {d['p_value']:.3g}  (n = {d['n']}, ×{d['repeats']})", va="center", fontsize=7.5)
    ax.set_yticks(range(len(tests))); ax.set_yticklabels([t[0] for t in tests], fontsize=7)
    ax.invert_yaxis(); ax.set_xlim(0, 1.18)
    ax.set_xlabel(f"share of cases on which the {N_CDC} CDCs could disagree with the BaseModel")
    ax.legend(frameon=False, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout(); fig.savefig(OUT / "fig_detectron.png", dpi=160, bbox_inches="tight"); plt.close(fig)

    # Fig 3: localized vs broad — the three injected shifts
    c = res["contrast"]; keys = list(c)
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.6))
    axs[0].bar(range(3), [100 * c[k]["share_flagged"] for k in keys], color=[ACC if k == res["shift"] else BLUE for k in keys])
    for i, k in enumerate(keys):
        axs[0].text(i, 100 * c[k]["share_flagged"] + 2, f"{c[k]['n_flagged']}/{c[k]['n_tested']}", ha="center", fontsize=8)
        axs[0].text(i, -14, "population:\n" + ("HCS" if c[k]["population_hcs"] else "no HCS"), ha="center", fontsize=7.5,
                    color=ACC if c[k]["population_hcs"] else INK)
    axs[0].set_xticks(range(3)); axs[0].set_xticklabels(keys); axs[0].set_ylim(0, 110)
    axs[0].set_ylabel("% of patients in flagged profiles"); axs[0].tick_params(axis="x", pad=24)
    axs[1].bar(np.arange(3) - 0.18, [c[k]["pop_auc_train_dist"] for k in keys], width=0.36, color=MUTED, label="training dist.")
    axs[1].bar(np.arange(3) + 0.18, [c[k]["pop_auc_test"] for k in keys], width=0.36, color=INK, label="deployment")
    lo = min(min(c[k]["pop_auc_test"], c[k]["pop_auc_train_dist"]) for k in keys)
    axs[1].set_ylim(max(0.5, lo - 0.08), 1.0); axs[1].set_xticks(range(3)); axs[1].set_xticklabels(keys)
    axs[1].set_ylabel("population AUC"); axs[1].legend(frameon=False, fontsize=7.5)
    fig.tight_layout(); fig.savefig(OUT / "fig_shift_types.png", dpi=160); plt.close(fig)


def fmt(v, d=2):
    return "—" if v is None else f"{v:.{d}f}"


def card(res):
    pop = res["population"]; d = pop["detectron"]; w = res["headline_profile"]
    flagged = [x for x in res["profiles"] if x["detectron"] and x["detectron"]["hcs"]]
    tiles = [
        {"label": "Population-level Detectron", "value": "HCS" if res["population_hcs"] else "no HCS",
         "sub": f"median p = {d['p_value']:.3g} over {d['repeats']} repeats; CDCs rejected {d['rate_Q']:.0%} of deployment vs {d['rate_Pr']:.0%} of reference cases",
         "tone": "warn" if res["population_hcs"] else "neutral"},
        {"label": "Profiles with a localized HCS", "value": f"{res['n_flagged']} of {res['n_tested']}",
         "sub": f"tested profiles (≥ {MIN_SHARE:.0%} of patients), covering {res['share_flagged']:.0%} of the population",
         "tone": "accent" if flagged else "neutral"},
    ]
    if w:
        tiles.append({"label": "Worst " + ("flagged" if flagged else "degraded") + " profile: AUC",
                      "value": f"{w['train_dist']['auc']:.2f} → {w['test']['auc']:.2f}",
                      "sub": f"{short(w['rule'], 70)} · {w['share']:.0%} of patients · sensitivity "
                             f"{fmt(w['train_dist']['sens'])} → {fmt(w['test']['sens'])}", "tone": "accent"})
    tiles.append({"label": "Population AUC", "value": f"{pop['train_dist']['auc']:.2f} → {pop['test']['auc']:.2f}",
                  "sub": f"training distribution → deployment; removed subgroup alone {fmt(pop['test_subgroup']['auc'])}",
                  "tone": "neutral"})
    inputs = {"dataset": res["dataset"], "outcome": res["outcome"], "removed from training": SHIFTS[SHIFT],
              "tree depth": DEPTH, "CDCs": N_CDC, "Detectron sample": N_DET, "min profile": f"{MIN_SHARE:.0%}", "α": ALPHA,
              "seed": SEED}
    c = res["contrast"]
    compare = [
        {"metric": "Age shift detected at population level?", "paper": "No, for all three tasks",
         "yours": ("HCS" if c["age<50"]["population_hcs"] else "no HCS") + f" (median p = {c['age<50']['population_p']:.3g})", "note": ""},
        {"metric": "Age shift localized to profiles", "paper": "Yes: e.g. readmission profile covering 17.68%",
         "yours": f"{c['age<50']['n_flagged']} of {c['age<50']['n_tested']} profiles ({c['age<50']['share_flagged']:.0%} of patients)", "note": ""},
        {"metric": "Sex / race shifts", "paper": "Detected in all (or all but two) profiles: broad, little localizing value",
         "yours": f"sex {c['sex']['n_flagged']}/{c['sex']['n_tested']} · race {c['race']['n_flagged']}/{c['race']['n_tested']} profiles; "
                  f"population {'HCS' if c['sex']['population_hcs'] else 'no HCS'} / {'HCS' if c['race']['population_hcs'] else 'no HCS'}", "note": ""},
    ]
    if w:
        compare.append({"metric": "Degraded profile: AUC / balanced acc. / sensitivity / specificity",
                        "paper": "0.80→0.64 / 0.72→0.58 / 0.67→0.42 / 0.77→0.75 (readmission, age shift)",
                        "yours": " / ".join(f"{fmt(w['train_dist'][k])}→{fmt(w['test'][k])}" for k in ("auc", "bal_acc", "sens", "spec")),
                        "note": short(w["rule"], 60)})
        if w["mean_age_train"] is not None:
            compare.append({"metric": "Mean age in that profile, training → deployment", "paper": "73.3 → 67.8",
                            "yours": f"{w['mean_age_train']:.1f} → {w['mean_age_test']:.1f}", "note": ""})
    figs = [{"path": "fig_profiles.png", "title": "Where does the model lose reliability?",
             "caption": "MED3pa profiles (leaves of the confidence tree), lowest confidence first. Arrow = AUC on held-out "
                        "training-distribution patients → deployment patients in the same profile. Right: share of patients, "
                        "Detectron verdict, and share of the removed subgroup inside the profile (deployment)."},
            {"path": "fig_detectron.png", "title": "Can disagreement classifiers tell deployment from training cases?",
             "caption": "Detectron: CDCs copy the BaseModel, must keep agreeing on training-distribution cases, and try to disagree "
                        "on deployment (Q_S) and reference (P_S^r) cases. Significantly more rejections on Q_S = harmful covariate shift."},
            {"path": "fig_shift_types.png", "title": "Localized or broad? Three injected shifts",
             "caption": "The same pipeline with each subgroup removed from training. Left: share of patients in profiles where "
                        "Detectron flags HCS (n flagged / n tested), and the population-level verdict. Right: population AUC."}]
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 9, "title": "Diagnosing Low-Confidence Patient Profiles via Localized Harmful Covariate Shift Detection",
                  "authors": "Olivier Lefebvre, Hakima Laribi, Dan Poenaru, Martin Vallières", "url": "https://doi.org/10.48550/arXiv.2610.19178",
                  "affiliation": "Université de Sherbrooke · Montreal Children's Hospital · McGill University"},
        "inputs": inputs, "tiles": tiles, "figures": figs, "compare": compare,
        "runbook": {"name": "smash-09-low-confidence-profiles", "url": P.get("runbook_url", "")}}, indent=2))


if __name__ == "__main__":
    main()
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
