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
    skill_name: smash-15-transparent-reward
    confidence: high
---

# Who Chose This Trade-off? Transparent Rewards for Insulin Dosing (SMASH 2026 · Paper #15)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Towards Transparent Reward Design in Clinical Reinforcement Learning"** (Caro Strickland, Baptiste Bonin, Audrey Durand).
Read the paper: https://drive.google.com/file/d/1NuHr7dRpH-Qh5nYx7jZ9j1t1NRRW5bXk/view?usp=sharing

The paper's claim: an RL insulin-dosing policy trained on one scalar reward silently encodes a trade-off between
competing clinical priorities, chosen by whoever wrote the reward. Splitting the reward into three objectives and
reporting the **Pareto front** makes that trade-off visible. Two policies with the **same time-in-range (TIR)** can
differ by tens of percentage points in time spent hypoglycaemic, which TIR alone never shows.

The participant brings **their own preference weights** over the three objectives (and their own hypo safety limit),
picks a simglucose virtual patient, and the run:
simulates a transparent family of 48 basal-only dosing rules on the FDA-accepted UVa/Padova simulator (simglucose);
scores each rule on the paper's three-objective reward; finds the Pareto set; shows which rule *their* weights would
choose; repeats the paper's "same TIR within 3 points, different hypo time" analysis; and maps every possible weight
vector to the rule it picks. Output: a shareable **result card**.

Target wall-clock: **under 5 minutes.** The experiment takes about 25–60 s (96 one-day simulations, run in parallel).

### The method as in the paper (§2), as implemented
- Reward vector per step: `r = (r_gly, r_hypo, r_dose)` with `r_gly = −RI(g_t)`, `r_hypo = −LBGI(g_t)` (Kovatchev
  risk index, `RI = LBGI + HBGI`), and `r_dose = −max(0, a_t − b_p) / (a_max − b_p)`, where `b_p` is the patient's basal
  need and `a_max = 4 b_p`.
- Each component is normalized by its empirical standard deviation (over every simulated step of every rule).
- Actions: seven basal levels spaced linearly across `[0, 4 b_p]`; basal-only dosing (no meal boluses).
- Matched pairs: drop policies whose SD across episodes exceeds 20 points on TIR or hypo time; among all pairs within
  3 TIR points, report the median and maximum hypo-time gap.

**What this runbook does differently (and says so on the card):** the paper trains SAC baselines and a
preference-conditioned Q-network (envelope MORL). Training deep RL is out of scope for a 5-minute CPU run, so this
runbook replaces the learned policies with an **enumerated family of simple rules**: the 7 basal levels × a CGM
hypo-suspend threshold (none / 80 / 110 mg/dL) × a high-glucose correction step (+0 / +1 / +2 levels while
CGM > 180 mg/dL). "Your weights' pick" is the rule maximizing `w · r̄` (normalized mean reward), i.e. an *oracle*
scalarized optimum within the family, not a trained agent. Rules with TIR < 20% are excluded from the matched-pair
analysis (clinically absurd, e.g. no insulin at all). Episodes are one simulated day (480 × 3-min CGM steps, random
meals from simglucose's scenario generator) and are not cut short at simglucose's `done` flag.

### Paper headline numbers (quote exactly)
- child#001: Baseline A (optimizing glycemic risk alone) hypoglycemic exposure **55.2%**; baseline B (w = (0.5, 0.3, 0.2))
  **0.0%** hypo at the cost of **56.0%** hyperglycemic exposure; both report a similar TIR.
- Table 1, hypo-exposure gap (pp) among policies within 3 TIR points:
  Adult 39/40 reliable, 98 pairs, median **0.0**, max **42.8**; Adolescent 39/40, 55 pairs, median **0.0**, max **26.5**;
  Child 28/40, 148 pairs, median **6.4**, max **39.8** (text: child 90th percentile **21.1**).
- Differential ("risk-decreasing") reward is exploitable: "a policy can collect higher reward by oscillating into and
  out of a hazardous state than by avoiding it altogether", so the paper uses absolute risk.

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
| Patient | `{{patient}}` | `child#001` | simglucose virtual patient: `adult#001`, `adolescent#001`, `child#001` (paper's three), or any `adult#001`–`#010`, `adolescent#…`, `child#…` |
| Weight: glycaemic risk | `{{w_glycemic}}` | `0.5` | Your preference weight on r_gly (paper's baseline B: 0.5) |
| Weight: hypo safety | `{{w_hypo}}` | `0.3` | Your preference weight on r_hypo (paper: 0.3) |
| Weight: insulin exposure | `{{w_dose}}` | `0.2` | Your preference weight on r_dose (paper: 0.2). Weights are renormalized to sum to 1 |
| Hypo limit | `{{max_hypo_pct}}` | `4` | Your maximum acceptable % time < 70 mg/dL (international consensus target: < 4%) |
| TIR tolerance | `{{tir_tolerance}}` | `3` | Two rules count as "same TIR" if within this many percentage points (paper: 3) |
| Days per rule | `{{n_days}}` | `2` | Simulated days (meal scenarios) per rule; ≥ 2 enables the paper's reliability filter |
| Seed | `{{seed}}` | `1` | Seed for meal scenarios and CGM noise |

## Dependencies

numpy, matplotlib, pandas, scipy (preinstalled or pulled in by simglucose) plus **simglucose** (pure Python; pulls in gym/gymnasium/pathos, all small). simglucose imports `pkg_resources`, so it needs `setuptools<70`. No other downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib, pandas, scipy" 2>/dev/null || uv pip install --system -q numpy matplotlib pandas scipy
python -W ignore -c "import pkg_resources, simglucose.patient.t1dpatient" 2>/dev/null || uv pip install --system -q "setuptools<70" simglucose
python -W ignore -c "import pkg_resources, simglucose.patient.t1dpatient; print('simglucose OK')"
nproc
```

Write `/app/work/params.json` (numbers as JSON numbers; if a value still looks like an unsubstituted `{{…}}`
placeholder, use the table default):

```json
{"patient": "{{patient}}", "w_glycemic": {{w_glycemic}}, "w_hypo": {{w_hypo}}, "w_dose": {{w_dose}},
 "max_hypo_pct": {{max_hypo_pct}}, "tir_tolerance": {{tir_tolerance}}, "n_days": {{n_days}}, "seed": {{seed}},
 "runbook_url": ""}
```

Validate before running: `patient` must match `adult#0NN`, `adolescent#0NN` or `child#0NN` with NN in 01–10 (else use
`child#001`); weights must be ≥ 0 and not all zero (else use 0.5, 0.3, 0.2); clamp `max_hypo_pct` to [0, 50],
`tir_tolerance` to [0.5, 10], `n_days` to [1, 4]. Record any correction as a caveat. The script itself lowers `n_days`
if the sandbox has too few cores for the time budget (it prints a line saying so; mention it as a caveat).

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
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 300 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: 25–60 s depending on cores. Ends with a `done:` line (max same-TIR hypo gap, your pick, % of unsafe preferences).

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers copied from `results.json`.
  Usually the worst matched pair (`worst_pair.hypo_gap` at `worst_pair.tir_diff` TIR difference), or that the
  participant's own weights pick a rule above their hypo limit (`your_pick.hypo` vs `max_hypo_pct`) when a safer rule
  with similar TIR exists.
- **idea**: (1) a scalar reward hides a trade-off chosen by the reward designer; (2) split it into glycaemic risk,
  hypo risk and insulin exposure and report the Pareto front instead; (3) TIR alone cannot tell a "dangerously low"
  policy from a "dangerously high" one.
- **findings**: (1) matched pairs: `n_matched_pairs`, `gap_median`, `gap_max` vs the paper's Table 1 row for the same
  cohort; describe the two traces in `fig_pair_traces.png` in plain words; (2) your weights' pick (`your_pick`:
  label, TIR, hypo, hyper) vs the two fixed weightings (`baseline_A_pick` = w (1,0,0), `baseline_B_pick` = paper's
  w) and whether any Pareto rule (`rules` with `pareto: true`) has similar TIR and lower hypo; (3) the simplex map:
  `simplex_unsafe_fraction` of weight vectors pick a rule above the hypo limit, `simplex_distinct_rules` different rules
  are reachable; (4) optional: differential vs absolute reward (`diff_vs_abs_spearman`, `best_by_differential`), noting
  that an undiscounted differential return telescopes to RI(start) − RI(end) and so is blind to everything in between.
- Use plain words: "hypo" = blood glucose below 70 mg/dL; "TIR" = % of time 70–180 mg/dL.
- **try_next**: 2–3 contrasting runs with exact values, using only the keys `patient, w_glycemic, w_hypo, w_dose,
  max_hypo_pct, tir_tolerance, n_days, seed`. Good contrasts: `adult#001` (the paper's 42.8-point adult gap; the
  easiest patient), `adolescent#001`, weights leaning hard on hypo safety (e.g. 0.1, 0.8, 0.1), or a stricter
  `tir_tolerance` of 1.
- **caveats** (2–4): simulated patients (UVa/Padova via simglucose), not people; an enumerated family of simple
  basal-only rules replaces the paper's trained SAC / preference-conditioned agents, so "picks" are oracle optima
  within that family; one-day episodes with random meals and no meal boluses; not clinical guidance.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: patient, weights, matched-pair stats vs paper, your pick, unsafe
fraction, headline).

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
python3 - "{{results_dir}}" "patient,w_glycemic,w_hypo,w_dose,max_hypo_pct,tir_tolerance,n_days,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} patient,w_glycemic,w_hypo,w_dose,max_hypo_pct,tir_tolerance,n_days,seed 300 checklist.json
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
"""Transparent reward lab — SMASH 2026 paper #15 (Caro Strickland, Baptiste Bonin, Audrey Durand).

The paper decomposes the scalar insulin-dosing reward into three objectives on the UVa/Padova simulator
(simglucose):  r = (r_gly, r_hypo, r_dose) with r_gly = -RI(g), r_hypo = -LBGI(g),
r_dose = -max(0, a - b_p)/(a_max - b_p); normalizes each by its standard deviation; and shows that policies
with the same time-in-range (TIR, within 3 points) can differ by tens of points in hypoglycaemic time.

This runbook does NOT train RL agents (no GPU, < 90 s). Instead it simulates a transparent family of simple
basal-only dosing rules for one simglucose patient (the paper's 7 basal levels on [0, 4 b_p], plus a CGM
hypo-suspend threshold and a high-glucose correction step), scores every rule on the paper's three objectives,
finds the Pareto set, picks the rule your preference weights w would choose (the scalarized optimum), and runs
the paper's matched-pair analysis: among rules within `tir_tolerance` points of TIR, how different is the hypo time?

usage: python experiment.py params.json outdir
"""
import json, os, sys, time, warnings, logging
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)
import numpy as np

T0 = time.time()
LEVELS = 7                     # paper: seven basal levels spaced linearly across [0, 4 b_p]
SUSPEND = [None, 80, 110]      # CGM below this (mg/dL) -> deliver 0 (hypo-suspend), None = never
CORRECT = [0, 1, 2]            # levels added while CGM > 180 mg/dL (capped at the top level)
STEPS = 480                    # one day at the Dexcom 3-min sample time
MIN_TIR = 20                   # matched-pair analysis ignores clinically absurd rules (TIR < 20%; e.g. no insulin at all)


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def risk(bg):
    """Kovatchev et al. (2005) risk index split into LBGI/HBGI components (as in simglucose.analysis.risk)."""
    f = 1.509 * (np.log(np.clip(bg, 10, 600)) ** 1.084 - 5.381)
    lb = np.where(f < 0, 10 * f ** 2, 0.0); hb = np.where(f > 0, 10 * f ** 2, 0.0)
    return lb, hb


def simulate(job):
    """One simulated day for one dosing rule. Returns true BG, CGM and delivered basal (U/min) per 3-min step."""
    name, k, susp, corr, day, seed = job
    from datetime import datetime
    from simglucose.patient.t1dpatient import T1DPatient
    from simglucose.sensor.cgm import CGMSensor
    from simglucose.actuator.pump import InsulinPump
    from simglucose.simulation.scenario_gen import RandomScenario
    from simglucose.simulation.env import T1DSimEnv
    from simglucose.controller.base import Action
    pat = T1DPatient.withName(name)
    bp = pat._params.u2ss * pat._params.BW / 6000.0          # physiological basal need b_p (U/min)
    levels = np.linspace(0, 4 * bp, LEVELS)
    env = T1DSimEnv(pat, CGMSensor.withName("Dexcom", seed=seed + 1000 * day),
                    InsulinPump.withName("Insulet"), RandomScenario(datetime(2026, 1, 1, 0, 0), seed=seed + day))
    obs = env.reset(); cgm = obs.observation.CGM
    bg, cg, ins = [], [], []
    for _ in range(STEPS):
        lvl = k
        if susp is not None and cgm < susp:
            lvl = 0
        elif cgm > 180:
            lvl = min(LEVELS - 1, k + corr)
        a = float(levels[lvl])
        o = env.step(Action(basal=a, bolus=0))   # episode is NOT cut at simglucose's done flag: full day always
        cgm = o.observation.CGM
        bg.append(o.info["bg"]); cg.append(cgm); ins.append(a)
    return job, bp, np.array(bg), np.array(cg), np.array(ins)


def main():
    P = json.loads(Path(sys.argv[1]).read_text())
    OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
    name = str(P["patient"]); n_days = int(P["n_days"]); seed = int(P["seed"])
    w = np.array([float(P["w_glycemic"]), float(P["w_hypo"]), float(P["w_dose"])], float)
    w = np.clip(w, 0, None); w = w / w.sum() if w.sum() > 0 else np.array([0.5, 0.3, 0.2])
    tol = float(P["tir_tolerance"]); floor = float(P["max_hypo_pct"])

    policies = [(k, s, c) for k in range(LEVELS) for s in SUSPEND for c in CORRECT
                if (c == 0 or k + c <= LEVELS - 1) and not (k == 0 and s is not None)]   # drop duplicates
    jobs = [(name, k, s, c, d, seed) for (k, s, c) in policies for d in range(n_days)]
    nproc = max(1, min(int(os.environ.get("SMASH_CPUS") or cpu_count()), len(jobs)))
    # budget guard: ~2.5 core-seconds per simulated day; keep the simulation phase under ~75 s
    while n_days > 1 and len(policies) * n_days * 2.5 / nproc > 75:
        n_days -= 1
    if n_days != int(P["n_days"]):
        log(f"only {nproc} cores: reducing n_days {P['n_days']} -> {n_days} to stay within the time budget")
    jobs = [(name, k, s, c, d, seed) for (k, s, c) in policies for d in range(n_days)]
    log(f"patient {name}: {len(policies)} dosing rules x {n_days} simulated day(s) = {len(jobs)} sims on {nproc} cores")
    with Pool(nproc) as pool:
        sims = pool.map(simulate, jobs, chunksize=1)
    log("simulations finished")

    bp = sims[0][1]; amax = 4 * bp
    by = {}
    for job, _, bg, cg, ins in sims:
        by.setdefault(job[1:4], []).append((bg, cg, ins))
    # ---- per-step reward vectors (paper §2): r_gly = -RI, r_hypo = -LBGI, r_dose = -max(0, a-bp)/(amax-bp)
    allr = []
    for key in policies:
        for bg, cg, ins in by[key]:
            lb, hb = risk(bg)
            allr.append(np.c_[-(lb + hb), -lb, -np.maximum(0, ins - bp) / (amax - bp)])
    sd = np.concatenate(allr).std(0) + 1e-12   # "normalize each by its empirically estimated standard deviation"
    rows = []
    for i, key in enumerate(policies):
        days = by[key]; per = []
        for bg, cg, ins in days:
            lb, hb = risk(bg); r = np.c_[-(lb + hb), -lb, -np.maximum(0, ins - bp) / (amax - bp)]
            ri = lb + hb
            per.append({"tir": 100 * np.mean((bg >= 70) & (bg <= 180)), "hypo": 100 * np.mean(bg < 70),
                        "hyper": 100 * np.mean(bg > 180), "severe": 100 * np.mean(bg < 54),
                        "dose_u_day": float(ins.sum() * 3), "r": r.mean(0) / sd,
                        "diff_return": float(ri[0] - ri[-1]),     # undiscounted differential return telescopes
                        "abs_return": float(-ri.sum())})
        k, s, c = key
        lab = f"basal {k}/6" + (f" · suspend<{s}" if s else "") + (f" · +{c} if >180" if c else "")
        rows.append({"id": i, "label": lab, "level": k, "basal_x_bp": round(4 * k / 6, 3), "suspend": s, "correct": c,
                     "tir": float(np.mean([p["tir"] for p in per])), "hypo": float(np.mean([p["hypo"] for p in per])),
                     "hyper": float(np.mean([p["hyper"] for p in per])), "severe": float(np.mean([p["severe"] for p in per])),
                     "tir_sd": float(np.std([p["tir"] for p in per])), "hypo_sd": float(np.std([p["hypo"] for p in per])),
                     "dose_u_day": float(np.mean([p["dose_u_day"] for p in per])),
                     "r_norm": [float(x) for x in np.mean([p["r"] for p in per], 0)],
                     "diff_return": float(np.mean([p["diff_return"] for p in per])),
                     "abs_return": float(np.mean([p["abs_return"] for p in per]))})
    R = np.array([r["r_norm"] for r in rows])
    # ---- Pareto set on the three (maximized) objectives
    dominated = np.array([any(np.all(R[j] >= R[i]) and np.any(R[j] > R[i]) for j in range(len(R))) for i in range(len(R))])
    for r, d in zip(rows, dominated):
        r["pareto"] = bool(not d)

    def pick(wv):
        return int(np.argmax(R @ np.asarray(wv, float) + 1e-6 * R.sum(1)))   # tiny tie-break: better on all objectives

    you, A, B = pick(w), pick([1, 0, 0]), pick([0.5, 0.3, 0.2])
    # ---- matched-pair analysis (paper §2/Table 1): reliable rules only (SD <= 20 pp on TIR and hypo)
    reliable = [r for r in rows if r["tir_sd"] <= 20 and r["hypo_sd"] <= 20 and r["tir"] >= MIN_TIR]
    pairs = [(a, b, abs(a["hypo"] - b["hypo"])) for a, b in combinations(reliable, 2) if abs(a["tir"] - b["tir"]) <= tol]
    gaps = np.array([g for *_, g in pairs]) if pairs else np.array([0.0])
    worst = max(pairs, key=lambda t: (t[2], -abs(t[0]["tir"] - t[1]["tir"]))) if pairs else None
    log(f"{len(rows)} rules, {int((~dominated).sum())} Pareto-optimal; {len(pairs)} matched pairs within {tol} TIR pts; "
        f"max hypo gap {gaps.max():.1f}")
    # ---- preference-simplex map: which rule does each weight vector pick?
    grid = [(a / 20, b / 20, 1 - a / 20 - b / 20) for a in range(21) for b in range(21 - a)]
    gpick = [pick(g) for g in grid]
    unsafe_frac = float(np.mean([rows[g]["hypo"] > floor for g in gpick]))
    distinct = len(set(gpick))
    # ---- differential vs absolute reward (paper §1): undiscounted differential return only sees the endpoints
    dr = np.array([r["diff_return"] for r in rows]); ar = np.array([r["abs_return"] for r in rows])
    rank = lambda x: np.argsort(np.argsort(x))
    rho = float(np.corrcoef(rank(dr), rank(ar))[0, 1])
    best_diff = rows[int(np.argmax(dr))]; best_abs = rows[int(np.argmax(ar))]

    res = {"params": P, "patient": name, "n_days_used": n_days, "cores": nproc, "basal_need_u_per_min": bp, "basal_need_u_per_h": bp * 60,
           "weights_normalized": [float(x) for x in w], "objective_sd": [float(x) for x in sd],
           "n_rules": len(rows), "n_pareto": int((~dominated).sum()), "n_reliable": len(reliable),
           "n_matched_pairs": len(pairs), "gap_median": float(np.median(gaps)), "gap_p90": float(np.percentile(gaps, 90)),
           "gap_max": float(gaps.max()),
           "worst_pair": ({"a": worst[0], "b": worst[1], "tir_diff": abs(worst[0]["tir"] - worst[1]["tir"]),
                           "hypo_gap": worst[2]} if worst else None),
           "your_pick": rows[you], "baseline_A_pick": rows[A], "baseline_B_pick": rows[B],
           "your_pick_violates_floor": bool(rows[you]["hypo"] > floor),
           "simplex_unsafe_fraction": unsafe_frac, "simplex_distinct_rules": distinct, "simplex_points": len(grid),
           "diff_vs_abs_spearman": rho, "best_by_differential": best_diff, "best_by_absolute": best_abs,
           "constant_basal": [r for r in rows if r["suspend"] is None and r["correct"] == 0],
           "rules": rows}

    # ------------------------------------------------------------------ figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#adb5bd", "#2b8a3e"
    tir = np.array([r["tir"] for r in rows]); hyp = np.array([r["hypo"] for r in rows])

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.axhspan(floor, max(100, hyp.max() + 5), color=ACC, alpha=0.04, lw=0)
    ax.axhline(floor, color=ACC, lw=0.8, ls=":")
    ax.text(1, floor + 1, f"your hypo limit {floor:g}%", color=ACC, fontsize=8, va="bottom")
    ax.scatter(tir[dominated], hyp[dominated], s=18, color=MUTED, label="dominated rule", zorder=2)
    ax.scatter(tir[~dominated], hyp[~dominated], s=26, color=BLUE, label="Pareto-optimal rule (3 objectives)", zorder=3)
    if worst:
        a, b = worst[0], worst[1]
        ax.plot([a["tir"], b["tir"]], [a["hypo"], b["hypo"]], color=ACC, lw=2, zorder=4)
        ax.scatter([a["tir"], b["tir"]], [a["hypo"], b["hypo"]], s=70, facecolor="none", edgecolor=ACC, lw=2, zorder=5,
                   label=f"same TIR (±{tol:g}), {worst[2]:.1f}-pt hypo gap")
    mk = [(A, "s", INK, "single-objective pick (w = 1,0,0)"), (B, "D", GOOD, "paper's fixed w = (0.5,0.3,0.2)"),
          (you, "*", ACC, "your weights' pick")]
    for idx, m, col, lab in mk:
        ax.scatter([tir[idx]], [hyp[idx]], marker=m, s=150 if m == "*" else 70, color=col, edgecolor="white",
                   lw=0.8, zorder=6, label=lab)
    ax.set_xlabel("% time in range (70–180 mg/dL)"); ax.set_ylabel("% time hypoglycaemic (<70 mg/dL)")
    ax.set_xlim(0, 100); ax.set_ylim(-2, max(20, hyp.max() + 4))
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout(); fig.savefig(OUT / "fig_tradeoff.png", dpi=160); plt.close(fig)

    # glucose traces of the worst matched pair (day 1)
    if worst:
        fig, ax = plt.subplots(figsize=(6.4, 2.9))
        hrs = np.arange(STEPS) * 3 / 60
        ax.axhspan(70, 180, color=GOOD, alpha=0.07, lw=0)
        for r_, col in [(worst[0], BLUE), (worst[1], ACC)]:
            bg = by[(r_["level"], r_["suspend"], r_["correct"])][0][0]
            ax.plot(hrs, np.clip(bg, 0, 600), color=col, lw=1.4,
                    label=f"{r_['label']}: TIR {r_['tir']:.0f}%, hypo {r_['hypo']:.0f}%")
        ax.axhline(70, color=ACC, lw=0.7, ls=":"); ax.axhline(180, color=INK, lw=0.7, ls=":")
        ax.set_xlabel("hour of simulated day 1"); ax.set_ylabel("blood glucose (mg/dL)"); ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 4))
        ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=1)
        fig.tight_layout(); fig.savefig(OUT / "fig_pair_traces.png", dpi=160); plt.close(fig)

    # preference simplex map: hypo time of the rule each w picks
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    g = np.array(grid); X = g[:, 1] + 0.5 * g[:, 2]; Y = g[:, 2] * np.sqrt(3) / 2
    tv = np.array([rows[i]["tir"] for i in gpick]); hv = np.array([rows[i]["hypo"] for i in gpick])
    sc = ax.scatter(X, Y, c=tv, cmap="Blues", s=80, marker="h", edgecolor="none", vmin=0, vmax=100)
    unsafe = hv > floor
    ax.scatter(X[unsafe], Y[unsafe], s=80, marker="h", facecolor="none", edgecolor=ACC, lw=1.4)
    ax.plot([0, 1, 0.5, 0], [0, 0, np.sqrt(3) / 2, 0], color=INK, lw=0.8)
    for (xx, yy, t, ha) in [(0, -0.06, "glycaemic risk\n(r_gly)", "center"), (1, -0.06, "hypo safety\n(r_hypo)", "center"),
                            (0.56, np.sqrt(3) / 2 - 0.02, "insulin exposure\n(r_dose)", "left")]:
        ax.text(xx, yy, t, ha=ha, va="top", fontsize=8.5)
    pw = lambda v: (v[1] + 0.5 * v[2], v[2] * np.sqrt(3) / 2)
    for v, m, col, lab in [([1, 0, 0], "s", INK, "w = (1,0,0)"), ([0.5, 0.3, 0.2], "D", GOOD, "paper w"), (w, "*", ACC, "your w")]:
        xx, yy = pw(v); ax.scatter([xx], [yy], marker=m, s=140 if m == "*" else 60, color=col, edgecolor="white", zorder=5, label=lab)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8); cb.set_label("% TIR of the rule this w picks")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_ylim(-0.17, 0.92); ax.set_xlim(-0.08, 1.08)
    ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(-0.02, 1.0))
    fig.tight_layout(); fig.savefig(OUT / "fig_simplex.png", dpi=160); plt.close(fig)

    # ------------------------------------------------------------------ card data
    yp = rows[you]
    tiles = [
        {"label": "Same TIR, different hypo", "value": f"{gaps.max():.1f} pts" if pairs else "n/a",
         "sub": (f"max hypo-time gap among {len(pairs)} rule pairs within {tol:g} TIR points (median {np.median(gaps):.1f})"),
         "tone": "accent"},
        {"label": "Your weights pick", "value": f"{yp['tir']:.0f}% TIR",
         "sub": f"{yp['label']}; hypo {yp['hypo']:.1f}%, hyper {yp['hyper']:.1f}%",
         "tone": "warn" if yp["hypo"] > floor else "good"},
        {"label": "Two fixed weightings", "value": f"{rows[A]['tir']:.0f}% vs {rows[B]['tir']:.0f}%",
         "sub": f"TIR of the w = (1,0,0) pick vs the paper's w = (0.5,0.3,0.2) pick; hypo {rows[A]['hypo']:.1f}% vs "
                f"{rows[B]['hypo']:.1f}%, insulin {rows[A]['dose_u_day']:.0f} vs {rows[B]['dose_u_day']:.0f} U/day",
         "tone": "neutral"},
        {"label": "Preferences that break your limit", "value": f"{100 * unsafe_frac:.0f}%",
         "sub": f"of {len(grid)} weight vectors pick a rule with > {floor:g}% hypo time", "tone": "warn" if unsafe_frac > 0 else "good"},
    ]
    cohort = "adult" if name.startswith("adult") else "adolescent" if name.startswith("adolescent") else "child"
    paper_gap = {"adult": ("98", "0.0", "42.8"), "adolescent": ("55", "0.0", "26.5"), "child": ("148", "6.4", "39.8")}[cohort]
    compare = [
        {"metric": f"Matched pairs within 3 TIR pts ({cohort})", "paper": paper_gap[0], "yours": f"{len(pairs)}",
         "note": f"{len(reliable)}/{len(rows)} rules kept (SD ≤ 20 pts, TIR ≥ {MIN_TIR}%); paper: 40 preference vectors"},
        {"metric": "Median hypo gap among matched pairs (pp)", "paper": paper_gap[1], "yours": f"{np.median(gaps):.1f}", "note": ""},
        {"metric": "Max hypo gap among matched pairs (pp)", "paper": paper_gap[2], "yours": f"{gaps.max():.1f}", "note": ""},
        {"metric": "child#001 fixed-weight failure modes",
         "paper": "Baseline A hypo 55.2%; baseline B hypo 0.0%, hyper 56.0%",
         "yours": f"A-pick hypo {rows[A]['hypo']:.1f}%; B-pick hypo {rows[B]['hypo']:.1f}%, hyper {rows[B]['hyper']:.1f}%",
         "note": "paper baselines are SAC agents; yours are the best rule in the family" + ("" if cohort == "child" else f" ({name})")},
        {"metric": "Differential (risk-decreasing) reward",
         "paper": "a policy can collect higher reward by oscillating into and out of a hazardous state",
         "yours": f"rank corr. with absolute reward {rho:.2f}; its favourite rule has {best_diff['hypo']:.1f}% hypo",
         "note": "undiscounted sum telescopes to RI(start) − RI(end)"},
    ]
    card = {"paper": {"num": 15, "title": "Towards Transparent Reward Design in Clinical Reinforcement Learning",
                      "authors": "Caro Strickland, Baptiste Bonin, Audrey Durand", "url": "https://drive.google.com/file/d/1NuHr7dRpH-Qh5nYx7jZ9j1t1NRRW5bXk/view?usp=sharing", "affiliation": "Université Laval"},
            "inputs": {"patient": name, "weights (gly, hypo, dose)": ", ".join(f"{x:.2f}" for x in w),
                       "hypo limit": f"{floor:g}%", "TIR tolerance": f"±{tol:g} pts", "simulated days / rule": n_days,
                       "dosing rules": len(rows), "seed": seed},
            "tiles": tiles,
            "figures": [
                {"path": "fig_tradeoff.png", "title": "Which risk does each dosing rule trade for its time in range?",
                 "caption": "Each dot is one basal-only dosing rule simulated on the UVa/Padova model. Blue = Pareto-optimal "
                            "on the paper's three objectives. The orange line joins the matched pair with the biggest "
                            "hypoglycaemia gap at (almost) the same TIR."},
                {"path": "fig_pair_traces.png", "title": "Same score, different day",
                 "caption": "Glucose traces of that matched pair on simulated day 1. Green band = target range 70–180 mg/dL."},
                {"path": "fig_simplex.png", "title": "Who chose the trade-off? Every preference vector, mapped",
                 "caption": "Each hexagon is a weight vector w over the three objectives; colour = time in range of the rule "
                            "that maximizes w·r. Orange outlines mark weights whose pick exceeds your hypo limit."}],
            "compare": compare, "runbook": {"name": "smash-15-transparent-reward", "url": P.get("runbook_url", "")}}
    (OUT / "card_data.json").write_text(json.dumps(card, indent=2))
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    log(f"done: {len(rows)} rules; max same-TIR hypo gap {gaps.max():.1f} pts (median {np.median(gaps):.1f}); "
        f"your pick '{yp['label']}' TIR {yp['tir']:.1f}% hypo {yp['hypo']:.1f}%; unsafe preferences {100 * unsafe_frac:.0f}%")


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
