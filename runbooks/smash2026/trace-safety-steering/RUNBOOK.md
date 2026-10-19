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
    skill_name: smash-10-trace-simulator
    confidence: high
---

# TRACE Simulator: Stop Early, Edit Only What Is Harmful (SMASH 2026 · Paper #10)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"TRACE: Temporal Risk Assessment and Concept Editing for Safer Language Generation"** (Ankur Garg, Xuemin Yu, Hassan Sajjad, Samira Ebrahimi Kahou).
Read the paper: https://github.com/agarg-dev/TRACE/blob/0d45d7e5a5e30399eeafd0e2a41c55ae8ae8288d/TRACE.pdf

The paper's claim: a safeguard should (1) detect harmful content **while it is being generated** and (2) intervene
**only when necessary**, leaving safe responses unchanged. TRACE learns a codebook of discrete activation concepts.
It scores each concept's harmfulness from response labels, and a causal detector accumulates a token-by-token
streaming risk that can stop generation. During generation it edits a token's activation **only if** that token is
assigned to a harmful concept, shifting it toward the nearest benign concept. On Qwen3-8B it improves streaming
detection over Kelp and cuts HarmBench ASR with almost no extra refusal on safe responses. A single global refusal
direction, by contrast, reaches ASR 0 but makes many safe responses refuse.

**What this runbook is.** It is a transparent **mechanism simulator**. It implements every TRACE equation on
*simulated* token activations, with no language model and no text. Why not a real model?
- Qwen3-8B cannot run on a CPU sandbox in the time budget.
- A CPU-sized model (e.g. a 135M-parameter one) would need about 450 MB of downloads (CPU PyTorch plus weights).
- It would also need a labelled corpus of harmful responses. This runbook deliberately does not ship one.

Simulation also gives what a tiny real model could not: **the ground truth of every token**. Concept purity,
detection latency and the effect of each activation edit can then be measured exactly.

The simulated world contains three abstract concept families, built from orthogonal *topic*, *compliance* and
*refusal* features:
- **benign**: ordinary content.
- **caution**: safe content on a sensitive topic, such as refusals and safety education. These are the hard negatives.
- **harmful**: compliance on a sensitive topic.

Harmful responses start benign and turn harmful at an onset point. The participant tunes the codebook and the
steering, makes the safe data harder, and **composes their own response trajectory** (e.g.
`benign:20, caution:8, harmful:14`) to see when TRACE would stop it and which tokens it would edit. Output: a
shareable **result card**.

Target wall-clock: **under 3 minutes.** The experiment takes about 5 s. No LLM calls, no downloads.

### The equations, as implemented
- **Eq. 1** encoder `z_t = (1 − ρ) x_t + ρ LN(W x_t + b)`, concept `c_t = argmin_j ‖z_t − e_j‖²`.
- **Eq. 2** (stand-in) `W, b` come from ridge regression of layer ℓ onto a simulated later layer u (reconstruction).
  The codebook is k-means. The region term appends the response label (× `region_weight`) as an extra coordinate
  during codebook learning only. Utilization is handled by re-seeding unused codes. The paper trains all of this
  jointly with β = 0.1, η = 0.01, γ = 5.
- **Eq. 3** `p_c = (H_c + a·r)/(N_c + a)`; `s_c = (p_c − r)/(1 − r)` if `p_c ≥ r`, else `(p_c − r)/r`; each concept is
  counted at most once per response; harmful iff `s_c > 0`; concept mean `μ_c` over layer-ℓ activations.
- **Eq. 4** token hazard `q_t`, cumulative risk `R_t = 1 − ∏_{i≤t}(1 − q_i)`; stop when `R_t` crosses a threshold chosen
  on validation.
- **Eq. 5** response head trained with cross-entropy, streaming head trained with BCE on `R_T`. Stand-in for the GRU:
  a causal logistic hazard on `[s_ct, max(s_ct,0), support, running max s, running mean s⁺, 4 PCA components of x_t]`.
- **Eq. 6** `b(h) = argmin_{b: s_b ≤ 0, well supported} ‖μ_h − μ_b‖`, `Δ_h = μ_b(h) − μ_h`.
- **Eq. 7** `x'_t = x_t + λ g_h Δ_h` with `g_h = max(s_h,0)/max_j max(s_j,0)`, applied only when `c_t` is harmful.
- Baselines: **DiffMean** (mean-difference direction, running-mean score) for detection. **Global refusal
  direction** (mean token of refusal/caution responses minus mean token of harmful responses) added to *every* token.
- Steering readouts (simulated downstream behaviour from the semantic features): **ASR analog** is the share of
  harmful test responses still harmful after editing. **ΔRef analog** is the share of originally non-refusing safe
  responses that now read as refusals.

### Paper headline numbers (quote exactly)
- Harmful-class F1 (Table 1), Resp. / Stream: TRACE **0.835 / 0.837** (WildGuard), **0.933 / 0.935** (S-Eval);
  Kelp 0.839 / 0.803, 0.900 / 0.896; DiffMean 0.491 / 0.491, 0.820 / 0.820; WildGuard classifier 0.571, 0.093.
- Steering (Table 2), ASR / ΔRef: Unsteered **0.873** / 0.000 and **0.634** / 0.000; TRACE **0.306 / +0.006** and
  **0.062 / −0.002**; Refusal direction **0.000 / +0.717** and **0.000 / +0.439**; CAST 0.278 / +0.241, 0.167 / +0.263;
  Self-Reminder 0.289 / +0.078, 0.182 / +0.103.
- Setup: Qwen3-8B, layer 20 read/steer, layer 24 reconstruction target; example stop threshold = 0.605 (Figure 1).

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
| Your sequence | `{{your_sequence}}` | `benign:20, caution:8, benign:6, harmful:14, benign:6` | Your response trajectory as `family:count` segments (`benign`, `caution`, `harmful`; ≤ 300 tokens). Activations are sampled for it; TRACE scores it token by token |
| Codebook size | `{{codebook_size}}` | `48` | Number of discrete concepts K (try `16` for a coarse codebook) |
| Prior strength | `{{prior_strength}}` | `5` | Virtual responses `a` in Eq. 3 (higher = rare concepts pulled harder toward the base rate) |
| Encoder mix ρ | `{{rho}}` | `0.5` | How much the learned projection changes the activation in Eq. 1 (0–1) |
| Region weight | `{{region_weight}}` | `0.5` | Strength of the region term pushing harmful- and safe-response tokens to different codes (0 = off) |
| Steering strength λ | `{{steer_strength}}` | `1.0` | λ in Eq. 7 (and the global direction's scale) |
| Hard negatives | `{{hard_negative_share}}` | `0.3` | Share of safe responses that are refusals / safety education on sensitive topics (0–0.9) |
| Harm onset | `{{harm_onset}}` | `0.4` | Mean position (fraction of the response) where harmful responses turn harmful |
| Seed | `{{seed}}` | `3` | Random seed |

## Dependencies

numpy, scikit-learn and matplotlib (preinstalled in `python312-uv`). No downloads, no LLM calls.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, sklearn, matplotlib" 2>/dev/null || uv pip install --system -q numpy scikit-learn matplotlib
```

Write `/app/work/params.json`. If a value is blank or still looks like an unsubstituted `{{…}}` placeholder, use the
table default. Clamp `codebook_size` to [8, 128] (integer), `prior_strength` to [0, 50], `rho` to [0, 1],
`region_weight` to [0, 5], `steer_strength` to [0, 4], `hard_negative_share` to [0, 0.9], and `harm_onset` to
[0.05, 0.9]. `your_sequence` is a string; segments that do not match `family:count` are ignored by the code. Record
any clamp as a caveat.

```json
{"your_sequence": "{{your_sequence}}", "codebook_size": {{codebook_size}}, "prior_strength": {{prior_strength}},
 "rho": {{rho}}, "region_weight": {{region_weight}}, "steer_strength": {{steer_strength}},
 "hard_negative_share": {{hard_negative_share}}, "harm_onset": {{harm_onset}}, "seed": {{seed}}, "runbook_url": ""}
```

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
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 240 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: about 5 s. Ends with a `done:` line giving streaming F1, ASR and ΔRef analogs, and where your sequence stops.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers from `results.json`. Usually
  the selective-vs-global steering contrast (`asr_trace` and `dref_trace` vs `asr_global` and `dref_global`), or,
  if detection broke down, the false-positive rate on safe sensitive-topic responses.
- **idea**: (1) detect harm *while it is generated* via a cumulative risk that can only rise; (2) discrete activation
  concepts with a smoothed harmfulness score (Eq. 3) make both detection and editing interpretable; (3) edit only
  tokens assigned to harmful concepts, toward nearby benign ones, instead of one global direction.
- **findings**: (1) detection: TRACE vs DiffMean streaming F1 and FPR (`detection`, including `fpr_hardneg`) vs the
  paper's Table 1, plus `trace_median_position`; (2) steering: ASR and ΔRef analogs for TRACE vs the global direction vs
  Table 2. Mention `safe_tokens_edited_trace`: TRACE may still edit a share of safe tokens (impure concepts) without
  changing their behaviour. (3) The codebook: `n_harmful_concepts` of `codebook_size` and their
  `harmful_concept_purity`, read off `fig_concepts.png`. (4) Your sequence: `your_stop_token` vs
  `your_harm_onset_token`, and whether a caution-only stretch triggered a stop.
- **try_next**: 2–3 runs with exact values using only `your_sequence, codebook_size, prior_strength, rho,
  region_weight, steer_strength, hard_negative_share, harm_onset, seed`. Good contrasts: a coarse codebook
  (`codebook_size` 16, `region_weight` 0, `hard_negative_share` 0.8), which usually breaks detection; a safe-only
  sequence (`caution:15, benign:10, caution:10`); a weaker edit (`steer_strength` 0.5); `region_weight` 0.
- **caveats**: simulated activations and a simulated downstream readout, not Qwen3-8B, WildGuard, S-Eval or HarmBench,
  so the ASR/ΔRef analogs are not comparable in level with the paper; the codebook and the hazard model are simplified
  stand-ins for the paper's jointly trained cross-layer VQ and GRU; the simulated world was designed with separable
  semantic features, which favours concept methods.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: settings, detection F1/FPR, steering ASR/ΔRef, your sequence, headline).

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
python3 - "{{results_dir}}" "your_sequence,codebook_size,prior_strength,rho,region_weight,steer_strength,hard_negative_share,harm_onset,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} your_sequence,codebook_size,prior_strength,rho,region_weight,steer_strength,hard_negative_share,harm_onset,seed 240 checklist.json
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
"""TRACE mechanism simulator — SMASH 2026 paper #10 (Garg, Yu, Sajjad, Kahou).

Every TRACE equation, run on SIMULATED token activations (no language model, no text):
  Eq 1  adaptive residual encoder z = (1-rho) x + rho LN(W x + b) and nearest-codebook assignment c_t
  Eq 2  codebook learning (stand-in: W from ridge regression onto the later "layer u", k-means codebook with a
        response-label "region" term and dead-code re-seeding for utilization)
  Eq 3  smoothed concept harmfulness p_c = (H_c + a r)/(N_c + a), s_c in [-1, 1], counted once per response
  Eq 4  cumulative streaming risk R_t = 1 - prod(1 - q_i) from a causal token hazard q_t
  Eq 5  response head (cross-entropy) + streaming head trained with BCE on R_T
  Eq 6  pair each harmful concept with the nearest well-supported benign concept, Delta_h = mu_b(h) - mu_h
  Eq 7  selective edit x' = x + lambda g_h Delta_h only when the token is assigned to a harmful concept
Baselines: DiffMean (mean-difference direction) for detection; a global "refusal direction" added to every token
for steering. Because the activations are simulated, the ground-truth concept of every token is known, so
steering can be scored exactly (an activation-level ASR and a safe-response disruption rate).

usage: python experiment.py params.json outdir
"""
import json, re, sys, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SEED = int(P.get("seed", 3)); rng = np.random.default_rng(SEED)
K = int(P.get("codebook_size", 48)); A_PRIOR = float(P.get("prior_strength", 5)); RHO = float(P.get("rho", 0.5))
REGION = float(P.get("region_weight", 0.5)); LAM = float(P.get("steer_strength", 1.0))
HARDNEG = float(P.get("hard_negative_share", 0.3)); ONSET = float(P.get("harm_onset", 0.4))
D, D_U = 48, 32


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


# ------------------------------------------------------------------ 1. synthetic activation world
# Ground-truth "concepts" are prototypes in activation space, in three abstract families, built from three
# orthogonal semantic features (topic, compliance, refusal) plus a random sub-topic part:
#   benign   - ordinary helpful content (no sensitive topic)
#   caution  - safety-relevant but SAFE content (refusals, safety education): sensitive topic + refusal feature
#   harmful  - harmful-compliance patterns: the same sensitive topics + compliance feature
N_BEN, N_CAU, N_HARM = 24, 8, 8
Q, _ = np.linalg.qr(rng.normal(0, 1, (D, 3)))
topic_dir, comply_dir, refuse_dir = Q[:, 0], Q[:, 1], Q[:, 2]


def deproject(M):
    return M - (M @ Q) @ Q.T


proto_ben = deproject(rng.normal(0, 1.0, (N_BEN, D)))
topics = deproject(rng.normal(0, 0.8, (N_HARM, D)))                 # shared sub-topics for caution & harmful
proto_cau = topics + 2.0 * topic_dir + 2.0 * refuse_dir + deproject(rng.normal(0, 0.3, (N_CAU, D)))
proto_harm = topics + 2.0 * topic_dir + 2.0 * comply_dir + deproject(rng.normal(0, 0.3, (N_HARM, D)))
PROTO = np.vstack([proto_ben, proto_cau, proto_harm])
FAMILY = np.array(["benign"] * N_BEN + ["caution"] * N_CAU + ["harmful"] * N_HARM)
FAM_IDX = {f: np.where(FAMILY == f)[0] for f in ["benign", "caution", "harmful"]}
NOISE = 0.75
A_u = rng.normal(0, 1 / np.sqrt(D), (D_U, D))                      # the later layer u is a nonlinear map of layer l


def layer_u(x):
    return np.tanh(x @ A_u.T)


def make_tokens(fams, r):
    """Token activations for a sequence of concept families; tokens persist on a concept for a few steps (AR drift)."""
    T = len(fams); X = np.empty((T, D)); true_c = np.empty(T, int); cur = None; drift = r.normal(0, 0.25, D)
    for t, f in enumerate(fams):
        if cur is None or FAMILY[cur] != f or r.random() < 0.35:
            cur = int(r.choice(FAM_IDX[f]))
        true_c[t] = cur
        X[t] = PROTO[cur] + drift + r.normal(0, NOISE, D)
    return X, true_c


def make_response(kind, r):
    T = int(r.integers(30, 80))
    if kind == "harmful":
        t0 = int(np.clip(r.normal(ONSET, 0.15), 0.05, 0.9) * T)
        fams = ["benign"] * t0 + [("harmful" if r.random() < 0.6 else ("caution" if r.random() < 0.3 else "benign")) for _ in range(T - t0)]
    elif kind == "hardneg":                                     # a safe response that discusses a sensitive topic
        t0 = int(r.uniform(0.0, 0.5) * T)
        fams = ["benign"] * t0 + [("caution" if r.random() < 0.6 else "benign") for _ in range(T - t0)]
    else:
        fams = ["benign"] * T
    X, c = make_tokens(fams, r)
    return {"kind": kind, "y": int(kind == "harmful"), "X": X, "true_c": c,
            "onset": fams.index("harmful") if "harmful" in fams else None}


N_RESP = 900; HARM_RATE = 0.35
kinds = rng.choice(["harmful", "hardneg", "plain"], N_RESP,
                   p=[HARM_RATE, (1 - HARM_RATE) * HARDNEG, (1 - HARM_RATE) * (1 - HARDNEG)])
data = [make_response(k, np.random.default_rng([SEED, i])) for i, k in enumerate(kinds)]
idx = rng.permutation(N_RESP); tr, va, te = idx[:540], idx[540:720], idx[720:]
log(f"simulated {N_RESP} responses, {sum(len(d['X']) for d in data):,} tokens (harmful {HARM_RATE:.0%}, hard negatives {HARDNEG:.0%} of safe)")

# ------------------------------------------------------------------ 2. Eq 1-2: encoder + codebook
Xtr = np.vstack([data[i]["X"] for i in tr]); Ytr_tok = np.concatenate([[data[i]["y"]] * len(data[i]["X"]) for i in tr])
Utr = layer_u(Xtr)
# W, b: ridge regression from layer l to layer u (stand-in for the reconstruction objective), padded to D dims
Xc = np.c_[Xtr, np.ones(len(Xtr))]
Wb = np.linalg.solve(Xc.T @ Xc + 10 * np.eye(D + 1), Xc.T @ Utr)          # (D+1, D_U)
Wfull = np.zeros((D + 1, D)); Wfull[:, :D_U] = Wb


def LN(h):
    return (h - h.mean(1, keepdims=True)) / (h.std(1, keepdims=True) + 1e-6)


def encode(X):
    return (1 - RHO) * X + RHO * LN(np.c_[X, np.ones(len(X))] @ Wfull)


Ztr = encode(Xtr)
# region term: an extra coordinate carrying the response label during codebook learning only
aug = np.c_[Ztr, REGION * 2.0 * (2 * Ytr_tok - 1)]
km = KMeans(K, n_init=2, random_state=SEED, max_iter=200).fit(aug)
E = km.cluster_centers_[:, :D]
for _ in range(2):                                                          # utilization: re-seed rarely used codes
    assign = np.argmin(((Ztr[:, None, :] - E[None]) ** 2).sum(-1), 1)
    cnt = np.bincount(assign, minlength=K); dead = np.where(cnt < 0.002 * len(Ztr))[0]
    if not len(dead):
        break
    E[dead] = Ztr[rng.choice(len(Ztr), len(dead), replace=False)]


def assign_codes(X):
    Z = encode(X)
    return np.argmin(((Z[:, None, :] - E[None]) ** 2).sum(-1), 1)


for d in data:
    d["c"] = assign_codes(d["X"])
code_use = np.bincount(np.concatenate([data[i]["c"] for i in tr]), minlength=K)
log(f"codebook: {K} concepts, {int((code_use > 0).sum())} used on training tokens")

# ------------------------------------------------------------------ 3. Eq 3: concept harmfulness, means, support
r_rate = float(np.mean([data[i]["y"] for i in tr]))
N_c = np.zeros(K); H_c = np.zeros(K)
for i in tr:
    u = np.unique(data[i]["c"]); N_c[u] += 1; H_c[u] += data[i]["y"]       # each concept counted once per response
p_c = (H_c + A_PRIOR * r_rate) / (N_c + A_PRIOR)
s_c = np.where(p_c >= r_rate, (p_c - r_rate) / (1 - r_rate), (p_c - r_rate) / r_rate)
mu_c = np.array([Xtr[np.argmin(((Ztr[:, None, :] - E[None]) ** 2).sum(-1), 1) == k].mean(0) if code_use[k] else E[k]
                 for k in range(K)])
support = np.log1p(N_c) / np.log1p(N_c.max())
harmful_concepts = np.where(s_c > 0)[0]
# purity: which ground-truth family do each concept's tokens come from?
true_tr = np.concatenate([data[i]["true_c"] for i in tr]); code_tr = np.concatenate([data[i]["c"] for i in tr])
fam_share = {f: np.array([np.mean(np.isin(true_tr[code_tr == k], FAM_IDX[f])) if code_use[k] else 0 for k in range(K)])
             for f in FAM_IDX}
log(f"concept scores: {len(harmful_concepts)} harmful concepts (s_c > 0); dataset harmful rate r = {r_rate:.2f}")

# ------------------------------------------------------------------ 4. Eq 4-5: causal detector
pc_mu = Xtr.mean(0); _, _, Vt = np.linalg.svd(Xtr[::5] - pc_mu, full_matrices=False); PC = Vt[:4]


def token_features(d):
    s = s_c[d["c"]]; sp = np.maximum(s, 0); t = np.arange(1, len(s) + 1)
    return np.c_[s, sp, support[d["c"]], np.maximum.accumulate(s), np.cumsum(sp) / t,
                 (d["X"] - pc_mu) @ PC.T / 3.0]


for d in data:
    d["F"] = token_features(d)
NF = data[0]["F"].shape[1]


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def train_hazard(ids, iters=400, lr=0.05):
    """Streaming head: q_t = sigmoid(w.f_t + b); loss = BCE(y, R_T) with R_T = 1 - prod(1 - q_t) (paper Eq 4-5)."""
    w = np.zeros(NF); b = -4.0; m = np.zeros(NF + 1); v = np.zeros(NF + 1)
    Fs = [data[i]["F"] for i in ids]; ys = np.array([data[i]["y"] for i in ids])
    for it in range(1, iters + 1):
        gw = np.zeros(NF); gb = 0.0
        for F, y in zip(Fs, ys):
            a = F @ w + b; S = np.logaddexp(0, a).sum()                   # S = -log(1 - R_T)
            dS = 1.0 if y == 0 else -1.0 / np.expm1(max(S, 1e-6))
            q = sigmoid(a); gw += dS * (q @ F); gb += dS * q.sum()
        g = np.r_[gw, gb] / len(ids) + 1e-3 * np.r_[w, 0]
        m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
        step = lr * (m / (1 - 0.9 ** it)) / (np.sqrt(v / (1 - 0.999 ** it)) + 1e-8)
        w -= step[:-1]; b -= step[-1]
    return w, b


def risk_curve(d, w, b):
    return 1 - np.exp(-np.cumsum(np.logaddexp(0, d["F"] @ w + b)))


w_h, b_h = train_hazard(tr)
for d in data:
    d["R"] = risk_curve(d, w_h, b_h)


def resp_features(d):
    F = d["F"]; return np.r_[F[-1, :5], F[:, :2].mean(0), F[:, 5:].mean(0), d["R"][-1]]


resp_head = LogisticRegression(max_iter=2000).fit([resp_features(data[i]) for i in tr], [data[i]["y"] for i in tr])


def f1(y, yh):
    y, yh = np.asarray(y), np.asarray(yh); tp = (y & yh).sum(); fp = (~y & yh).sum(); fn = (y & ~yh).sum()
    return float(2 * tp / max(2 * tp + fp + fn, 1))


yva = np.array([data[i]["y"] for i in va], bool); yte = np.array([data[i]["y"] for i in te], bool)
grid = np.linspace(0.05, 0.95, 91)
thr = float(grid[np.argmax([f1(yva, np.array([data[i]["R"].max() >= g for i in va])) for g in grid])])


def stream_eval(ids, scores_fn, th):
    flags, pos = [], []
    for i in ids:
        sc = scores_fn(data[i]); hit = np.where(sc >= th)[0]
        flags.append(len(hit) > 0)
        if len(hit) and data[i]["y"]:
            pos.append(100 * (hit[0] + 1) / len(sc))
    flags = np.array(flags); y = np.array([data[i]["y"] for i in ids], bool)
    return {"f1": f1(y, flags), "fpr": float(flags[~y].mean()), "recall": float(flags[y].mean()),
            "median_position": float(np.median(pos)) if pos else None,
            "fpr_hardneg": float(np.mean([f for f, i in zip(flags, ids) if data[i]["kind"] == "hardneg"])) if any(data[i]["kind"] == "hardneg" for i in ids) else None}


trace_stream = stream_eval(te, lambda d: d["R"], thr)
trace_resp_f1 = f1(yte, resp_head.predict([resp_features(data[i]) for i in te]).astype(bool))
# DiffMean baseline: mean-difference direction; streaming score = running mean of token projections
dm = Xtr[Ytr_tok == 1].mean(0) - Xtr[Ytr_tok == 0].mean(0); dm /= np.linalg.norm(dm)
for d in data:
    pr = d["X"] @ dm; d["DM"] = np.cumsum(pr) / np.arange(1, len(pr) + 1)
dgrid = np.quantile(np.concatenate([data[i]["DM"] for i in va]), np.linspace(0.5, 0.999, 120))
dthr = float(dgrid[np.argmax([f1(yva, np.array([data[i]["DM"].max() >= g for i in va])) for g in dgrid])])
dm_stream = stream_eval(te, lambda d: d["DM"], dthr)
dm_resp_f1 = f1(yte, np.array([data[i]["DM"][-1] >= dthr for i in te]))
log(f"detection (test): TRACE resp F1 {trace_resp_f1:.3f}, stream F1 {trace_stream['f1']:.3f}, FPR {trace_stream['fpr']:.3f} "
    f"| DiffMean stream F1 {dm_stream['f1']:.3f}, FPR {dm_stream['fpr']:.3f}; threshold {thr:.3f}")

# latency vs false positives across thresholds (paper Fig. 2 analog)
lat = {"TRACE": [], "DiffMean": []}
for g in np.linspace(0.1, 0.95, 18):
    e = stream_eval(te, lambda d: d["R"], g)
    if e["recall"] >= 0.2:                                                  # need enough detections for a median
        lat["TRACE"].append((e["fpr"], e["median_position"]))
for g in np.quantile(np.concatenate([data[i]["DM"] for i in te]), np.linspace(0.6, 0.995, 18)):
    e = stream_eval(te, lambda d: d["DM"], g)
    if e["recall"] >= 0.2:
        lat["DiffMean"].append((e["fpr"], e["median_position"]))

# ------------------------------------------------------------------ 5. Eq 6-7: concept-conditioned steering
well_supported = np.where((s_c <= 0) & (N_c >= max(5, 0.02 * len(tr))))[0]
b_of = {h: int(well_supported[np.argmin(((mu_c[well_supported] - mu_c[h]) ** 2).sum(1))]) for h in harmful_concepts}
g_h = np.maximum(s_c, 0) / max(np.maximum(s_c, 0).max(), 1e-9)
# global baseline: a refusal-direction-style vector from data = mean token of refusal/caution (hard-negative) responses
# minus mean token of harmful responses, added to EVERY token (refusal-direction addition, Arditi et al.)
hn_tok = np.vstack([data[i]["X"] for i in tr if data[i]["kind"] == "hardneg"] or [Xtr[Ytr_tok == 0]])
refusal_dir = hn_tok.mean(0) - Xtr[Ytr_tok == 1].mean(0)
mean_delta = np.mean([np.linalg.norm(mu_c[b_of[h]] - mu_c[h]) for h in harmful_concepts]) if len(harmful_concepts) else 1.0
refusal_dir = refusal_dir / np.linalg.norm(refusal_dir) * mean_delta


def steer(d, lam, mode):
    X = d["X"].copy(); edited = np.zeros(len(X), bool)
    if mode == "trace":
        c = assign_codes(X)                                         # assign the current token, then decide
        for t, k in enumerate(c):
            if k in b_of and lam > 0:
                X[t] = X[t] + lam * g_h[k] * (mu_c[b_of[k]] - mu_c[k]); edited[t] = True
    elif mode == "global":
        X = X + lam * refusal_dir; edited[:] = lam > 0
    return X, edited


def behaviour(X):
    """Simulated downstream model: reads the semantic features of the (possibly edited) activations.
    A response is harmful if >= 15% of its tokens carry the compliance feature on a sensitive topic; it reads as a
    refusal/caution response if >= 15% of its tokens carry the refusal feature. Known only because the world is simulated."""
    tau, kap, ref = X @ topic_dir, X @ comply_dir, X @ refuse_dir
    return {"harmful": bool(((kap > 1.0) & (tau > 1.0)).mean() >= 0.15), "caution": bool((ref > 1.0).mean() >= 0.15)}


test_h = [i for i in te if data[i]["y"]]; test_s = [i for i in te if not data[i]["y"]]
base_ref = {i: behaviour(data[i]["X"])["caution"] for i in test_s}


def steer_eval(lam, mode):
    asr = np.mean([behaviour(steer(data[i], lam, mode)[0])["harmful"] for i in test_h])
    dref, touched, tok_edit = [], [], []
    for i in test_s:
        Xs, ed = steer(data[i], lam, mode)
        dref.append(behaviour(Xs)["caution"] and not base_ref[i]); touched.append(ed.any()); tok_edit.append(ed.mean())
    return {"lambda": lam, "asr": float(asr), "delta_ref": float(np.mean(dref)), "safe_touched": float(np.mean(touched)),
            "safe_tokens_edited": float(np.mean(tok_edit))}


unsteered = steer_eval(0.0, "trace")
trace_main = steer_eval(LAM, "trace"); global_main = steer_eval(LAM, "global")
sweep = {"trace": [steer_eval(l, "trace") for l in [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]],
         "global": [steer_eval(l, "global") for l in [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]]}
log(f"steering lambda={LAM}: ASR {unsteered['asr']:.3f} -> TRACE {trace_main['asr']:.3f} (dRef {trace_main['delta_ref']:+.3f}) "
    f"| global {global_main['asr']:.3f} (dRef {global_main['delta_ref']:+.3f})")

# ------------------------------------------------------------------ 6. the participant's response trajectory
seq_txt = (P.get("your_sequence") or "").strip() or "benign:20, caution:8, benign:6, harmful:14, benign:6"
fams = []
for part in re.split(r"[,;]+", seq_txt):
    m = re.match(r"\s*(benign|caution|harmful)\s*[:x*]\s*(\d+)\s*$", part.strip(), re.I)
    if m:
        fams += [m.group(1).lower()] * min(int(m.group(2)), 200)
fams = fams[:300] or ["benign"] * 20 + ["harmful"] * 10
yours = {"kind": "yours", "y": int("harmful" in fams), "onset": fams.index("harmful") if "harmful" in fams else None}
yours["X"], yours["true_c"] = make_tokens(fams, np.random.default_rng([SEED, 999]))
yours["c"] = assign_codes(yours["X"]); yours["F"] = token_features(yours); yours["R"] = risk_curve(yours, w_h, b_h)
hit = np.where(yours["R"] >= thr)[0]
yours_stop = int(hit[0]) if len(hit) else None
_, yours_edit = steer(yours, LAM, "trace")

# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#868e96"
FAMCOL = {"benign": "#a5d8ff", "caution": "#ffd43b", "harmful": ACC}

order = np.argsort(-s_c)
fig, ax = plt.subplots(figsize=(6.4, 3.0))
bottom = np.zeros(K)
for f in ["benign", "caution", "harmful"]:
    ax.bar(range(K), fam_share[f][order], bottom=bottom, color=FAMCOL[f], width=0.85, label=f"true family: {f}")
    bottom += fam_share[f][order]
ax2 = ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(range(K), s_c[order], "k.-", lw=1, ms=4, label="harmfulness score s_c")
ax2.axhline(0, color=INK, lw=0.6, ls="--"); ax2.set_ylim(-1.05, 1.05); ax2.set_ylabel("s_c (Eq. 3)")
ax.set_ylabel("ground-truth composition"); ax.set_xlabel(f"learned concepts, sorted by s_c ({len(harmful_concepts)} with s_c > 0 = harmful)")
ax.set_xticks([]); ax.set_ylim(0, 1)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7.5, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.2))
fig.tight_layout(); fig.savefig(OUT / "fig_concepts.png", dpi=160); plt.close(fig)

fig, axs = plt.subplots(2, 1, figsize=(6.4, 3.6), sharex=False, gridspec_kw={"height_ratios": [3, 0.6]})
ax = axs[0]
ex_h = next(i for i in te if data[i]["kind"] == "harmful" and data[i]["onset"] and data[i]["onset"] > 10)
ex_n = next((i for i in te if data[i]["kind"] == "hardneg"), next(i for i in te if not data[i]["y"]))
for i, col, lab in [(ex_h, MUTED, "a harmful test response"), (ex_n, BLUE, "a safe response on a sensitive topic")]:
    ax.plot(data[i]["R"], color=col, lw=1.4, label=lab)
    if data[i]["onset"] is not None:
        ax.axvline(data[i]["onset"], color=col, ls=":", lw=1)
ax.plot(yours["R"], color=ACC, lw=2.2, label="your sequence")
ax.axhline(thr, color=INK, ls="--", lw=1); ax.text(1, thr + 0.03, f"stop threshold {thr:.3f} (chosen on validation)", fontsize=7.5)
if yours_stop is not None:
    ax.plot(yours_stop, yours["R"][yours_stop], "o", color=ACC); ax.text(yours_stop + 1, yours["R"][yours_stop] - 0.12, f"stop at token {yours_stop + 1}", color=ACC, fontsize=8)
ax.set_ylabel("cumulative risk R_t"); ax.set_ylim(0, 1.05); ax.legend(frameon=False, fontsize=7.5, loc="lower right")
ax = axs[1]
ax.imshow(np.array([[{"benign": 0, "caution": 1, "harmful": 2}[f] for f in fams]]), aspect="auto",
          cmap=matplotlib.colors.ListedColormap([FAMCOL["benign"], FAMCOL["caution"], FAMCOL["harmful"]]), vmin=0, vmax=2)
ed = np.where(yours_edit)[0]; ax.plot(ed, np.zeros(len(ed)), "kv", ms=3)
ax.set_yticks([]); ax.set_xlabel("token position in your sequence (colour = true family; ▼ = TRACE edit)", fontsize=8.5)
fig.tight_layout(); fig.savefig(OUT / "fig_stream.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.0))
for mode, col, lab in [("trace", BLUE, "TRACE selective edit (Eq. 7)"), ("global", ACC, "global refusal direction")]:
    xs = [s["delta_ref"] for s in sweep[mode]]; ys = [s["asr"] for s in sweep[mode]]
    ax.plot(xs, ys, "o-", color=col, label=lab)
    seen = set()
    for s in sweep[mode]:
        key = (round(s["delta_ref"], 2), round(s["asr"], 2))
        if s["lambda"] in (0.5, 1.0, 2.0) and key not in seen:
            seen.add(key)
            ax.annotate(f"λ={s['lambda']:g}", (s["delta_ref"], s["asr"]), fontsize=7, xytext=(4, 3), textcoords="offset points", color=col)
ax.set_xlabel("ΔRef analog: safe responses pushed into refusal-like behaviour"); ax.set_ylabel("ASR analog\n(harmful responses still harmful)")
ax.legend(frameon=False, fontsize=8); ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
fig.tight_layout(); fig.savefig(OUT / "fig_steering.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.8))
for name, col in [("TRACE", BLUE), ("DiffMean", MUTED)]:
    pts = [(f, p) for f, p in lat[name] if p is not None]
    ax.plot([100 * f for f, _ in pts], [p for _, p in pts], "o-", color=col, ms=3, label=name)
ax.set_xlabel("false-positive rate (%)"); ax.set_ylabel("median detection position\n(% of response)")
ax.legend(frameon=False, fontsize=8); ax.text(0.98, 0.95, "lower left is better", transform=ax.transAxes, ha="right", fontsize=8, color=MUTED)
fig.tight_layout(); fig.savefig(OUT / "fig_latency.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ outputs
res = {"params": P, "world": {"responses": N_RESP, "harmful_rate": HARM_RATE, "hard_negative_share": HARDNEG, "dim": D,
                              "true_concepts": {"benign": N_BEN, "caution": N_CAU, "harmful": N_HARM}},
       "codebook_size": K, "codes_used": int((code_use > 0).sum()), "n_harmful_concepts": int(len(harmful_concepts)),
       "harmful_concept_purity": float(np.mean(fam_share["harmful"][harmful_concepts])) if len(harmful_concepts) else None,
       "r_rate": r_rate, "threshold": thr,
       "detection": {"trace_resp_f1": trace_resp_f1, "trace_stream": trace_stream, "diffmean_resp_f1": dm_resp_f1, "diffmean_stream": dm_stream},
       "trace_stream_f1": trace_stream["f1"], "trace_fpr": trace_stream["fpr"], "diffmean_stream_f1": dm_stream["f1"], "diffmean_fpr": dm_stream["fpr"],
       "trace_median_position": trace_stream["median_position"],
       "steering": {"unsteered": unsteered, "trace": trace_main, "global": global_main, "sweep": sweep},
       "asr_unsteered": unsteered["asr"], "asr_trace": trace_main["asr"], "asr_global": global_main["asr"],
       "dref_trace": trace_main["delta_ref"], "dref_global": global_main["delta_ref"],
       "safe_tokens_edited_trace": trace_main["safe_tokens_edited"], "safe_touched_trace": trace_main["safe_touched"],
       "your_sequence": seq_txt, "your_tokens": len(fams), "your_stop_token": None if yours_stop is None else yours_stop + 1,
       "your_harm_onset_token": None if yours["onset"] is None else yours["onset"] + 1,
       "your_tokens_edited": int(yours_edit.sum()), "your_final_risk": float(yours["R"][-1]),
       "latency_curves": lat}

stop_txt = f"token {yours_stop + 1}" if yours_stop is not None else "never"
tiles = [
    {"label": "Streaming F1 (test)", "value": f"{trace_stream['f1']:.2f} vs {dm_stream['f1']:.2f}",
     "sub": f"TRACE vs DiffMean; FPR {100 * trace_stream['fpr']:.0f}% vs {100 * dm_stream['fpr']:.0f}%", "tone": "good"},
    {"label": "ASR analog", "value": f"{unsteered['asr']:.2f} → {trace_main['asr']:.2f}",
     "sub": f"unsteered → TRACE edit at λ = {LAM:g} (global: {global_main['asr']:.2f})", "tone": "accent"},
    {"label": "ΔRef analog", "value": f"{trace_main['delta_ref']:+.2f} vs {global_main['delta_ref']:+.2f}",
     "sub": "safe responses disrupted: TRACE vs global direction", "tone": "warn"},
    {"label": "Your sequence stops at", "value": stop_txt,
     "sub": f"harm starts at token {yours['onset'] + 1}" if yours["onset"] is not None else "no harmful segment in it", "tone": "neutral"},
]
compare = [
    {"metric": "Harmful-class F1, response / streaming (TRACE)", "paper": "WildGuard 0.835 / 0.837; S-Eval 0.933 / 0.935",
     "yours": f"{trace_resp_f1:.3f} / {trace_stream['f1']:.3f}", "note": "synthetic activations"},
    {"metric": "DiffMean F1, response / streaming", "paper": "WildGuard 0.491 / 0.491; S-Eval 0.820 / 0.820",
     "yours": f"{dm_resp_f1:.3f} / {dm_stream['f1']:.3f}", "note": ""},
    {"metric": "Steering ASR (unsteered → TRACE)", "paper": "WildGuard 0.873 → 0.306; S-Eval 0.634 → 0.062",
     "yours": f"{unsteered['asr']:.3f} → {trace_main['asr']:.3f}", "note": "activation-level analog"},
    {"metric": "ΔRef, TRACE vs refusal direction", "paper": "+0.006 vs +0.717 (WildGuard); −0.002 vs +0.439 (S-Eval)",
     "yours": f"{trace_main['delta_ref']:+.3f} vs {global_main['delta_ref']:+.3f}", "note": "analog"},
    {"metric": "Refusal direction ASR", "paper": "0.000 on both datasets", "yours": f"{global_main['asr']:.3f} at λ = {LAM:g}", "note": ""},
    {"metric": "Stop threshold", "paper": "threshold = 0.605 (Figure 1 example)", "yours": f"{thr:.3f}", "note": "validation-selected"},
]
Path(OUT / "card_data.json").write_text(json.dumps({
    "paper": {"num": 10, "title": "TRACE: Temporal Risk Assessment and Concept Editing for Safer Language Generation",
              "authors": "Ankur Garg, Xuemin Yu, Hassan Sajjad, Samira Ebrahimi Kahou", "url": "https://github.com/agarg-dev/TRACE/blob/0d45d7e5a5e30399eeafd0e2a41c55ae8ae8288d/TRACE.pdf", "affiliation": ""},
    "inputs": {"codebook": K, "prior a": f"{A_PRIOR:g}", "ρ": f"{RHO:g}", "region weight": f"{REGION:g}", "λ": f"{LAM:g}",
               "hard negatives": f"{100 * HARDNEG:.0f}% of safe", "harm onset": f"{ONSET:g}", "your sequence": seq_txt[:60], "seed": SEED},
    "tiles": tiles,
    "figures": [{"path": "fig_stream.png", "title": "When would generation stop?",
                 "caption": "Cumulative streaming risk R_t = 1 − ∏(1 − q_i) for your concept sequence and two test responses. "
                            "Dotted lines mark where harmful content truly starts. The strip shows your sequence's true concept "
                            "families and the tokens TRACE would edit."},
                {"path": "fig_steering.png", "title": "Selective edits vs one global direction",
                 "caption": "Sweeping the steering strength λ. TRACE edits only tokens assigned to harmful concepts (Eq. 7); "
                            "the global direction shifts every token. Lower left is better."},
                {"path": "fig_concepts.png", "title": "Did the codebook find the harmful concepts?",
                 "caption": "Each bar is a learned concept: its true composition (simulated ground truth) and its smoothed "
                            "harmfulness score s_c (Eq. 3) computed only from response labels."},
                {"path": "fig_latency.png", "title": "Earlier detection costs false positives",
                 "caption": "Median detection position vs false-positive rate across thresholds (the paper's Figure 2 analog)."}],
    "compare": compare, "runbook": {"name": "smash-10-trace-simulator", "url": P.get("runbook_url", "")}}, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: stream F1 {trace_stream['f1']:.3f} (DiffMean {dm_stream['f1']:.3f}); ASR {unsteered['asr']:.3f}->{trace_main['asr']:.3f} "
    f"dRef {trace_main['delta_ref']:+.3f} vs global ASR {global_main['asr']:.3f} dRef {global_main['delta_ref']:+.3f}; "
    f"your sequence stops at {stop_txt}")
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
