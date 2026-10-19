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
    skill_name: smash-20-contamination-audit
    confidence: high
---

# Contamination Audit Lab: Evade the Detectors, Then Get Caught (SMASH 2026 · Paper #20)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Towards Robust, Performance-Based Contamination Detection for LLMs"** (Allenna Tang, Jackie Cheung).
Read the paper: https://drive.google.com/file/d/1eG9T_MAj1dUJLBNzRlAUpSu32xIt5zom/view?usp=sharing

The paper's two claims:
1. **Current contamination detectors can be cheaply evaded.** An *argmax-preserving logit transform* reshapes the
   token probabilities on contaminated (member) benchmark items to look like unseen items, without changing a
   single benchmark answer. On Llama-3.1-8B-Instruct fine-tuned on MMLU items, Min-K%++, Min-K%, LOSS and ZLIB fall
   from near-perfect detection to chance.
2. **A performance-based detector is immune by construction.** Calibrate item difficulty and discrimination with
   a 2PL Item Response Theory model on a population of 102 LLMs, estimate the audited model's ability θ̂, and flag
   items where it does better than predicted: residual `r_j = u_j − p_j(θ̂)` with `p_j(θ) = logistic(a_j(θ − b_j))`.
   It reads only right/wrong answers, so the transform cannot touch it.

The participant plays both sides in a transparent, synthetic re-enactment of the experiment: choose how strongly the
model is contaminated, how able it is, and how big the benchmark and model population are. The run:
calibrates an IRT item bank; contaminates an audited model; computes the four confidence detectors from simulated
token-probability rows; applies the paper's transform φ row by row; scores the IRT-residual detector; and then asks
the question the paper implies: **what would an adversary have to give up to beat the IRT detector too?**
Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment itself takes seconds.

### The transform φ (paper §3.3, App. A), as implemented
At each position the row of probabilities is modified by resetting one target token to probability α and rescaling all
other tokens by a common factor `(1 − α)/(1 − p_t)` (relative probabilities preserved; still a valid distribution).
At non-answer positions the target is the actual next token and α is drawn from the empirical non-member confidence
distribution. At the answer position the target is the chosen option w; it is reset the same way, the other options are
clamped strictly below it, and the row is renormalized, so w stays the unique argmax. Draws are seeded on the item, so
repeated queries return identical outputs.

### Paper headline numbers (quote exactly)
- AUROC before → after evasion: Min-K%++ **0.99 → 0.48**, Min-K% **0.93 → 0.54**, LOSS **0.99 → 0.54**,
  ZLIB **0.99 → 0.45**, IRT-residual **0.68 → 0.68** (ΔAUROC = 0.00).
- Control (uncontaminated base model): IRT AUROC 0.5016 (95% CI [0.487, 0.516], p = 0.495); contaminated 0.6781 (p = 0.003).
- Contamination: member accuracy 0.5996 → 0.9908 (6 epochs LoRA); non-member 0.5957 → 0.6622.
- MMLU split |M| = 2,812, |U| = 2,812, |C| = 8,418; item parameters from Fluid Benchmarking (102 LMs).
- Limitation: on very easy items r ≈ 0, so contamination there is undetectable (but also inflates the score least).

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
| Contamination strength | `{{contamination}}` | `0.97` | Fraction of the member items the model used to get wrong that contamination makes it answer right (paper: member accuracy 0.60 → 0.99 ≈ 0.97). Try `0.3` for light contamination |
| Model ability | `{{model_ability}}` | `0.3` | Audited model's true ability θ on the population scale (−2 weak … +2 strong) |
| Memorization boost | `{{memorization_boost}}` | `1.0` | How much training sharpens next-token probabilities on member text (drives the confidence detectors) |
| Member items | `{{n_member_items}}` | `1200` | Contaminated items |M| (= unseen items |U|) |
| Calibration items | `{{n_calibration_items}}` | `3600` | Items used only to estimate θ̂ |
| Model population | `{{n_population}}` | `102` | LLMs used to calibrate the IRT item bank (paper: 102) |
| Seed | `{{seed}}` | `7` | Random seed |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json` (JSON numbers; if a value still looks like an unsubstituted `{{…}}` placeholder use the
table default). Clamp: `contamination` to [0, 1], `model_ability` to [−3, 3], `memorization_boost` to [0, 4],
`n_member_items` to [200, 3000], `n_calibration_items` to [500, 8000], `n_population` to [20, 300]; record any clamp as a caveat.

```json
{"contamination": {{contamination}}, "model_ability": {{model_ability}}, "memorization_boost": {{memorization_boost}},
 "n_member_items": {{n_member_items}}, "n_calibration_items": {{n_calibration_items}}, "n_population": {{n_population}},
 "seed": {{seed}}, "runbook_url": ""}
```

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
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 240 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: a few seconds. Ends with a `done:` line listing every detector's AUROC before → after.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers copied from `results.json`,
  typically the confidence detectors' collapse vs the IRT detector holding, or the sandbagging cost.
- **idea**: the paper's two claims plus why "performance-based" is robust, in plain language.
- **findings**: (1) the evasion: before/after AUROCs vs the paper's Table 1, and `answers_changed_by_evasion` (should
  be 0); (2) the IRT detector: AUROC and p-value vs the uncontaminated control (`irt_control_auroc`); (3) the trade-off
  (`sandbag_to_chance`): to push IRT to ≈ chance the adversary must give back `fraction_given_back` of its gains,
  losing `points_lost` benchmark points and keeping only `inflation_kept_pct`% of the inflation; (4) the easy-item blind
  spot (`irt_by_difficulty`). Be clear that the IRT AUROC (~0.7) is modest; its strength is robustness, not accuracy.
- **try_next**: 2–3 contrasting runs with exact values using only the keys `contamination, model_ability,
  memorization_boost, n_member_items, n_calibration_items, n_population, seed`. Good contrasts: light contamination
  (`contamination` 0.3); a very strong model (`model_ability` 2.0, where most items are easy); a small calibration
  population (`n_population` 20).
- **caveats**: synthetic re-enactment (simulated population, items and token probabilities; not MMLU or Llama);
  sandbagging is this runbook's extension, not a result in the paper; AUROC levels depend on the simulation settings.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, AUROC table, control, sandbag cost, headline).

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
python3 - "{{results_dir}}" "contamination,model_ability,memorization_boost,n_member_items,n_calibration_items,n_population,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} contamination,model_ability,memorization_boost,n_member_items,n_calibration_items,n_population,seed 240 checklist.json
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
"""Contamination audit lab — SMASH 2026 paper #20 (Allenna Tang, Jackie Cheung).

A synthetic, fully transparent re-enactment of the paper's experiment:
  1. calibrate a 2PL IRT item bank on a population of LLMs (simulated response matrix);
  2. contaminate an audited model on member items M (a `contamination` fraction of its wrong member answers become right);
  3. score four confidence-based detectors (LOSS, ZLIB, Min-K%, Min-K%++) from token probability rows;
  4. apply the paper's argmax-preserving confidence-masking transform phi and re-score;
  5. score the IRT-residual detector r_j = u_j - p_j(theta_hat), which only reads right/wrong.
Then explore what an adversary must give up to beat the IRT detector ("sandbagging").

usage: python experiment.py params.json outdir
"""
import json, sys, time, zlib
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(int(P["seed"]))

N_POP = int(P["n_population"])        # paper: 102 LMs (Fluid Benchmarking)
N_MEM = int(P["n_member_items"])      # paper: 2,812
N_UNS = N_MEM                         # paper: |U| = |M|
N_CAL = int(P["n_calibration_items"]) # paper: 8,418
N_ITEMS = N_MEM + N_UNS + N_CAL
CONTAM = float(P["contamination"])    # fraction of wrongly-answered member items that training makes right
                                      # (paper: member accuracy 0.60 -> 0.99, i.e. ~0.97)
THETA = float(P["model_ability"])
V, K_OPT, DELTA, MINK = 64, 4, 1e-3, 0.2


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def logistic(x):
    return 1 / (1 + np.exp(-x))


def auroc(scores, labels):
    """P(random member scores above random non-member), ties = 1/2 (Mann-Whitney)."""
    s = np.asarray(scores); y = np.asarray(labels).astype(bool)
    order = np.argsort(s, kind="mergesort"); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, ranks); ranks = (sums / cnt)[inv]
    n1, n0 = y.sum(), (~y).sum()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


# ------------------------------------------------------------------ 1. IRT calibration on a population
a_true = np.exp(rng.normal(0.0, 0.35, N_ITEMS))           # discrimination
b_true = rng.normal(-0.4, 1.1, N_ITEMS)                    # difficulty
theta_pop = rng.normal(0, 1, N_POP)
U_pop = rng.random((N_POP, N_ITEMS)) < logistic(a_true * (theta_pop[:, None] - b_true))


def calibrate(U, iters=60):
    """Joint maximum likelihood for the 2PL (alternating Newton steps; abilities standardized each round)."""
    n_p, n_i = U.shape; th = np.zeros(n_p); a = np.ones(n_i); b = np.zeros(n_i)
    pc = U.mean(1).clip(0.02, 0.98); th = np.log(pc / (1 - pc)); th = (th - th.mean()) / th.std()
    for _ in range(iters):
        for _inner in range(2):
            p = logistic(a * (th[:, None] - b)); r = U - p; w = p * (1 - p)
            # d logL / d b = -a * sum(r); Newton step (observed information a^2 * sum(w))
            b = np.clip(b - (a * r).sum(0) / ((a ** 2 * w).sum(0) + 1e-6), -6, 6)
            p = logistic(a * (th[:, None] - b)); r = U - p; w = p * (1 - p); x = th[:, None] - b
            ga = (x * r).sum(0) - (np.log(a)) / a; ha = (x ** 2 * w).sum(0) + 1e-6
            a = np.clip(a + ga / ha, 0.2, 4)
        p = logistic(a * (th[:, None] - b)); r = U - p; w = p * (1 - p)
        th = np.clip(th + (a * r).sum(1) / ((a ** 2 * w).sum(1) + 1e-6), -5, 5)
        th = (th - th.mean()) / th.std()
    return a, b


def ability(u, a, b):
    th = 0.0
    for _ in range(50):
        p = logistic(a * (th - b)); th += (a * (u - p)).sum() / ((a ** 2 * p * (1 - p)).sum() + 1e-6)
        th = float(np.clip(th, -6, 6))
    return th


a_hat, b_hat = calibrate(U_pop.astype(float))
log(f"calibrated 2PL item bank on {N_POP} models x {N_ITEMS} items "
    f"(corr b: {np.corrcoef(b_hat, b_true)[0, 1]:.3f}, a: {np.corrcoef(a_hat, a_true)[0, 1]:.3f})")

# Stratified-by-difficulty split into members M, unseen U, calibration C (paper §5.1):
# within each difficulty decile, items are shuffled and dealt to M / U / C in the target proportions.
split = np.empty(N_ITEMS, dtype="<U1")
for dec in np.array_split(np.argsort(b_true), 10):
    dec = rng.permutation(dec); n = len(dec)
    nm, nu = round(n * N_MEM / N_ITEMS), round(n * N_UNS / N_ITEMS)
    split[dec[:nm]], split[dec[nm:nm + nu]], split[dec[nm + nu:]] = "M", "U", "C"
M, Un, C = split == "M", split == "U", split == "C"

# ------------------------------------------------------------------ 2. audited model: base + contaminated
p_base = logistic(a_true * (THETA - b_true))
u_base = rng.random(N_ITEMS) < p_base
base_mem_acc = float(u_base[M].mean())
# contamination: each member item the base model got wrong becomes right with probability CONTAM
u_cont = u_base.copy(); flip = M & ~u_base & (rng.random(N_ITEMS) < CONTAM); u_cont[flip] = True
log(f"audited model: member acc {u_base[M].mean():.3f} -> {u_cont[M].mean():.3f}; unseen {u_cont[Un].mean():.3f}")

# ------------------------------------------------------------------ 3. token probability rows
ID = np.where(M | Un)[0]                      # detection set = M ∪ U
L = rng.poisson(55, len(ID)) + 20             # tokens of prompt + answer continuation
memb = M[ID]
MEM_BOOST = float(P["memorization_boost"])    # how much training on M sharpens next-token prediction


def rows_for_item(i, member, contaminated):
    """Return (V-dim prob rows per position, target index per position) for item ID[i]; last row = answer option."""
    r = np.random.default_rng([int(P["seed"]), int(ID[i])])
    z = r.normal(0, 1.6, (L[i], V)); tgt = r.integers(0, V, L[i])
    boost = r.normal(1.4, 1.4, L[i]) + (MEM_BOOST if (member and contaminated) else 0.0)
    z[np.arange(L[i]), tgt] += boost
    p = np.exp(z - z.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
    return p, tgt


def answer_row(i, u, member, contaminated):
    """Distribution over the K answer options at the answer position; chosen option = argmax."""
    r = np.random.default_rng([int(P["seed"]), int(ID[i]), 7])
    correct = 0; chosen = correct if u else 1 + r.integers(0, K_OPT - 1)
    z = r.normal(0, 0.8, K_OPT); z[chosen] = z.max() + abs(r.normal(1.0, 0.8)) + (3.0 if member and contaminated else 0)
    q = np.exp(z - z.max()); return q / q.sum(), chosen, correct


def detector_scores(rows_list):
    loss, zl, mink, minkpp = [], [], [], []
    for (p, tgt, q, chosen, correct) in rows_list:
        lp_t = np.log(p[np.arange(len(tgt)), tgt])
        lp_ans = np.log(q[correct])
        lp = np.r_[lp_t, lp_ans]
        loss.append(lp.mean())                                          # LOSS: higher log-lik = member
        zl.append(lp.sum() / len(zlib.compress(tgt.astype(np.uint8).tobytes())))  # ZLIB-normalized
        k = max(1, int(MINK * len(lp))); mink.append(np.sort(lp)[:k].mean())     # Min-K%
        logp = np.log(p); mu = (p * logp).sum(1); sd = np.sqrt(np.maximum((p * logp ** 2).sum(1) - mu ** 2, 1e-9))
        zz = (lp_t - mu) / sd; kk = max(1, int(MINK * len(zz))); minkpp.append(np.sort(zz)[:kk].mean())  # Min-K%++
    return {"LOSS": np.array(loss), "ZLIB": np.array(zl), "Min-K%": np.array(mink), "Min-K%++": np.array(minkpp)}


def build_rows(u):
    out = []
    for i in range(len(ID)):
        p, tgt = rows_for_item(i, memb[i], True)
        q, chosen, correct = answer_row(i, u[ID[i]], memb[i], True)
        out.append((p, tgt, q, chosen, correct))
    return out


# ------------------------------------------------------------------ 4. the evasion phi (paper §3.3, App. A)
def phi_row(p, t, alpha):
    """Reset target token t to probability alpha; rescale every other token by (1-alpha)/(1-p_t)."""
    out = p * (1 - alpha) / max(1 - p[t], 1e-12); out[t] = alpha; return out


def evade(rows_list):
    # empirical non-member confidence distributions (what an unseen item looks like)
    nm_tok = np.concatenate([r[0][np.arange(len(r[1])), r[1]] for r, m in zip(rows_list, memb) if not m])
    nm_ans = np.array([r[2][r[3]] for r, m in zip(rows_list, memb) if not m])
    out, changed = [], 0
    for i, (p, tgt, q, chosen, correct) in enumerate(rows_list):
        r = np.random.default_rng([int(P["seed"]), int(ID[i]), 99])          # deterministic in the prompt
        alphas = r.choice(nm_tok, len(tgt))
        p2 = np.array([phi_row(p[j], tgt[j], alphas[j]) for j in range(len(tgt))])
        a_star = float(r.choice(nm_ans)); a_star = max(a_star, 1 / K_OPT + DELTA)
        q2 = phi_row(q, chosen, a_star)
        others = [c for c in range(K_OPT) if c != chosen]
        q2[others] = np.minimum(q2[others], a_star - DELTA)                 # chosen stays the unique argmax
        q2 = q2 / q2.sum()
        changed += int(np.argmax(q2) != chosen)
        out.append((p2, tgt, q2, chosen, correct))
    return out, changed


rows = build_rows(u_cont)
before = detector_scores(rows)
rows_ev, n_changed = evade(rows)
after = detector_scores(rows_ev)
log(f"evasion applied to {len(ID)} items; answers changed: {n_changed}")

# ------------------------------------------------------------------ 5. IRT residual detector
th_hat = ability(u_cont[C].astype(float), a_hat[C], b_hat[C])
resid = u_cont[ID] - logistic(a_hat[ID] * (th_hat - b_hat[ID]))
th_hat_base = ability(u_base[C].astype(float), a_hat[C], b_hat[C])
resid_base = u_base[ID] - logistic(a_hat[ID] * (th_hat_base - b_hat[ID]))   # control: uncontaminated model

table = []
for name in ["Min-K%++", "Min-K%", "LOSS", "ZLIB"]:
    b4, af = auroc(before[name], memb), auroc(after[name], memb)
    table.append({"detector": name, "before": b4, "after": af, "delta": b4 - af})
irt = auroc(resid, memb)
table.append({"detector": "IRT-residual", "before": irt, "after": irt, "delta": 0.0})
irt_control = auroc(resid_base, memb)


# permutation p-value for the IRT AUROC (contaminated vs chance)
def perm_p(scores, labels, n=500):
    obs = auroc(scores, labels); r = np.random.default_rng(1)
    return float((1 + sum(auroc(scores, r.permutation(labels)) >= obs for _ in range(n))) / (n + 1))


p_irt, p_ctrl = perm_p(resid, memb), perm_p(resid_base, memb)

# ------------------------------------------------------------------ 6. adversary vs IRT: sandbagging trade-off
sandbag = []
gained = np.where(M & u_cont & ~u_base)[0]          # member items the contamination turned right
ranked = gained[np.argsort(-(u_cont[gained] - logistic(a_hat[gained] * (th_hat - b_hat[gained]))))]
for frac in np.linspace(0, 1, 11):
    u_s = u_cont.copy(); u_s[ranked[: int(round(frac * len(ranked)))]] = False   # deliberately answer wrong
    th_s = ability(u_s[C].astype(float), a_hat[C], b_hat[C])
    r_s = u_s[ID] - logistic(a_hat[ID] * (th_s - b_hat[ID]))
    sandbag.append({"fraction_given_back": float(frac), "irt_auroc": auroc(r_s, memb),
                    "benchmark_acc": float(u_s[M | Un].mean()), "member_acc": float(u_s[M].mean())})

# easy-item blind spot: residual AUROC by difficulty tercile
p_pred = logistic(a_hat[ID] * (th_hat - b_hat[ID]))
terc = np.quantile(p_pred, [1 / 3, 2 / 3]); bins = np.digitize(p_pred, terc)
by_diff = [{"bin": ["hard", "medium", "easy"][k], "auroc": auroc(resid[bins == k], memb[bins == k]),
            "mean_p": float(p_pred[bins == k].mean())} for k in range(3)]

res = {"params": P, "n_items": {"members": int(M.sum()), "unseen": int(Un.sum()), "calibration": int(C.sum())},
       "population": N_POP, "calibration_corr_b": float(np.corrcoef(b_hat, b_true)[0, 1]),
       "member_acc_base": base_mem_acc, "member_acc_contaminated": float(u_cont[M].mean()),
       "unseen_acc": float(u_cont[Un].mean()), "benchmark_acc_base": float(u_base[M | Un].mean()),
       "benchmark_acc_contaminated": float(u_cont[M | Un].mean()),
       "theta_hat": th_hat, "answers_changed_by_evasion": n_changed, "table": table,
       "irt_auroc": irt, "irt_p": p_irt, "irt_control_auroc": irt_control, "irt_control_p": p_ctrl,
       "best_confidence_before": max(t["before"] for t in table[:4]), "best_confidence_after": max(t["after"] for t in table[:4]),
       "sandbag": sandbag, "irt_by_difficulty": by_diff}
# where does the adversary get IRT back to ~chance, and at what cost?
chance = next((s for s in sandbag if s["irt_auroc"] <= 0.55), sandbag[-1])
res["sandbag_to_chance"] = {**chance, "points_lost": 100 * (res["benchmark_acc_contaminated"] - chance["benchmark_acc"]),
                            "inflation_kept_pct": 100 * (chance["benchmark_acc"] - res["benchmark_acc_base"]) /
                            max(res["benchmark_acc_contaminated"] - res["benchmark_acc_base"], 1e-9)}

# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#adb5bd"
fig, ax = plt.subplots(figsize=(6.4, 3.0))
names = [t["detector"] for t in table]; x = np.arange(len(names))
ax.bar(x - 0.2, [t["before"] for t in table], 0.38, color=MUTED, label="before evasion")
ax.bar(x + 0.2, [t["after"] for t in table], 0.38, color=[ACC] * 4 + [BLUE], label="after evasion")
for i, t in enumerate(table):
    ax.text(i + 0.2, t["after"] + 0.02, f"{t['after']:.2f}", ha="center", fontsize=8)
ax.axhline(0.5, color=INK, ls="--", lw=1); ax.text(len(names) - 0.5, 0.51, "chance", fontsize=8, ha="right")
ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylim(0, 1.08); ax.set_ylabel("AUROC (member vs unseen)")
ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.13))
fig.tight_layout(); fig.savefig(OUT / "fig_auroc.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.8))
bins_ = np.linspace(-1, 1, 41)
ax.hist(resid[~memb], bins_, color=MUTED, alpha=0.9, label="unseen items")
ax.hist(resid[memb], bins_, color=ACC, alpha=0.6, label="contaminated (member) items")
ax.set_xlabel("IRT residual  r = u − p(θ̂)   (did better than its ability predicts →)"); ax.set_ylabel("items")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "fig_residuals.png", dpi=160); plt.close(fig)

fig, ax1 = plt.subplots(figsize=(6.4, 3.0))
fx = [s["fraction_given_back"] for s in sandbag]
ax1.plot(fx, [s["irt_auroc"] for s in sandbag], "o-", color=BLUE, label="IRT-residual AUROC")
ax1.axhline(0.5, color=INK, ls="--", lw=1); ax1.set_ylabel("IRT AUROC", color=BLUE); ax1.set_ylim(0.3, 1)
ax2 = ax1.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(fx, [100 * s["benchmark_acc"] for s in sandbag], "s-", color=ACC, label="benchmark accuracy")
ax2.axhline(100 * res["benchmark_acc_base"], color=ACC, ls=":", lw=1)
ax2.set_ylabel("benchmark accuracy (%)", color=ACC)
ax1.set_xlabel("Fraction of contamination gains the adversary deliberately gives back")
fig.tight_layout(); fig.savefig(OUT / "fig_sandbag.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ card data
sb = res["sandbag_to_chance"]
tiles = [
    {"label": "Best confidence detector", "value": f"{res['best_confidence_before']:.2f} → {res['best_confidence_after']:.2f}",
     "sub": "AUROC before → after the evasion", "tone": "warn"},
    {"label": "IRT-residual detector", "value": f"{irt:.2f} → {irt:.2f}", "sub": f"unchanged by construction (p = {p_irt:.3f})", "tone": "good"},
    {"label": "Benchmark answers changed by evasion", "value": f"{n_changed}", "sub": f"of {len(ID):,} audited items", "tone": "accent"},
    {"label": "Cost to beat IRT too", "value": f"−{sb['points_lost']:.1f} pts",
     "sub": f"adversary must give back {100 * sb['fraction_given_back']:.0f}% of its contamination gains", "tone": "neutral"},
]
compare = [{"metric": t["detector"] + " AUROC (before → after)",
            "paper": {"Min-K%++": "0.99 → 0.48", "Min-K%": "0.93 → 0.54", "LOSS": "0.99 → 0.54", "ZLIB": "0.99 → 0.45",
                      "IRT-residual": "0.68 → 0.68 (Δ 0.00)"}[t["detector"]],
            "yours": f"{t['before']:.2f} → {t['after']:.2f}", "note": ""} for t in table]
compare += [{"metric": "Control (uncontaminated) IRT AUROC", "paper": "0.5016, p = 0.495", "yours": f"{irt_control:.3f}, p = {p_ctrl:.3f}", "note": ""},
            {"metric": "Easy-item blind spot (IRT AUROC by difficulty)", "paper": "on very easy items r ≈ 0: contamination undetectable",
             "yours": " / ".join(f"{d['bin']} {d['auroc']:.2f}" for d in by_diff), "note": ""},
            {"metric": "Member accuracy (contamination)", "paper": "0.5996 → 0.9908",
             "yours": f"{base_mem_acc:.3f} → {res['member_acc_contaminated']:.3f}", "note": "synthetic"}]
Path(OUT / "card_data.json").write_text(json.dumps({
    "paper": {"num": 20, "title": "Towards Robust, Performance-Based Contamination Detection for LLMs",
              "authors": "Allenna Tang, Jackie Cheung", "url": "https://drive.google.com/file/d/1eG9T_MAj1dUJLBNzRlAUpSu32xIt5zom/view?usp=sharing", "affiliation": "McGill University · Mila"},
    "inputs": {"population": f"{N_POP} models", "items": f"{N_MEM:,} members / {N_UNS:,} unseen / {N_CAL:,} calibration",
               "contamination strength": CONTAM, "model ability θ": THETA, "memorization boost": MEM_BOOST, "seed": P["seed"]},
    "tiles": tiles,
    "figures": [{"path": "fig_auroc.png", "title": "The evasion: confidence detectors collapse, IRT does not",
                 "caption": "AUROC for separating contaminated (member) from unseen items. The transform reshapes token "
                            "probabilities to look like unseen items while keeping every answer's argmax."},
                {"path": "fig_residuals.png", "title": "Why IRT still sees it",
                 "caption": "The audited model answers member items better than its estimated ability predicts: positive residuals."},
                {"path": "fig_sandbag.png", "title": "What would it take to fool IRT too?",
                 "caption": "An adversary can only lower the IRT signal by answering contaminated items wrong — giving back "
                            "the very score inflation it was after (dotted line = uncontaminated accuracy)."}],
    "compare": compare, "runbook": {"name": "smash-20-contamination-audit", "url": P.get("runbook_url", "")}}, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log("done: " + "; ".join(f"{t['detector']} {t['before']:.2f}->{t['after']:.2f}" for t in table)
    + f"; control {irt_control:.3f}; sandbag cost {sb['points_lost']:.1f} pts")
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
