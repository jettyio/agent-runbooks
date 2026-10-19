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
    skill_name: smash-19-engagement-not-enough
    confidence: high
---

# What Should the AI Optimize? Set the Weights, Watch the Verdict Flip (SMASH 2026 · Paper #19)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"When Engagement Is Not Enough: What Should AI Optimize in Gamified Education?"** (Takuji Takemoto).
Read the paper: https://drive.google.com/file/d/1L1jl5c3v9hjZtZ1QofMdEY-6dHQ-uJSn/view?usp=sharing

The paper's claim: engagement, perceived learning, behavioural intention and persistence are all legitimate signs of
educational success, but they **need not move together**, so an AI that optimizes one convenient proxy (engagement)
can pick the wrong intervention. It proposes keeping four outcome classes distinct, `U = f(E, L, B, P)`, and treating
their relative weight as a normative decision that must be stated (outcome accountability), and checking that
immediate proxies hold up over time (temporal accountability).

The participant **brings their own outcome weights** over Engagement (E), Learning (L), Behavioural intention (B) and
Persistence (P), plus their own assumption about persistence (the paper's follow-up T2 is still ongoing). The run:
1. **Case 1 (STEAM crossover, n = 49):** builds synthetic paired learners whose gamified − conventional differences
   reproduce the paper's d_z exactly; bootstraps d_z; scores both conditions under the participant's weights; reports
   the winner, how often it wins across resamples, and **the weight at which the decision flips**.
2. **Case 2 (disaster-preparedness card game, n = 37):** builds synthetic T0/T1 learners matching the paper's means,
   SDs and d_z, with engagement censored at the top of the 7-point scale and correlated with gains at the paper's r;
   asks **whether a system that watches engagement can find the learners who gained most**, and how strong the proxy
   would have to be; and shows the intervention's four different "success" numbers.

Output: a shareable **result card**. Target wall-clock: **under 3 minutes**; the experiment takes about 1 second.

**The paper's data are not public. Every learner in this run is synthetic, generated to match the paper's reported
summary statistics.** Anything the paper did not report (correlations between outcomes, the shape of distributions)
is an assumption stated below and on the card.

### How the synthetic data are calibrated
- Case 1: four difference scores per learner (interest, enjoyment of interaction, overall enjoyment = **E**; perceived
  acquisition of new expressions = **L**), multivariate normal, transformed so the *sample* d_z equal the paper's exactly.
  Assumed correlations: 0.6 among the three E outcomes; `affect_learning_corr` between E and L (unknown; default 0).
  E is the mean of the three E d_z. Case 1 measured neither B nor P, so those weights are dropped for the Case 1
  decision (and the card reports how much of your weight that was).
- Case 2: pre score and change for knowledge, competence, intention, with exact sample means/SDs; the pre–change
  correlation is implied by the reported T0 and T1 SDs and the SD of change (Δ / d_z; for intention, from its 95% CI).
  Engagement is a latent normal censored at 7 so the observed mean/SD are 6.32/0.63; its latent correlations with
  gains are calibrated so the *observed* correlations are .24 (knowledge), .05 (competence), .26 (intention).
  Assumed: knowledge–competence change r = 0.5, other change correlations 0.2, pre-score correlations 0.3–0.4.
- Case 2 "success" by class: E = (6.32 − 4)/0.63 (distance above the scale midpoint), L = mean of the two d_z,
  B = intention d_z, P = `retention` × L (an assumption; T2 is ongoing).

### Paper headline numbers (quote exactly)
- Case 1 (n = 49): interest d_z = **0.64**, 95% CI [0.35, 0.92]; enjoyment of interaction **0.61** [0.32, 0.89];
  overall enjoyment **0.50** [0.21, 0.78]; perceived acquisition of new expressions **-0.55** [-0.84, -0.27].
- Case 2 (n = 37): engagement M = **6.32**, SD = 0.63 (seven-point scale); perceived knowledge 4.37 (SD 0.70) → 5.45
  (SD 0.53), Δ = 1.07, d_z = **1.53**; competence 4.07 (0.79) → 5.49 (0.69), Δ = 1.41, d_z = **1.99**; intention 5.97
  (0.83) → 6.00 (0.88), Δ = 0.03, d_z = **0.03**, p ≈ .85.
- Engagement vs individual gains: r ≈ **.24** (knowledge), **.26** (intention), **.05** (competence); exploratory.
- Small internal rounding inconsistency: 5.45 − 4.37 = 1.08 and 5.49 − 4.07 = 1.42, vs reported Δ 1.07 and 1.41.
  The synthetic data match the reported Δ and pre means, so T1 means come out 5.44 and 5.48.

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
| Weight: engagement (E) | `{{w_engagement}}` | `0.25` | How much you value engagement (interest, enjoyment). Weights are renormalized to sum to 1 |
| Weight: learning (L) | `{{w_learning}}` | `0.25` | How much you value learning-related outcomes (acquisition, knowledge, competence) |
| Weight: intention (B) | `{{w_intention}}` | `0.25` | How much you value behavioural intention / action |
| Weight: persistence (P) | `{{w_persistence}}` | `0.25` | How much you value durable change over time |
| Retention (assumed) | `{{retention}}` | `0.5` | Your assumption: fraction of the Case 2 learning effect still present at follow-up (paper: T2 ongoing) |
| Affect–learning correlation | `{{affect_learning_corr}}` | `0` | Assumed correlation between a learner's engagement benefit and learning benefit in Case 1 (−0.5 … 0.8) |
| Engagement scale top | `{{engagement_ceiling}}` | `7` | Top of the engagement scale (7 = paper). Raise it (e.g. 10) to remove the ceiling and test the "proxy saturation" idea |
| Case 1 sample size | `{{n_case1}}` | `49` | Learners in the synthetic crossover (paper: 49) |
| Case 2 sample size | `{{n_case2}}` | `37` | Learners in the synthetic card-game study (paper: 37) |
| Seed | `{{seed}}` | `3` | Random seed |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json` (JSON numbers; if a value still looks like an unsubstituted `{{…}}` placeholder use the
table default):

```json
{"w_engagement": {{w_engagement}}, "w_learning": {{w_learning}}, "w_intention": {{w_intention}},
 "w_persistence": {{w_persistence}}, "retention": {{retention}}, "affect_learning_corr": {{affect_learning_corr}},
 "engagement_ceiling": {{engagement_ceiling}}, "n_case1": {{n_case1}}, "n_case2": {{n_case2}}, "seed": {{seed}},
 "runbook_url": ""}
```

Validate before running: weights must be ≥ 0 and not all zero (else 0.25 each); clamp `retention` to [0, 1],
`affect_learning_corr` to [−0.5, 0.8], `engagement_ceiling` to [7, 20], `n_case1` and `n_case2` to [10, 2000].
Record any correction as a caveat.

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

Expected: about 1 second. Ends with a `done:` line (Case 1 winner and flip point, proxy capture rate, Case 2 E vs B).

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers copied from `results.json`.
  Usually: which condition the participant's weights pick and how close it is to flipping (`case1.winner`,
  `case1.p_winner`, `case1.flip_learning_share`), or how weak engagement is as a proxy (`case2.proxy_capture`).
- **idea**: (1) legitimate outcomes can point to different "best" interventions; (2) choosing what the AI optimizes is a
  stated, normative decision (keep E, L, B, P distinct); (3) immediate responses are not persistence (temporal
  accountability).
- **findings**: (1) Case 1: E and L d_z, the winner under the participant's weights (`weights_E_L_renormalized`),
  `p_winner` across bootstrap resamples, the flip point, and `unmeasured_weight_share` (weight on outcomes Case 1 never
  measured); (2) Case 2 proxy: `proxy_capture["7"]` vs chance 1/3, `share_at_scale_top_7pt`, and from
  `proxy_capture_curve` how strong the correlation would need to be before engagement finds most top gainers; say
  plainly whether removing the ceiling (`proxy_capture["latent"]`) helps; (3) Case 2's four numbers
  (`effect_by_class`): engagement looks enormous, intention barely moves, and persistence is only an assumption.
- Plain words: "d_z" = average within-person difference divided by its SD; "bootstrap" = re-running the comparison on
  resampled learners.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `w_engagement, w_learning, w_intention,
  w_persistence, retention, affect_learning_corr, engagement_ceiling, n_case1, n_case2, seed`. Good contrasts: a
  learning-leaning weighting just past the flip (e.g. `w_learning` 0.3 with `w_engagement` 0.25); a larger study
  (`n_case1` 200) to see how certainty changes at the same weights; `engagement_ceiling` 10.
- **caveats** (2–4): all learners are synthetic, calibrated to the paper's summary statistics (not the authors' data);
  unreported correlations are assumptions; persistence is the participant's assumption (T2 ongoing); outcomes are
  self-reports, as the paper notes.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: weights, Case 1 winner/flip, proxy capture, Case 2 class effects, headline).

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
python3 - "{{results_dir}}" "w_engagement,w_learning,w_intention,w_persistence,retention,affect_learning_corr,engagement_ceiling,n_case1,n_case2,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} w_engagement,w_learning,w_intention,w_persistence,retention,affect_learning_corr,engagement_ceiling,n_case1,n_case2,seed 240 checklist.json
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
"""What should the AI optimize? — SMASH 2026 paper #19 (Takuji Takemoto).

The paper's data are not public. This script builds SYNTHETIC learners calibrated to the paper's reported
statistics and asks the paper's question with the participant's own outcome weights over
Engagement (E), Learning (L), Behavioural intention (B) and Persistence (P):

  Case 1 (STEAM crossover, n = 49): paired gamified - conventional differences for interest, enjoyment of
    interaction, overall enjoyment (E) and perceived acquisition of new expressions (L), generated so the sample
    d_z equal the paper's exactly. Bootstrap -> which condition "wins" under your weights, and where it flips.
  Case 2 (disaster-preparedness card game, n = 37): T0/T1 perceived knowledge, competence (L) and intention (B)
    with the paper's means/SDs/d_z, plus engagement (E) censored at the top of the 7-point scale and correlated
    with gains at the paper's r. Can an AI that watches engagement find the learners who gained most?

usage: python experiment.py params.json outdir
"""
import json, sys, time
from math import erf, exp, pi, sqrt
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(int(P["seed"]))
W = np.array([float(P[k]) for k in ["w_engagement", "w_learning", "w_intention", "w_persistence"]])
W = np.clip(W, 0, None); W = W / W.sum() if W.sum() > 0 else np.full(4, 0.25)
RET = float(P["retention"]); RHO_AL = float(P["affect_learning_corr"]); CEIL = float(P["engagement_ceiling"])
N1, N2 = int(P["n_case1"]), int(P["n_case2"]); NBOOT = 4000


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def exact_mvn(n, mean, sd, corr, r):
    """n draws whose SAMPLE mean, SD and correlation equal the targets exactly (whiten, then re-colour)."""
    k = len(mean); X = r.standard_normal((n, k)); X -= X.mean(0)
    L = np.linalg.cholesky(np.cov(X, rowvar=False)); X = X @ np.linalg.inv(L).T          # sample cov = I
    C = np.asarray(corr) * np.outer(sd, sd)
    return X @ np.linalg.cholesky(C).T + np.asarray(mean)


def near_pd(C, eps=1e-6):
    v, Q = np.linalg.eigh(C); C2 = Q @ np.diag(np.maximum(v, eps)) @ Q.T
    d = np.sqrt(np.diag(C2)); return C2 / np.outer(d, d)


def dz(x):
    return x.mean(0) / x.std(0, ddof=1)


# ======================================================================= Case 1: STEAM crossover
C1_NAMES = ["Interest", "Enjoyment of interaction", "Overall enjoyment", "Acquisition of new expressions"]
C1_DZ = np.array([0.64, 0.61, 0.50, -0.55])          # paper: gamified - conventional, d_z
C1_CI = ["[0.35, 0.92]", "[0.32, 0.89]", "[0.21, 0.78]", "[-0.84, -0.27]"]
corr1 = np.array([[1, .6, .6, RHO_AL], [.6, 1, .6, RHO_AL], [.6, .6, 1, RHO_AL], [RHO_AL, RHO_AL, RHO_AL, 1]], float)
corr1 = near_pd(corr1)
D1 = exact_mvn(N1, C1_DZ, np.ones(4), corr1, rng)    # difference scores in SD-of-difference units
idx = rng.integers(0, N1, (NBOOT, N1))
bz = np.stack([dz(D1[i]) for i in idx])               # NBOOT x 4 bootstrap d_z
ci1 = np.percentile(bz, [2.5, 97.5], 0).T
E1, L1 = bz[:, :3].mean(1), bz[:, 3]                  # E = mean affective d_z, L = acquisition d_z
E1_hat, L1_hat = float(dz(D1)[:3].mean()), float(dz(D1)[3])
measured = W[0] + W[1]                                # Case 1 measured only E and L
wE, wL = (W[0] / measured, W[1] / measured) if measured > 0 else (0.5, 0.5)
U1 = wE * E1 + wL * L1
p_gam = float((U1 > 0).mean()); U1_hat = wE * E1_hat + wL * L1_hat
shares = np.linspace(0, 1, 101)
p_curve = np.array([((1 - s) * E1 + s * L1 > 0).mean() for s in shares])
flip_share = float(E1_hat / (E1_hat - L1_hat))      # learning share where U1_hat = 0
winner = "gamified" if U1_hat > 0 else "conventional"
log(f"case 1: n={N1}; E d_z {E1_hat:.3f}, L d_z {L1_hat:.3f}; your weights -> {winner} (P = {max(p_gam, 1 - p_gam):.2f}); "
    f"flip at learning share {flip_share:.3f}")

# ======================================================================= Case 2: disaster-preparedness card game
# paper: knowledge 4.37 (0.70) -> 5.45 (0.53), Δ 1.07, d_z 1.53; competence 4.07 (0.79) -> 5.49 (0.69), Δ 1.41, d_z 1.99;
#        intention 5.97 (0.83) -> 6.00 (0.88), Δ 0.03, d_z 0.03; engagement 6.32 (0.63); r(E, ΔK) .24, r(E, ΔB) .26, r(E, ΔC) .05
C2 = {"knowledge": (4.37, 0.70, 5.45, 0.53, 1.07, 1.53), "competence": (4.07, 0.79, 5.49, 0.69, 1.41, 1.99),
      "intention": (5.97, 0.83, 6.00, 0.88, 0.03, 0.03)}
pre_mu, pre_sd, d_mu, d_sd, r_pre_d = [], [], [], [], []
for k, (m0, s0, m1, s1, dl, d) in C2.items():
    sdd = dl / d if d > 0.1 else 0.87          # intention: SD of change from the 95% CI [-0.26, 0.32], n = 37
    cov = (s1 ** 2 - s0 ** 2 - sdd ** 2) / 2   # implied by var(post) = var(pre) + var(Δ) + 2 cov(pre, Δ)
    pre_mu.append(m0); pre_sd.append(s0); d_mu.append(dl); d_sd.append(sdd); r_pre_d.append(float(np.clip(cov / (s0 * sdd), -0.95, 0.95)))
post_sd = [v[3] for v in C2.values()]
implied_prepost_r = [float((s0 ** 2 + rp * s0 * sd_) / (s0 * s1)) for s0, s1, sd_, rp in zip(pre_sd, post_sd, d_sd, r_pre_d)]


def ncdf(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def censored_moments(mu, sig, c):
    """Mean and SD of min(X, c) for X ~ N(mu, sig)."""
    a = (c - mu) / sig; Phi = ncdf(a); phi = exp(-a * a / 2) / sqrt(2 * pi)
    m = mu * Phi - sig * phi + c * (1 - Phi)
    ex2 = (mu ** 2 + sig ** 2) * Phi - sig * (mu + c) * phi + c * c * (1 - Phi)
    return m, sqrt(max(ex2 - m * m, 1e-12))


# latent engagement (mu, sigma) such that, censored at 7 (the scale top), mean = 6.32 and SD = 0.63
best = None
for mu in np.arange(6.0, 9.0, 0.01):
    for sg in np.arange(0.4, 2.5, 0.01):
        m, s = censored_moments(mu, sg, 7.0)
        e = (m - 6.32) ** 2 + (s - 0.63) ** 2
        if best is None or e < best[0]:
            best = (e, mu, sg)
E_MU, E_SG = float(best[1]), float(best[2])
share_at_top = 1 - ncdf((7 - E_MU) / E_SG)
TARGET_R = np.array([0.24, 0.05, 0.26])             # r(E, ΔK), r(E, ΔC), r(E, ΔB) observed on the 7-point scale


def case2_corr(r_e):
    # order: preK, dK, preC, dC, preB, dB, E_latent ; cross-outcome links are assumptions (stated on the card)
    C = np.eye(7)
    for j in range(3):
        C[2 * j, 2 * j + 1] = C[2 * j + 1, 2 * j] = r_pre_d[j]
    for a, b, v in [(0, 2, .4), (0, 4, .3), (2, 4, .3), (1, 3, .5), (1, 5, .2), (3, 5, .2)]:
        C[a, b] = C[b, a] = v
    for j in range(3):
        C[2 * j + 1, 6] = C[6, 2 * j + 1] = r_e[j]
    return near_pd(C)


def draw_case2(n, r_e, r, exact=True):
    mean = [pre_mu[0], d_mu[0], pre_mu[1], d_mu[1], pre_mu[2], d_mu[2], E_MU]
    sd = [pre_sd[0], d_sd[0], pre_sd[1], d_sd[1], pre_sd[2], d_sd[2], E_SG]
    C = case2_corr(r_e)
    if exact:
        return exact_mvn(n, mean, sd, C, r)
    return r.multivariate_normal(mean, C * np.outer(sd, sd), n)


def observed_E(x, ceil):
    return np.clip(np.round(x * 6) / 6, 1, ceil)       # 6-item mean on a 1..ceil scale


# calibrate latent r(E, gains) so that, after the 7-point ceiling, the observed r equal the paper's
r_lat = TARGET_R.copy(); big = np.random.default_rng(99)
for _ in range(6):
    X = draw_case2(200_000, r_lat, big, exact=False); Eo = observed_E(X[:, 6], 7.0)
    obs = np.array([np.corrcoef(Eo, X[:, j])[0, 1] for j in (1, 3, 5)])
    r_lat = np.clip(r_lat * TARGET_R / np.where(np.abs(obs) > 1e-3, obs, 1e-3), -0.9, 0.9)
log(f"case 2: latent engagement N({E_MU:.2f}, {E_SG:.2f}) censored at 7 -> {100 * share_at_top:.0f}% of learners at the top; "
    f"latent r(E, gains) {np.round(r_lat, 3).tolist()}")


def proxy_capture(X, ceil, r):
    """Share of the top-third knowledge gainers found by picking the top third on engagement (ties broken at random)."""
    Eo = observed_E(X[:, 6], ceil) + r.random(len(X)) * 1e-6
    k = max(1, round(len(X) / 3))
    topE = set(np.argsort(-Eo)[:k]); topK = set(np.argsort(-X[:, 1])[:k])
    return len(topE & topK) / k


# one exact synthetic cohort (for the figure and the reported sample statistics)
X2 = draw_case2(N2, r_lat, rng)
Eobs = observed_E(X2[:, 6], CEIL)
samp = {k: {"pre_mean": float(X2[:, 2 * j].mean()), "post_mean": float((X2[:, 2 * j] + X2[:, 2 * j + 1]).mean()),
            "delta": float(X2[:, 2 * j + 1].mean()), "d_z": float(dz(X2[:, 2 * j + 1]))} for j, k in enumerate(C2)}
samp_r = {k: float(np.corrcoef(Eobs, X2[:, 2 * j + 1])[0, 1]) for j, k in enumerate(C2)}
# replicate cohorts: how often does an engagement-watching AI find the top gainers? (7-point ceiling vs yours)
reps = {"7": [], "yours": [], "latent": []}; rr = np.random.default_rng(int(P["seed"]) + 1)
for _ in range(1500):
    X = draw_case2(N2, r_lat, rr, exact=False)
    reps["7"].append(proxy_capture(X, 7.0, rr)); reps["yours"].append(proxy_capture(X, CEIL, rr))
    reps["latent"].append(proxy_capture(X, 1e9, rr))
cap = {k: float(np.mean(v)) for k, v in reps.items()}
# how strong would the proxy have to be? capture rate vs the observed-scale correlation (latent r scaled like r_lat)
R_GRID = np.round(np.linspace(0, 0.9, 10), 2); curve = {"7": [], "none": [], "yours": []}; r_eff = []
for rg in R_GRID:
    rl = np.clip(r_lat * (rg / 0.24), -0.95, 0.95) if rg > 0 else np.zeros(3)
    Xb = draw_case2(50_000, rl, big, exact=False)             # actual observed r after PSD repair and the 7-pt ceiling
    r_eff.append(float(np.corrcoef(observed_E(Xb[:, 6], 7.0), Xb[:, 1])[0, 1]))
    out = {"7": [], "none": [], "yours": []}
    for _ in range(300):
        X = draw_case2(N2, rl, rr, exact=False)
        out["7"].append(proxy_capture(X, 7.0, rr)); out["none"].append(proxy_capture(X, 1e9, rr))
        if CEIL != 7:
            out["yours"].append(proxy_capture(X, CEIL, rr))
    for k_ in curve:
        curve[k_].append(float(np.mean(out[k_])) if out[k_] else None)
Xr = draw_case2(200_000, r_lat, big, exact=False)
r_by_ceiling = {str(c): float(np.corrcoef(observed_E(Xr[:, 6], c), Xr[:, 1])[0, 1]) for c in (7.0, 8.0, 10.0, CEIL)}
top_share_yours = float((observed_E(Xr[:, 6], CEIL) >= CEIL - 1e-9).mean())
log(f"proxy capture of top-third knowledge gainers: ceiling 7 {cap['7']:.3f}, ceiling {CEIL:g} {cap['yours']:.3f}, "
    f"no ceiling {cap['latent']:.3f} (chance 0.333)")

# Case 2 'success' by outcome class (standardized): E vs scale midpoint, L = mean d_z(K, C), B = d_z(intention), P = assumed
d_E = (6.32 - 4.0) / 0.63
d_L = (1.53 + 1.99) / 2
d_B = 0.03
d_P = RET * d_L
U2 = float(W @ np.array([d_E, d_L, d_B, d_P]))

res = {"params": P, "weights_normalized": W.tolist(), "case1": {
    "n": N1, "names": C1_NAMES, "paper_dz": C1_DZ.tolist(), "sample_dz": dz(D1).tolist(), "boot_ci": ci1.tolist(),
    "E_dz": E1_hat, "L_dz": L1_hat, "weights_E_L_renormalized": [wE, wL], "unmeasured_weight_share": float(W[2] + W[3]),
    "utility": U1_hat, "winner": winner, "p_gamified_wins": p_gam, "p_winner": max(p_gam, 1 - p_gam),
    "flip_learning_share": flip_share, "your_learning_share": wL},
    "case2": {"n": N2, "sample": samp, "sample_r_engagement_gain": samp_r, "latent_engagement_mu_sd": [E_MU, E_SG],
              "share_at_scale_top_7pt": share_at_top, "share_at_top_your_ceiling": top_share_yours,
              "latent_r_engagement_gain": r_lat.tolist(), "r_engagement_knowledge_by_ceiling": r_by_ceiling,
              "proxy_capture": cap, "proxy_capture_curve": {"r_observed": r_eff, **curve}, "proxy_capture_chance": 1 / 3, "implied_r_pre_delta": r_pre_d, "implied_r_pre_post": implied_prepost_r,
              "sd_of_change": d_sd, "effect_by_class": {"E": d_E, "L": d_L, "B": d_B, "P_assumed": d_P},
              "proxy_gap_E_minus_B": d_E - d_B, "utility": U2}}

# ======================================================================= figures
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#adb5bd"

fig, ax = plt.subplots(figsize=(6.4, 2.9))
y = np.arange(4)[::-1]
paper_lo = [0.35, 0.32, 0.21, -0.84]; paper_hi = [0.92, 0.89, 0.78, -0.27]
for i in range(4):
    col = BLUE if i < 3 else ACC
    ax.plot([paper_lo[i], paper_hi[i]], [y[i] + 0.15] * 2, color=MUTED, lw=3, solid_capstyle="butt")
    ax.plot(ci1[i], [y[i] - 0.15] * 2, color=col, lw=2)
    ax.scatter([C1_DZ[i]], [y[i] + 0.15], color=MUTED, s=25, zorder=3)
    ax.scatter([dz(D1)[i]], [y[i] - 0.15], color=col, s=30, zorder=3)
ax.axvline(0, color=INK, lw=0.8)
ax.set_yticks(y); ax.set_yticklabels([n + (" (L)" if i == 3 else " (E)") for i, n in enumerate(C1_NAMES)], fontsize=8.5)
ax.set_xlabel("d_z  (← favours conventional   |   favours gamified →)")
ax.plot([], [], color=MUTED, lw=3, label="paper 95% CI"); ax.plot([], [], color=INK, lw=2, label="synthetic bootstrap 95% CI")
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "fig_case1_effects.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.9))
ax.fill_between(shares, 0, p_curve, color=BLUE, alpha=0.15, lw=0)
ax.plot(shares, p_curve, color=BLUE, lw=2, label="P(gamified wins) over bootstrap resamples")
ax.axhline(0.5, color=MUTED, lw=0.8, ls="--"); ax.axvline(flip_share, color=INK, lw=0.8, ls=":")
ax.text(flip_share + 0.01, 0.92, f"flips at {flip_share:.2f}", fontsize=8.5)
ax.scatter([wL], [p_gam], marker="*", s=180, color=ACC, zorder=5, label="your weights")
ax.set_xlabel("share of weight on learning (L) vs engagement (E)"); ax.set_ylabel("P(gamified preferred)")
ax.set_ylim(0, 1.02); ax.set_xlim(0, 1); ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig(OUT / "fig_flip.png", dpi=160); plt.close(fig)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})
jit = rng.uniform(-0.04, 0.04, N2)
a1.scatter(Eobs + jit, X2[:, 1], s=22, color=BLUE, alpha=0.85, edgecolor="white", lw=0.4)
a1.axvline(7.0, color=ACC, lw=0.8, ls=":")
a1.set_xlabel(f"engagement (scale top = {CEIL:g}; dotted = 7)"); a1.set_ylabel("knowledge gain T0→T1")
a1.set_title(f"synthetic cohort, r = {samp_r['knowledge']:.2f}", fontsize=9)
for key, col, lab in [("7", MUTED, "7-point scale (paper)"), ("none", BLUE, "no ceiling")] + \
        ([("yours", ACC, f"ceiling {CEIL:g} (yours)")] if CEIL != 7 else []):
    a2.plot(r_eff, curve[key], "o-", ms=3, color=col, label=lab)
a2.axhline(1 / 3, color=INK, lw=0.8, ls="--"); a2.text(0.45, 1 / 3 - 0.02, "chance", fontsize=8, ha="center", va="top")
a2.axvline(0.24, color=ACC, lw=0.8, ls=":"); a2.text(0.25, 0.95, "paper r ≈ .24", fontsize=7.5, color=ACC, va="top")
a2.set_xlabel("r(engagement, knowledge gain)", fontsize=9); a2.set_ylim(0.2, 1.0); a2.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.88))
a2.set_ylabel("top-third gainers found", fontsize=9); a2.set_title("pick top third by engagement", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "fig_proxy.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.6))
cls = ["Engagement (E)\nvs scale midpoint", "Learning (L)\nknowledge+competence", "Intention (B)", "Persistence (P)\nassumed"]
vv = [d_E, d_L, d_B, d_P]
bars = ax.barh(range(4)[::-1], vv, color=[BLUE, BLUE, ACC, MUTED], height=0.6)
bars[3].set_hatch("//"); bars[3].set_edgecolor("white")
for i, v in enumerate(vv):
    ax.text(v + 0.05, 3 - i, f"{v:.2f}" + ("  (your retention assumption)" if i == 3 else ""), va="center", fontsize=8.5)
ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(cls, fontsize=8); ax.set_xlim(0, max(vv) * 1.45)
ax.set_xlabel("standardized effect (Case 2, from the paper's numbers)")
fig.tight_layout(); fig.savefig(OUT / "fig_case2_classes.png", dpi=160); plt.close(fig)

# ======================================================================= card
tiles = [
    {"label": "Winner under your weights", "value": winner.capitalize(),
     "sub": f"in {100 * max(p_gam, 1 - p_gam):.0f}% of {NBOOT:,} bootstrap resamples (Case 1, composite {U1_hat:+.3f})", "tone": "accent"},
    {"label": "Decision flips at", "value": f"{100 * flip_share:.0f}% on L",
     "sub": f"you put {100 * wL:.0f}% on learning vs engagement; {100 * (W[2] + W[3]):.0f}% of your weight is on outcomes Case 1 never measured",
     "tone": "neutral"},
    {"label": "Engagement as a proxy", "value": f"{100 * cap['7']:.0f}%",
     "sub": f"of the top-third knowledge gainers found by watching engagement (chance 33%; {100 * share_at_top:.0f}% of learners hit the ceiling)",
     "tone": "warn"},
    {"label": "Same game, two verdicts", "value": f"{d_E:.2f} vs {d_B:.2f}",
     "sub": "Case 2 standardized effect: engagement vs behavioural intention", "tone": "neutral"},
]
compare = [{"metric": f"Case 1 d_z: {n}", "paper": f"{C1_DZ[i]:.2f} {C1_CI[i]}",
            "yours": f"{dz(D1)[i]:.2f} [{ci1[i][0]:.2f}, {ci1[i][1]:.2f}]", "note": "synthetic, n = %d" % N1}
           for i, n in enumerate(C1_NAMES)]
compare += [
    {"metric": "Case 2 knowledge T0 → T1 (d_z)", "paper": "4.37 → 5.45 (d_z = 1.53)",
     "yours": f"{samp['knowledge']['pre_mean']:.2f} → {samp['knowledge']['post_mean']:.2f} (d_z = {samp['knowledge']['d_z']:.2f})", "note": "calibrated"},
    {"metric": "Case 2 competence T0 → T1 (d_z)", "paper": "4.07 → 5.49 (d_z = 1.99)",
     "yours": f"{samp['competence']['pre_mean']:.2f} → {samp['competence']['post_mean']:.2f} (d_z = {samp['competence']['d_z']:.2f})", "note": "calibrated"},
    {"metric": "Case 2 intention T0 → T1 (d_z)", "paper": "5.97 → 6.00 (d_z = 0.03)",
     "yours": f"{samp['intention']['pre_mean']:.2f} → {samp['intention']['post_mean']:.2f} (d_z = {samp['intention']['d_z']:.2f})", "note": "calibrated"},
    {"metric": "r(engagement, gain): knowledge / intention / competence", "paper": "r ≈ .24 / .26 / .05",
     "yours": f"{samp_r['knowledge']:.2f} / {samp_r['intention']:.2f} / {samp_r['competence']:.2f}",
     "note": f"one synthetic cohort, engagement scale 1–{CEIL:g}"},
    {"metric": "Persistence (T2)", "paper": "T2 is ongoing; at present, persistence cannot yet be established",
     "yours": f"assumed retention {RET:g}", "note": "your assumption, not data"},
]
card = {"paper": {"num": 19, "title": "When Engagement Is Not Enough: What Should AI Optimize in Gamified Education?",
                  "authors": "Takuji Takemoto", "url": "https://drive.google.com/file/d/1L1jl5c3v9hjZtZ1QofMdEY-6dHQ-uJSn/view?usp=sharing", "affiliation": "University of Fukui"},
        "inputs": {"weights E/L/B/P": " / ".join(f"{x:.2f}" for x in W), "retention (assumed)": RET,
                   "affect–learning corr.": RHO_AL, "engagement scale top": CEIL, "n Case 1": N1, "n Case 2": N2,
                   "seed": P["seed"], "data": "synthetic, calibrated to the paper"},
        "tiles": tiles,
        "figures": [
            {"path": "fig_case1_effects.png", "title": "Case 1: which condition is 'better' depends on the outcome",
             "caption": "Grey = the paper's d_z and 95% CI. Coloured = this run's synthetic learners (generated so the sample d_z "
                        "match exactly) with bootstrap CIs. Blue = engagement-type outcomes (E), orange = learning (L)."},
            {"path": "fig_flip.png", "title": "Where does the decision flip?",
             "caption": "Probability that the gamified condition comes out ahead as the weight moves from engagement to "
                        "learning. The star is your weighting (B and P weights dropped: Case 1 did not measure them)."},
            {"path": "fig_proxy.png", "title": "Case 2: can an AI find who learned by watching engagement?",
             "caption": "Left: one synthetic cohort, engagement vs perceived-knowledge gain (note the pile-up at the scale top). "
                        "Right: share of the top-third gainers that a system ranking learners by engagement would pick, by how "
                        "strongly engagement tracks gains (300 synthetic cohorts per point)."},
            {"path": "fig_case2_classes.png", "title": "Case 2: one intervention, four 'success' numbers",
             "caption": "Standardized effects from the paper's reported numbers. Persistence is not measured yet (T2 ongoing): "
                        "the hatched bar is your retention assumption times the learning effect."}],
        "compare": compare, "runbook": {"name": "smash-19-engagement-not-enough", "url": P.get("runbook_url", "")}}
(OUT / "card_data.json").write_text(json.dumps(card, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: Case 1 winner {winner} (P {max(p_gam, 1 - p_gam):.2f}, flip at L share {flip_share:.3f}); "
    f"proxy capture {cap['7']:.3f} vs chance 0.333; Case 2 E {d_E:.2f} vs B {d_B:.2f}")
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
