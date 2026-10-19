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
    skill_name: smash-16-fl-bias-propagation
    confidence: high
---

# Who Gets Hurt? Predicting Bias Propagation in Federated Learning (SMASH 2026 · Paper #16)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Tracing Bias Propagation Across Subgroups in Federated Learning"** (Tirathraj Ramburn, Afaf Taïk, Farnoosh Ghadiri).
Read the paper: https://drive.google.com/file/d/1aA6Fac9mYYJa1VoylGh4o3GgjQjDeobk/view?usp=sharing

The paper's question: in federated learning, if one hospital (client) systematically records false-negative
labels for one patient subgroup, **which subgroups at the *other* hospitals get hurt, and can we predict it
without retraining?** Its answer for logistic regression is a closed-form **propagation vector**

`v_T = α_b · π⁺_{b,T} · H⁻¹ · μ⁺_{b,T}`  and predicted decrease  `L̂_{g,T}(ρ) = ρ · (μ⁺_g)ᵀ v_T`

where α_b is the source client's weight, π⁺_{b,T} the fraction of its training rows that are positive members
of target subgroup T, μ⁺_{b,T} their mean feature vector, H the Hessian of the shared training objective, ρ the
fraction of target positives flipped to 0, and μ⁺_g the mean feature vector of a recipient group's positive
cases. A recipient's damage depends on **how far its mean projects along v_T, not on how similar it is to the
source group**, so the most-affected subgroup can be a different one entirely.

The participant chooses which subgroup is mislabelled, how badly, how different the clients are, and (optionally)
the data-generating coefficients. The run simulates the paper's federation, predicts every recipient subgroup's
damage with the formula, actually retrains to check it, and builds an **audit matrix** of all 8 possible
source errors. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment itself takes seconds.

### Setup exactly as in the paper (§3, App. B)
- 4 equally weighted clients; each with 3,000 train / 3,000 validation / 8,000 test rows; seeds 0–19.
- A ~ Bern(0.5); Z, W1, W2 ~ N(0,1); R | A ~ N(0.25(2A−1) + h·d_k, 1) with d = (0, −1, 0, 1);
  X = (1, Z, R, W1, W2); Y ~ Bern(σ(Xᵀβ)), β = (−1, 0.85, 0.90, −0.70, 0.55).
- 8 groups = A ∈ {0,1} × Z-quartile band B1–B4 (cuts −0.6745, 0, 0.6745). The model never sees A or group.
- Only client 0's labels change (nested random subsets); λ = 1e−3 (intercept unregularized).
- Training: FedAvg with full participation and one full-batch local step equals gradient descent on the weighted
  objective (paper App. B); this runbook solves that same objective with Newton's method (same optimum, faster).
- Measured effect: mean (reference − retrained) logit over unchanged positive test cases at clients 1–3.
- Agreement: Spearman rank correlation and zero-intercept slope c = ΣL·L̂ / ΣL̂²; 95% CIs from 2,000 whole-seed bootstraps.

### Paper headline numbers (quote exactly)
- IID, 30%: A1-B3 target → Spearman **0.975** [0.961, 0.987], c = **1.014**; A0-B2 → **0.968** [0.955, 0.980], c = 1.016.
- Heterogeneous: Spearman 0.931–0.974, c = 1.007–1.015; at h = 1, A1-B3 0.974, A0-B2 0.942.
- Only **45.25** (A1-B3) / **27.20** (A0-B2) labels flipped per seed = **0.377% / 0.227%** of 12,000 labels, yet every
  recipient mean decreased (480 and 2,880 group–client–seed means).
- A1-B3 error → **A1-B4** hit hardest (0.04225), **18.2%** more than A1-B3 itself (ranks 2nd).
- A0-B2 error → **A1-B1** hit hardest (0.02679), **34.9%** more than A0-B2 (ranks only 4th).
- At h = 1, A1-B3 drops 0.02486 / 0.03441 / 0.04304 at clients 1 / 2 / 3; R-component of v_T is 0.03954 (A1-B3) vs 0.00047 (A0-B2).

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
| Mislabelled subgroup | `{{target_group}}` | `A1-B3` | Source subgroup at client 0 whose positives get flipped: `A0-B1` … `A0-B4`, `A1-B1` … `A1-B4` (A = audit attribute, B = Z quartile band) |
| Flip fraction | `{{flip_fraction}}` | `0.3` | Fraction ρ of that subgroup's positive labels changed 1 → 0 (paper: 0.1–0.4) |
| Client heterogeneity | `{{heterogeneity}}` | `0` | h: shifts the mean of predictor R by h·(0, −1, 0, 1) across clients (paper: 0, 0.5, 1) |
| Clients | `{{n_clients}}` | `4` | Number of clients (2–8); client 0 is the source |
| Coefficients | `{{beta}}` | `-1,0.85,0.90,-0.70,0.55` | True β for (intercept, Z, R, W1, W2) |
| A→R association | `{{r_shift}}` | `0.25` | How strongly the audit attribute shifts predictor R (0 = A independent of features) |
| Seeds | `{{n_seeds}}` | `20` | Independent federations (paper: 20) |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json` (numbers as JSON numbers; if a value still looks like an unsubstituted `{{…}}`
placeholder, use the default from the table):

```json
{"target_group": "{{target_group}}", "flip_fraction": {{flip_fraction}}, "heterogeneity": {{heterogeneity}},
 "n_clients": {{n_clients}}, "beta": "{{beta}}", "r_shift": {{r_shift}}, "n_seeds": {{n_seeds}}, "runbook_url": ""}
```

Validate before running: `target_group` must be one of the 8 groups; clamp `flip_fraction` to [0.05, 0.9],
`n_clients` to [2, 8], `n_seeds` to [5, 50]; `beta` must have 5 comma-separated numbers. Record any correction
as a caveat.

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

Expected: a few seconds. Ends with a `done:` line.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Then write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result *of this run*, with 1–2 numbers copied from
  `results.json`. Usually: who was hurt most vs. the mislabelled group, and how well the formula predicted it.
- **idea**: the paper's contribution in plain language for a non-specialist audience (local label errors
  propagate through the shared model; a closed-form propagation vector predicts each recipient's damage without
  retraining; damage follows projection onto that vector, not similarity to the source).
- **findings**: (1) did the prediction hold (Spearman, slope c, compared with the paper's numbers for the same
  target); (2) who was hurt most, and by how much more than the same-named group; (3) what the audit matrix says
  (`audit_sources_whose_top_victim_is_another_group` of 8; mention any negative predicted cells, meaning a
  recipient whose logit *increases*); (4) if h > 0 or β/r_shift changed, explain via the propagation vector
  components (`propagation_vector`) why clients or groups separate.
- Use plain words: "logit decrease" = "the model's score for true positive cases dropped".
- Be precise about agreement: Spearman < 1 means the predicted order is *close to*, not exactly, the measured
  order; say "closely predicted the ranking (Spearman …)", never "ranked all groups correctly".
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `target_group, flip_fraction,
  heterogeneity, n_clients, beta, r_shift, n_seeds`. Prefer ones where the audit matrix predicts a non-matching
  victim, or h = 1 with a target whose v_T has a large R component.
- **caveats**: synthetic data; logistic regression only (the paper's linear setting); a lower logit does not
  necessarily flip a prediction; Newton solve in place of FedAvg rounds (same optimum).

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, Spearman/c with CIs, most affected vs target, audit
count, headline).

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
python3 - "{{results_dir}}" "target_group,flip_fraction,heterogeneity,n_clients,beta,r_shift,n_seeds" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} target_group,flip_fraction,heterogeneity,n_clients,beta,r_shift,n_seeds 240 checklist.json
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
"""Bias propagation in federated learning — SMASH 2026 paper #16 (Ramburn, Taïk).

Simulates the paper's synthetic federation, plants a false-negative labelling error in one
subgroup at client 0, predicts every recipient subgroup's mean logit decrease with the
closed-form propagation vector (no retraining), then retrains and checks the prediction.

usage: python experiment.py params.json outdir
"""
import json, sys, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)

K = int(P["n_clients"]); N_TR, N_VA, N_TE = 3000, 3000, 8000
LAM = 1e-3
BETA = np.array([float(x) for x in str(P["beta"]).split(",")])  # (intercept, Z, R, W1, W2)
R_SHIFT = float(P["r_shift"])          # R | A ~ N(r_shift (2A − 1), 1); paper: 0.25
H_SET = float(P["heterogeneity"])      # h; client offsets d = (0, −1, 0, 1, …)
TARGET = P["target_group"]             # e.g. "A1-B3"
RHO = float(P["flip_fraction"])
SEEDS = int(P["n_seeds"])
CUTS = (-0.6745, 0.0, 0.6745)
GROUPS = [f"A{a}-B{b}" for a in (0, 1) for b in (1, 2, 3, 4)]
FEATS = ["intercept", "Z", "R", "W1", "W2"]
D_OFF = np.array([0, -1, 0, 1, -0.5, 0.5, -1.5, 1.5])[:K]


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def sigmoid(u):
    return 1 / (1 + np.exp(-u))


def make_client(rng, n, k):
    A = rng.binomial(1, 0.5, n); Z, W1, W2, eps = rng.standard_normal((4, n))
    R = R_SHIFT * (2 * A - 1) + H_SET * D_OFF[k] + eps
    X = np.c_[np.ones(n), Z, R, W1, W2]
    Y = rng.binomial(1, sigmoid(X @ BETA))
    band = np.searchsorted(CUTS, Z) + 1
    g = np.array([f"A{a}-B{b}" for a, b in zip(A, band)])
    return X, Y, g


def fit(Xs, Ys):
    """Minimise sum_k (alpha_k/n_k) sum_i logloss + (lam/2) th' D th  (paper Eq. 4) by Newton.
    FedAvg with full participation and one full-batch local step is gradient descent on this
    same objective (paper App. B), so the optimum is identical; Newton just gets there faster."""
    d = Xs[0].shape[1]; Dm = np.eye(d); Dm[0, 0] = 0
    th = np.zeros(d); a = 1 / len(Xs)
    for _ in range(50):
        g = LAM * Dm @ th; H = LAM * Dm.copy()
        for X, Y in zip(Xs, Ys):
            p = sigmoid(X @ th)
            g += a / len(Y) * X.T @ (p - Y)
            H += a / len(Y) * (X * (p * (1 - p))[:, None]).T @ X
        step = np.linalg.solve(H, g); th -= step
        if np.linalg.norm(g) < 1e-10:
            break
    return th, H


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def run_seed(seed, target, rhos):
    rng = np.random.default_rng(seed)
    clients = [{"tr": make_client(rng, N_TR, k), "va": make_client(rng, N_VA, k), "te": make_client(rng, N_TE, k)}
               for k in range(K)]
    Xs = [c["tr"][0] for c in clients]; Ys = [c["tr"][1].copy() for c in clients]
    th0, H = fit(Xs, Ys)
    # source error at client 0: positives in target group, nested random order
    X0, Y0, g0 = clients[0]["tr"]
    elig = np.where((g0 == target) & (Y0 == 1))[0]
    order = rng.permutation(elig)
    pi_plus = len(elig) / N_TR
    mu_src = X0[elig].mean(0)
    v = (1 / K) * pi_plus * np.linalg.solve(H, mu_src)              # propagation vector (Eq. 2)
    out = {"v": v, "n_elig": len(elig), "by_rho": {}}
    for rho in rhos:
        m = int(round(rho * len(elig))); flip = order[:m]
        Y0c = Y0.copy(); Y0c[flip] = 0
        th_r, _ = fit(Xs, [Y0c] + Ys[1:])
        rho_eff = m / max(len(elig), 1)
        cells = []
        for k in range(1, K):
            for gname in GROUPS:
                Xv, Yv, gv = clients[k]["va"]; Xt, Yt, gt = clients[k]["te"]
                mu_g = Xv[(gv == gname) & (Yv == 1)].mean(0)
                pred = rho_eff * mu_g @ v                                  # Eq. 3
                sel = (gt == gname) & (Yt == 1)
                meas = float(np.mean(Xt[sel] @ (th0 - th_r)))
                cells.append({"client": k, "group": gname, "pred": float(pred), "meas": meas})
        out["by_rho"][rho] = {"cells": cells, "n_changed": m, "pct_of_federation": 100 * m / (K * N_TR)}
    # audit matrix: predicted decrease at every recipient group for every possible source group (no retraining)
    Xv = np.vstack([clients[k]["va"][0] for k in range(1, K)]); Yv = np.concatenate([clients[k]["va"][1] for k in range(1, K)])
    gv = np.concatenate([clients[k]["va"][2] for k in range(1, K)])
    mu_rec = {gname: Xv[(gv == gname) & (Yv == 1)].mean(0) for gname in GROUPS}
    audit = np.zeros((len(GROUPS), len(GROUPS)))
    for i, src in enumerate(GROUPS):
        e = np.where((g0 == src) & (Y0 == 1))[0]
        vs = (1 / K) * (len(e) / N_TR) * np.linalg.solve(H, X0[e].mean(0))
        audit[i] = [RHO * mu_rec[gname] @ vs for gname in GROUPS]
    out["audit"] = audit
    return out


def summarize(cells, iid):
    if iid:  # average recipient clients -> 8 group effects (paper's IID analysis)
        agg = {}
        for c in cells:
            agg.setdefault(c["group"], []).append(c)
        return [{"client": "1-%d" % (K - 1), "group": gname, "pred": float(np.mean([x["pred"] for x in v])),
                 "meas": float(np.mean([x["meas"] for x in v]))} for gname, v in agg.items()]
    return cells


def main():
    iid = H_SET == 0
    rhos = sorted(set([0.1, 0.2, 0.3, 0.4, RHO]))
    seeds = [run_seed(s, TARGET, rhos) for s in range(SEEDS)]
    log(f"{SEEDS} seeds fitted ({len(rhos) + 1} fits each)")
    per_seed = []
    for s in seeds:
        cells = summarize(s["by_rho"][RHO]["cells"], iid)
        pr = np.array([c["pred"] for c in cells]); me = np.array([c["meas"] for c in cells])
        per_seed.append({"spearman": spearman(pr, me), "c": float(me @ pr / (pr @ pr)), "cells": cells})
    rng = np.random.default_rng(0)
    def boot(key):
        vals = np.array([x[key] for x in per_seed])
        bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(2000)]  # whole-seed bootstrap
        return float(vals.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    sp, sp_ci = boot("spearman"); c, c_ci = boot("c")
    # mean cell effects across seeds
    keys = [(x["client"], x["group"]) for x in per_seed[0]["cells"]]
    mean_cells = []
    for i, (k, gname) in enumerate(keys):
        pr = [ps["cells"][i]["pred"] for ps in per_seed]; me = [ps["cells"][i]["meas"] for ps in per_seed]
        mean_cells.append({"client": k, "group": gname, "pred": float(np.mean(pr)), "meas": float(np.mean(me)),
                           "meas_ci": [float(np.percentile(me, 2.5)), float(np.percentile(me, 97.5))]})
    ranked = sorted(mean_cells, key=lambda x: -x["meas"])
    top = ranked[0]
    # compare the most-affected cell with the target-matched group at the same recipient client (paper §4)
    tgt_best = [x for x in mean_cells if x["group"] == TARGET and x["client"] == top["client"]][0]
    all_pos = all(x["meas"] > 0 for ps in per_seed for x in ps["cells"])
    target_rank = 1 + [x["group"] for x in ranked if x["client"] == top["client"]].index(TARGET)
    v_mean = np.mean([s["v"] for s in seeds], 0)
    audit = np.mean([s["audit"] for s in seeds], 0)
    sweep = [{"rho": r, "pred": float(np.mean([np.mean([c["pred"] for c in summarize(s["by_rho"][r]["cells"], True)]) for s in seeds])),
              "meas": float(np.mean([np.mean([c["meas"] for c in summarize(s["by_rho"][r]["cells"], True)]) for s in seeds]))}
             for r in rhos]
    n_changed = float(np.mean([s["by_rho"][RHO]["n_changed"] for s in seeds]))
    pct = float(np.mean([s["by_rho"][RHO]["pct_of_federation"] for s in seeds]))
    most_hit_by_source = {GROUPS[i]: GROUPS[int(np.argmax(audit[i]))] for i in range(len(GROUPS))}
    n_self_not_top = sum(1 for k, v in most_hit_by_source.items() if k != v)
    res = {"params": P, "analysis": "IID (8 groups, recipients averaged)" if iid else f"heterogeneous h={H_SET} ({len(mean_cells)} client-subgroup cells)",
           "spearman": sp, "spearman_ci": sp_ci, "slope_c": c, "slope_c_ci": c_ci,
           "labels_changed_per_seed": n_changed, "pct_of_federation_labels": pct,
           "all_recipient_means_decreased": all_pos, "n_cell_seed_means": len(per_seed) * len(mean_cells),
           "most_affected": top, "target_matched_best": tgt_best, "target_rank": target_rank,
           "most_affected_is_target": top["group"] == TARGET,
           "most_affected_pct_more_than_target": float(100 * (top["meas"] / tgt_best["meas"] - 1)) if top["group"] != TARGET else 0.0,
           "propagation_vector": dict(zip(FEATS, map(float, v_mean))), "cells": mean_cells, "rho_sweep": sweep,
           "audit_matrix": {"sources": GROUPS, "recipients": GROUPS, "pred": audit.tolist()},
           "audit_most_hit": most_hit_by_source, "audit_sources_whose_top_victim_is_another_group": n_self_not_top}
    figures(res, mean_cells, sweep, audit)
    card(res)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    log(f"done: spearman {sp:.3f} {sp_ci}, c {c:.3f}; most affected {top['group']} (target rank {target_rank})")


def figures(res, cells, sweep, audit):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    INK, A1, A0, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#868e96"
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    mx = max(max(x["pred"] for x in cells), max(x["meas"] for x in cells)) * 1.12
    ax.plot([0, mx], [0, mx], ls="--", color=MUTED, lw=1)
    top = res["most_affected"]
    for x in cells:
        col = A1 if x["group"].startswith("A1") else A0
        mk = "*" if x["group"] == TARGET else ("D" if x is top or (x["group"] == top["group"] and x["client"] == top["client"]) else "o")
        ax.errorbar(x["pred"], x["meas"], yerr=[[x["meas"] - x["meas_ci"][0]], [x["meas_ci"][1] - x["meas"]]],
                    fmt=mk, color=col, ms=13 if mk == "*" else 7, alpha=0.9, elinewidth=0.8, capsize=0)
        if mk != "o" or len(cells) <= 8:
            lbl = x["group"] if len(cells) <= 8 else f"{x['group']} @c{x['client']}"
            ax.annotate(lbl, (x["pred"], x["meas"]), xytext=(5, 3), textcoords="offset points", fontsize=8)
    ax.set_xlim(0, mx); ax.set_ylim(0, mx)
    ax.set_xlabel("Predicted mean logit decrease (closed form, no retraining)")
    ax.set_ylabel("Measured decrease after retraining")
    ax.set_title(f"Spearman {res['spearman']:.3f} · slope c = {res['slope_c']:.3f}   (★ target {TARGET}, ◆ most affected)",
                 fontsize=9, loc="left")
    fig.tight_layout(); fig.savefig(OUT / "fig_pred_vs_meas.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 4.8))
    lim = np.abs(audit).max()
    im = ax.imshow(audit, cmap="RdBu_r", vmin=-lim, vmax=lim)
    ax.set_xticks(range(8)); ax.set_xticklabels(GROUPS, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(8)); ax.set_yticklabels(GROUPS, fontsize=8)
    for i in range(8):
        j = int(np.argmax(audit[i])); ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=1.6))
        ax.add_patch(plt.Rectangle((i - .5, i - .5), 1, 1, fill=False, ec=MUTED, lw=1, ls=":"))
    ax.set_xlabel("Recipient subgroup (clients 1…K−1)"); ax.set_ylabel(f"Source error at client 0\n({int(RHO * 100)}% of positives flipped)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03, label="predicted logit decrease (red = hurt)")
    fig.tight_layout(); fig.savefig(OUT / "fig_audit_matrix.png", dpi=160); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.6), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axs[0]
    ax.plot([x["rho"] for x in sweep], [x["pred"] for x in sweep], "o--", color=MUTED, label="predicted")
    ax.plot([x["rho"] for x in sweep], [x["meas"] for x in sweep], "o-", color=INK, label="measured")
    ax.set_xlabel("Fraction ρ of target positives flipped"); ax.set_ylabel("Mean decrease"); ax.legend(frameon=False, fontsize=8)
    ax = axs[1]
    v = res["propagation_vector"]
    ax.bar(list(v)[1:], list(v.values())[1:], color=[A1 if x > 0 else A0 for x in list(v.values())[1:]])
    ax.axhline(0, color=INK, lw=0.8); ax.set_title("Propagation vector v_T", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "fig_sweep_vector.png", dpi=160); plt.close(fig)


def card(res):
    top, t = res["most_affected"], res["target_matched_best"]
    iid = H_SET == 0
    where = lambda x: x["group"] if iid else f"{x['group']} at client {x['client']}"
    tiles = [
        {"label": "Rank agreement (Spearman)", "value": f"{res['spearman']:.3f}",
         "sub": f"95% CI [{res['spearman_ci'][0]:.3f}, {res['spearman_ci'][1]:.3f}] over {SEEDS} seeds", "tone": "good"},
        {"label": "Size agreement (slope c)", "value": f"{res['slope_c']:.3f}",
         "sub": f"1.0 = measured as large as predicted; CI [{res['slope_c_ci'][0]:.3f}, {res['slope_c_ci'][1]:.3f}]", "tone": "good"},
        {"label": "Most affected recipient", "value": where(top),
         "sub": ("the target-matched group itself" if res["most_affected_is_target"] else
                 f"{res['most_affected_pct_more_than_target']:.0f}% more than target {TARGET} (rank {res['target_rank']})"),
         "tone": "neutral" if res["most_affected_is_target"] else "warn"},
        {"label": "Labels changed", "value": f"{res['labels_changed_per_seed']:.1f}",
         "sub": f"{res['pct_of_federation_labels']:.3f}% of {K * N_TR:,} federation labels; "
                + ("every recipient mean decreased" if res["all_recipient_means_decreased"] else "not every mean decreased"),
         "tone": "accent"},
    ]
    inputs = {"source error": f"{int(RHO * 100)}% of {TARGET} positives → 0 at client 0", "clients": K,
              "heterogeneity h": H_SET, "β (1,Z,R,W1,W2)": P["beta"], "A→R shift": R_SHIFT, "seeds": SEEDS,
              "analysis": res["analysis"]}
    compare = [
        {"metric": "Spearman (IID, 30%)", "paper": "A1-B3: 0.975 [0.961, 0.987] · A0-B2: 0.968 [0.955, 0.980]",
         "yours": f"{res['spearman']:.3f} [{res['spearman_ci'][0]:.3f}, {res['spearman_ci'][1]:.3f}]", "note": "target " + TARGET},
        {"metric": "Slope c", "paper": "A1-B3: 1.014 · A0-B2: 1.016 (h=1: 1.009 / 1.007)", "yours": f"{res['slope_c']:.3f}", "note": ""},
        {"metric": "Most affected vs target", "paper": "A1-B3 → A1-B4 hit 18.2% more · A0-B2 → A1-B1 hit 34.9% more (target ranks 4th)",
         "yours": f"{where(top)}" + ("" if res["most_affected_is_target"] else f", {res['most_affected_pct_more_than_target']:.1f}% more (target rank {res['target_rank']})"), "note": ""},
        {"metric": "Labels changed (30%)", "paper": "A1-B3: 45.25 (0.377%) · A0-B2: 27.20 (0.227%)",
         "yours": f"{res['labels_changed_per_seed']:.2f} ({res['pct_of_federation_labels']:.3f}%)", "note": ""},
        {"metric": "Sources whose biggest victim is another group", "paper": "—  (new: audit matrix)",
         "yours": f"{res['audit_sources_whose_top_victim_is_another_group']} of 8", "note": "predicted, no retraining"},
    ]
    figs = [{"path": "fig_pred_vs_meas.png", "title": "Can we predict who gets hurt without retraining?",
             "caption": "Each point is a recipient subgroup: x = closed-form prediction ρ·μ⁺ᵀv_T, y = measured mean logit "
                        "decrease on unchanged positive test cases after actually retraining (mean and 95% range over seeds)."},
            {"path": "fig_audit_matrix.png", "title": "Audit without retraining: every possible source error",
             "caption": "Rows = which subgroup's positives are mislabelled at client 0; columns = recipient subgroups elsewhere. "
                        "Boxed = most-hit recipient; dotted = the same-named group. Off-diagonal boxes are the paper's warning."},
            {"path": "fig_sweep_vector.png", "title": "Linearity in ρ, and the direction of propagation",
             "caption": "Left: the measured effect grows ≈ proportionally with the flipped fraction, as Eq. 3 predicts. "
                        "Right: the propagation vector; recipients whose positive-case means project further along it lose more."}]
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 16, "title": "Tracing Bias Propagation Across Subgroups in Federated Learning",
                  "authors": "Tirathraj Ramburn, Afaf Taïk, Farnoosh Ghadiri", "url": "https://drive.google.com/file/d/1aA6Fac9mYYJa1VoylGh4o3GgjQjDeobk/view?usp=sharing", "affiliation": ""},
        "inputs": inputs, "tiles": tiles, "figures": figs, "compare": compare,
        "runbook": {"name": "smash-16-fl-bias-propagation", "url": P.get("runbook_url", "")}}, indent=2))


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
