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
    skill_name: smash-01-complementary-vulnerabilities
    confidence: high
---

# Paired-Error Audit: Do Two Readers Fail on the Same Cases? (SMASH 2026 · Paper #1)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Complementary Vulnerabilities: Auditing and Governing Clinician-LLM Error Overlap"** (Mohsen Amoei, Kathleen Fraser, Dan Poenaru).
Read the paper: https://drive.google.com/file/d/1_bJ_5DA5k0V2X1XuuxliKg5WdLPq1SMP/view?usp=sharing

The paper's claim: a second reasoner reduces error only insofar as it **fails differently** from the first. The
deciding property ("complementary vulnerabilities") is not accuracy but **same-case error overlap**, and it is
fragile: it erodes when the clinician defers to the model or the model conforms to the clinician. The paper
therefore proposes a pre-deployment **paired-error audit** with two go/no-go gates, and governance that preserves
the measured independence.

The participant runs that audit for real on public medical questions, with two LLM readers:
- a fast small model answering "from first impression" stands in for the **unaided clinician** (a *proxy*;
  no clinicians are involved), and
- a second model is the **system under audit**.

Both answer the same MedQA-USMLE cases blind; the run builds the paper's 2x2, double-fault rate and Yule's Q, then
re-runs the pair in **assisted workflows** (model answers second after seeing the clinician's impression; clinician
answers second after seeing the AI suggestion) to measure how much independence survives. A no-LLM simulator shows
"two models at the same 90% accuracy with very different double-fault rates". Participants can instead paste their
own paired counts. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment takes ~30 s (about 24 small/large LLM calls).

### The method, as in the paper (§4)
- Paired, case-level record: the clinician's answer before model reveal, the locked model on the same information,
  both scored against a prespecified reference. Crossing them gives four outcomes: **shared success**,
  **model-only error** (substitution risk), **clinician-only error** (rescue potential), **shared error**
  (common-mode failure).
- Report error association, not only accuracy: raw paired counts, the **double-fault rate** (both wrong together)
  and a correlation coefficient (Kuncheva & Whitaker 2003; here **Yule's Q** = (N11·N00 − N10·N01)/(N11·N00 + N10·N01),
  plus phi and disagreement). Stratify across case mix. Re-run in the assisted workflow, "since offline divergence is
  only rescue potential".
- Two gates with site-prespecified thresholds: (1) adequate accuracy with low failure overlap; (2) manageable
  model-only harm with preserved independent judgment. Overlap concentrated in identifiable strata → partial deployment.

### Paper numbers (quote exactly; the paper is conceptual and reports no audit of its own)
- "Two models can both be 90% accurate while one fails exactly where clinicians fail and the other catches clinician misses."
- Sizing: "a serious-harm outcome near 1% prevalence implies a sample on the order of 1,000 adjudicated cases to expect 10 such events".
- Cited evidence: the model "reproduced all of the clinician's listed diagnoses in 48% of cases when it answered second
  versus 3% when it answered first (Everett et al., 2026)"; "Incorrect LLM recommendations lowered physicians' accuracy
  by 14 to 18 percentage points" (Qazi et al., 2026); "human-model error diversity exceeded model-model diversity" (Zoller et al., 2025).

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All computed numbers incl. per-item answers (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Clinician proxy | `{{clinician_proxy}}` | `small-fast` | Reader standing in for the unaided clinician: `small-fast` (Claude Haiku, answers from first impression), `small` (Haiku, careful) or `large` (Claude Sonnet) |
| Model under audit | `{{audit_model}}` | `large` | The candidate model: `large` (Sonnet), `small` (Haiku, careful) or `small-fast` |
| Cases | `{{n_items}}` | `36` | Number of MedQA-USMLE test cases (12–60) |
| Case mix | `{{case_mix}}` | `mixed` | `mixed` (equal thirds), `diagnosis`, `management`, or `mechanism/other` (question type parsed from the stem) |
| Assisted workflow | `{{anchoring}}` | `both` | `both`, `model_conforms` (model sees the clinician's impression first), `clinician_defers` (clinician sees the AI suggestion first), or `off` |
| Anchor source | `{{anchor_source}}` | `enriched` | What the second reader is shown: `clinician` (the other reader's real answers), `enriched` (real answers plus a wrong one planted on a third of the cases it got right, so enough wrong anchors exist) or `always_wrong` |
| Gate thresholds | `{{gate_thresholds}}` | `accuracy>=0.80,double_fault<=0.05,model_only<=0.10,rescue_retained>=0.50` | Your site's prespecified go/no-go thresholds |
| Your paired counts | `{{byo_counts}}` | — | Skip the LLMs and audit **your own** paired record: `shared_success,model_only_error,clinician_only_error,shared_error`, optionally `| the same four counts from your assisted re-audit` (e.g. `812,41,97,50 | 790,52,60,98`) |
| Simulator accuracy | `{{sim_accuracy}}` | `0.90` | Accuracy of the three hypothetical models in the no-LLM simulator panel |
| Seed | `{{seed}}` | `1` | Which cases are drawn and which anchors are planted |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). Data: the MedQA-USMLE 4-option test split
(`GBaker/MedQA-USMLE-4-options` on Hugging Face, CC-BY-4.0; Jin et al. 2020), 2.1 MB, downloaded at run time.
LLM access: `llm.py` (embedded) uses the sandbox's OpenRouter/Anthropic/OpenAI key.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json`. If a value still looks like an unsubstituted `{{…}}` placeholder use the table
default; use `""` for a blank `byo_counts`. Clamp `n_items` to [12, 60] and `sim_accuracy` to [0.5, 0.99]; map an
unknown `clinician_proxy`/`audit_model` to the default and record any change as a caveat.

```json
{"clinician_proxy": "{{clinician_proxy}}", "audit_model": "{{audit_model}}", "n_items": {{n_items}},
 "case_mix": "{{case_mix}}", "anchoring": "{{anchoring}}", "anchor_source": "{{anchor_source}}",
 "gate_thresholds": "{{gate_thresholds}}", "byo_counts": "{{byo_counts}}", "sim_accuracy": {{sim_accuracy}},
 "seed": {{seed}}, "runbook_url": ""}
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

Expected: ~30 s, ending with a `done:` line (accuracies, double-fault, Q, gates, LLM calls). If it fails with an
HTTP error, run it once more (replies are cached in `/app/work/llm_cache.json`, so finished calls are not repeated).
If no LLM key is available, rerun with `byo_counts` set to the example in the table and say so in the caveats.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers copied from `results.json`,
  usually how the double-fault rate or the copying of wrong answers changes once a reader sees the other's answer
  (`model_conforms`, `clinician_defers`), or the offline Q / double-fault vs the independence baseline.
- **idea**: (1) a second reader only helps if it fails on different cases; (2) the paired-error audit (2x2,
  double-fault, association, strata, gates); (3) independence is fragile, so governance should preserve it.
- **findings**: (1) the offline 2x2: accuracies, double-fault vs `double_fault_if_independent`, Q with its CI;
  (2) the assisted workflows: wrong answers copied blind → after seeing them, rescue retained, and the proxy
  clinician's accuracy on AI-wrong cases (`accuracy_drop_pp_when_ai_wrong`; the paper cites 14 to 18 points for
  physicians); (3) the gates and which strata pass Gate 1 (`partial_deployment_strata`), stressing the tiny n;
  (4) optionally the simulator (same accuracy, very different overlap). In `byo` mode, describe the participant's
  counts and gates instead.
- **try_next**: 2–3 contrasting runs with exact values using only the keys `clinician_proxy, audit_model, n_items,
  case_mix, anchoring, anchor_source, gate_thresholds, byo_counts, sim_accuracy, seed`. Good contrasts: same-family
  readers (`audit_model` `small`, which shares errors with the Haiku proxy); `anchor_source` `always_wrong`
  (pure conformity test); a different `case_mix`; or `byo_counts` with the participant's own audit.
- **caveats**: always say that both readers are LLMs, so this is an LLM-vs-LLM **proxy** of the clinician–model audit,
  not evidence about clinicians; MedQA exam questions are not clinical cases (and have known key errors); n is far
  below the paper's ~1,000-case sizing so every rate has a wide CI; gate thresholds are illustrative; LLM answers vary
  between runs even at temperature 0.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: readers, n, offline 2x2, double-fault and Q, assisted-workflow
changes, gate results, headline).

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
python3 - "{{results_dir}}" "clinician_proxy,audit_model,n_items,case_mix,anchoring,anchor_source,gate_thresholds,byo_counts,sim_accuracy,seed" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} clinician_proxy,audit_model,n_items,case_mix,anchoring,anchor_source,gate_thresholds,byo_counts,sim_accuracy,seed 300 checklist.json
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
"""Complementary vulnerabilities: a paired-error audit — SMASH 2026 paper #1 (Amoei, Fraser, Poenaru).

Two LLM "readers" answer the same public medical MCQs (MedQA-USMLE, CC-BY-4.0): a fast small model stands in
for the unaided clinician (a PROXY, not a clinician) and a second model is the system under audit. Crossing their
case-level correctness gives the paper's 2x2 (shared success / model-only error / clinician-only error / shared
error), the double-fault rate and Yule's Q (Kuncheva & Whitaker 2003). Then the readers are re-run in an assisted
workflow where one sees the other's answer first, to measure how much independence survives (conformity).
A no-LLM simulator shows two models at the same accuracy with very different double-fault rates.
Or: bring your own paired counts and skip the LLMs.

usage: python experiment.py params.json outdir
"""
import json, math, os, re, sys, time, urllib.request
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).resolve().parent
DATA_URL = "https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options/resolve/main/phrases_no_exclude_test.jsonl"
INK, ACC, BLUE, MUTED, GOOD = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e"
CELLS = ["shared success", "model-only error", "clinician-only error", "shared error"]
CELL_COL = ["#ced4da", ACC, BLUE, INK]
BATCH = 6


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def s(key, default):
    v = P.get(key, default)
    return default if v is None or (isinstance(v, str) and (v.strip() == "" or v.strip().startswith("{{"))) else v


CLIN = str(s("clinician_proxy", "small-fast")); MODEL = str(s("audit_model", "large"))
N_ITEMS = int(min(60, max(12, int(float(s("n_items", 36))))))
MIX = str(s("case_mix", "mixed")); ANCHOR = str(s("anchoring", "both")); ANCHOR_SRC = str(s("anchor_source", "enriched"))
SEED = int(float(s("seed", 1))); SIM_ACC = float(s("sim_accuracy", 0.90)); SIM_CLIN = 0.80  # replaced by the measured clinician accuracy in main()
BYO = str(s("byo_counts", "")).strip()
GATES = {"accuracy": 0.80, "double_fault": 0.05, "model_only": 0.10, "rescue_retained": 0.50}
for part in str(s("gate_thresholds", "")).split(","):
    m = re.match(r"\s*(\w+)\s*(?:>=|<=|=)\s*([\d.]+)", part)
    if m and m.group(1) in GATES:
        GATES[m.group(1)] = float(m.group(2))

# ---------------------------------------------------------------- the paper's paired-error statistics


def paired(a_ok, b_ok):
    """a = clinician (proxy), b = model. Returns the 2x2 and the paper's association measures."""
    a_ok, b_ok = np.asarray(a_ok, bool), np.asarray(b_ok, bool)
    n11 = int(np.sum(a_ok & b_ok)); n10 = int(np.sum(a_ok & ~b_ok)); n01 = int(np.sum(~a_ok & b_ok)); n00 = int(np.sum(~a_ok & ~b_ok))
    return from_counts(n11, n10, n01, n00)


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def from_counts(n11, n10, n01, n00):
    N = n11 + n10 + n01 + n00
    acc_c = (n11 + n10) / N; acc_m = (n11 + n01) / N
    num, den = n11 * n00 - n10 * n01, n11 * n00 + n10 * n01
    corrected = den == 0 or min(n11, n10, n01, n00) == 0
    if corrected:  # Haldane–Anscombe 0.5 correction so Q stays finite
        a, b, c, d = n11 + .5, n10 + .5, n01 + .5, n00 + .5; num, den = a * d - b * c, a * d + b * c
    q = num / den
    phi_den = math.sqrt(max((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00), 1e-12))
    return {"n": N, "shared_success": n11, "model_only_error": n10, "clinician_only_error": n01, "shared_error": n00,
            "clinician_accuracy": acc_c, "model_accuracy": acc_m, "double_fault": n00 / N,
            "double_fault_ci": wilson(n00, N), "double_fault_if_independent": (1 - acc_c) * (1 - acc_m),
            "yules_q": q, "q_continuity_corrected": corrected, "phi": (n11 * n00 - n10 * n01) / phi_den,
            "disagreement": (n10 + n01) / N, "model_only_rate": n10 / N, "clinician_only_rate": n01 / N,
            "rescue_rate": n01 / (n01 + n00) if (n01 + n00) else float("nan"),
            "cases_to_expect_10_shared_errors": int(math.ceil(10 * N / n00)) if n00 else None}


def boot_q(a_ok, b_ok, B=2000, seed=0):
    rng = np.random.default_rng(seed); a_ok, b_ok = np.asarray(a_ok, bool), np.asarray(b_ok, bool); qs = []
    for _ in range(B):
        i = rng.integers(0, len(a_ok), len(a_ok)); qs.append(paired(a_ok[i], b_ok[i])["yules_q"])
    return [float(np.percentile(qs, 2.5)), float(np.percentile(qs, 97.5))]


def gates(off, assisted):
    g1 = off["model_accuracy"] >= GATES["accuracy"] and off["double_fault"] <= GATES["double_fault"]
    rr = None
    if assisted is not None and off["rescue_rate"] == off["rescue_rate"] and off["rescue_rate"] > 0:
        rr = assisted["rescue_rate"] / off["rescue_rate"]
    g2_mo = off["model_only_rate"] <= GATES["model_only"]
    g2 = (g2_mo and rr is not None and rr >= GATES["rescue_retained"]) if rr is not None else None
    return {"gate1_accuracy_and_low_overlap": bool(g1), "gate2_model_only_harm_and_preserved_independence": g2,
            "gate2_model_only_part": bool(g2_mo), "rescue_retained": rr, "thresholds": GATES}


# ---------------------------------------------------------------- items and LLM readers

def stratum(q):
    """Question type from the final (question) sentence of the stem."""
    t = re.split(r"(?<=[.!])\s+", q.strip().strip('"').lower())[-1]
    if re.search(r"diagnosis|most likely (underlying )?cause|most likely (condition|disease)|is most likely (affected|responsible)", t):
        return "diagnosis"
    if re.search(r"next (best )?step|first step|most appropriate|best initial|management|treatment|therapy|pharmacotherapy|"
                 r"should be (added|given|administered|started|prescribed|recommended)|drug of choice", t):
        return "management"
    return "mechanism/other"


def load_items():
    cache = Path(os.environ.get("SMASH_DATA_DIR", HERE)) / "medqa_usmle_test.jsonl"
    if not cache.exists():
        log("downloading MedQA-USMLE test split (2.1 MB, CC-BY-4.0) from Hugging Face")
        with urllib.request.urlopen(DATA_URL, timeout=60) as r:
            cache.write_bytes(r.read())
    rows = [json.loads(l) for l in cache.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if len(r["question"]) <= 1400]
    for i, r in enumerate(rows):
        r["idx"] = i; r["stratum"] = stratum(r["question"])
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(rows))
    names = ["diagnosis", "management", "mechanism/other"]
    if MIX in names:
        want = {MIX: N_ITEMS}
    else:
        want = {k: N_ITEMS // 3 + (1 if j < N_ITEMS % 3 else 0) for j, k in enumerate(names)}
    picked = []
    for i in order:
        r = rows[i]
        if want.get(r["stratum"], 0) > 0:
            picked.append(r); want[r["stratum"]] -= 1
        if len(picked) == N_ITEMS:
            break
    return picked


READERS = {  # name -> (llm size, persona, ask for a short rationale)
    "small-fast": ("small", "You are a busy attending physician on a long shift. Answer each case from your first clinical "
                            "impression, in a few seconds, without deliberating. Never skip a case.", False),
    "small": ("small", "You are a careful physician. Answer each multiple-choice case.", True),
    "large": ("large", "You are a careful physician. Answer each multiple-choice case.", True),
}


def fmt_item(k, r, anchor=None, anchor_label=""):
    opts = "\n".join(f"  ({L}) {t}" for L, t in r["options"].items())
    a = f"\n  {anchor_label}: ({anchor}) {r['options'][anchor]}" if anchor else ""
    return f"Case {k}:\n{r['question']}\n{opts}{a}"


def ask(reader, items, anchors=None, anchor_label=""):
    from llm import chat_many
    size, persona, why = READERS[reader]
    fmt = ('{"1": {"answer": "B", "why": "<= 12 words"}, "2": ...}' if why else '{"1": "B", "2": "D", ...}')
    extra = ""
    if anchors:
        extra = (f"\nEach case shows the {anchor_label.lower()}. Take it into account as you would in practice, "
                 "then give your own final answer.")
    prompts = []
    for b in range(0, len(items), BATCH):
        chunk = items[b:b + BATCH]
        body = "\n\n".join(fmt_item(k + 1, r, anchors[b + k] if anchors else None, anchor_label) for k, r in enumerate(chunk))
        prompts.append(f"Answer these {len(chunk)} USMLE-style cases.{extra}\n\n{body}\n\nReply with ONLY a JSON object (no prose, "
                       f"no markdown) mapping case number to the option letter, like {fmt}")
    sysmsg = persona + " You always reply with a single JSON object and nothing else."
    replies = chat_many(prompts, system=sysmsg, size=size, max_tokens=100 + (70 if why else 8) * BATCH, workers=8)
    n_calls = len(prompts)

    def grab(rep):
        found = {int(k): v for k, v in re.findall(r'"(\d+)"\s*:\s*\{[^{}]*?"answer"\s*:\s*"\(?([A-D])', rep)}
        found.update({int(k): v for k, v in re.findall(r'"(\d+)"\s*:\s*"\(?([A-D])\)?"', rep)})
        return found  # regex, not json.loads: robust to code fences, prose and a truncated final rationale
    answers, unparsed, retry = [], 0, []
    for b, rep in zip(range(0, len(items), BATCH), replies):
        found = grab(rep)
        for k in range(1, len(items[b:b + BATCH]) + 1):
            answers.append(found.get(k, "?"))
            if k not in found:
                retry.append(b + k - 1)
    if retry:  # one strict letters-only retry for anything missing
        rp = [f"{fmt_item(1, items[i], anchors[i] if anchors else None, anchor_label)}{extra}\n\nReply with ONLY this JSON: "
              '{"1": "<letter>"}' for i in retry]
        reps = chat_many(rp, system=sysmsg, size=size, max_tokens=20, workers=8); n_calls += len(rp)
        for i, rep in zip(retry, reps):
            answers[i] = grab(rep).get(1, "?")
    unparsed = sum(a == "?" for a in answers)
    return answers, unparsed, n_calls


# ---------------------------------------------------------------- main

def run_llm():
    import llm
    items = load_items()
    log(f"{len(items)} items: " + ", ".join(f"{k} {sum(r['stratum'] == k for r in items)}" for k in ["diagnosis", "management", "mechanism/other"]))
    gold = [r["answer_idx"] for r in items]
    calls = 0
    a_ind, ua, c = ask(CLIN, items); calls += c
    b_ind, ub, c = ask(MODEL, items); calls += c
    log(f"independent readers done ({calls} calls)")
    rng = np.random.default_rng(SEED + 1)

    def wrong_anchor(r):
        return str(rng.choice([L for L in "ABCD" if L != r["answer_idx"]]))

    def anchors(real):
        """clinician: the other reader's real answers. enriched: real answers, plus a wrong answer planted on a seeded
        third of the cases the other reader got right (so enough wrong anchors exist to measure conformity).
        always_wrong: a wrong option on every case."""
        if ANCHOR_SRC == "always_wrong":
            return [wrong_anchor(r) for r in items]
        outa = []
        for a, r in zip(real, items):
            if a not in "ABCD" or a == "?":
                a = wrong_anchor(r)
            elif ANCHOR_SRC == "enriched" and a == r["answer_idx"] and rng.random() < 1 / 3:
                a = wrong_anchor(r)
            outa.append(a)
        return outa
    out = {"items": items, "gold": gold, "a_ind": a_ind, "b_ind": b_ind, "unparsed": ua + ub}
    if ANCHOR in ("both", "model_conforms"):
        anc = anchors(a_ind)
        b_anc, u, c = ask(MODEL, items, anc, "Treating clinician's initial impression"); calls += c; out["unparsed"] += u
        out.update(b_anc=b_anc, anchor_for_model=anc)
    if ANCHOR in ("both", "clinician_defers"):
        anc = anchors(b_ind)
        a_anc, u, c = ask(CLIN, items, anc, "AI assistant's suggested answer"); calls += c; out["unparsed"] += u
        out.update(a_anc=a_anc, anchor_for_clinician=anc)
    out["calls"] = calls; out["backend"] = llm.backend()
    out["models"] = {"clinician_proxy": f"{CLIN} ({llm.model_name(READERS[CLIN][0])})", "audit_model": f"{MODEL} ({llm.model_name(READERS[MODEL][0])})"}
    log(f"assisted workflows done ({calls} calls total)")
    return out


def parse_byo(txt):
    sets = []
    for part in txt.split("|"):
        nums = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", part)]
        if len(nums) >= 4:
            sets.append(nums[:4])
    if not sets or sum(sets[0]) == 0:
        raise SystemExit("byo_counts must be 'shared_success,model_only_error,clinician_only_error,shared_error' "
                         "(optionally '| same four counts for the assisted workflow')")
    return sets


def simulator():
    pc, pm = SIM_CLIN, SIM_ACC
    lo, hi, ind = max(0.0, (1 - pc) + (1 - pm) - 1), min(1 - pc, 1 - pm), (1 - pc) * (1 - pm)
    out = []
    for name, df in [("complementary", lo), ("independent", ind), ("redundant", hi)]:
        n00 = df; n01 = (1 - pc) - df; n10 = (1 - pm) - df; n11 = 1 - n00 - n01 - n10
        k = [round(x * 1000) for x in (n11, n10, n01, n00)]
        st = from_counts(*k)
        out.append({"name": name, "double_fault": df, "rescue_rate": st["rescue_rate"], "yules_q": st["yules_q"],
                    "team_ceiling": 1 - df, "cells_per_1000": dict(zip(CELLS, k))})
    return {"clinician_accuracy": pc, "model_accuracy": pm, "models": out}


def main():
    res = {"params": P, "mode": "byo" if BYO else "llm", "gates_thresholds": GATES}
    if BYO:
        sets = parse_byo(BYO)
        off = from_counts(*sets[0]); ass = from_counts(*sets[1]) if len(sets) > 1 else None
        res.update(offline=off, assisted=ass, gates=gates(off, ass), llm_calls=0)
        log(f"BYO counts: N={off['n']}, double-fault {off['double_fault']:.3f}, Q {off['yules_q']:.2f}")
    else:
        L = run_llm(); gold = np.array(L["gold"])
        a_ok = np.array(L["a_ind"]) == gold; b_ok = np.array(L["b_ind"]) == gold
        off = paired(a_ok, b_ok); off["yules_q_ci"] = boot_q(a_ok, b_ok)
        res.update(offline=off, llm_calls=L["calls"], backend=L["backend"], models=L["models"], unparsed_answers=L["unparsed"],
                   n_items=len(gold), dataset="MedQA-USMLE 4-option test split (GBaker/MedQA-USMLE-4-options, CC-BY-4.0)")
        a_ans, b_ans = np.array(L["a_ind"]), np.array(L["b_ind"])
        res["agree_offline"] = float(np.mean(a_ans == b_ans))
        ass = None
        if "b_anc" in L:  # clinician-first workflow: model answers second, sees clinician impression
            anc = np.array(L["anchor_for_model"]); b_anc = np.array(L["b_anc"]); ba_ok = b_anc == gold
            imp_ok = anc == gold  # the "clinician" in this workflow is the impression actually shown
            ref = paired(imp_ok, b_ok); ass = paired(imp_ok, ba_ok); ass["yules_q_ci"] = boot_q(imp_ok, ba_ok)
            wrong = anc != gold
            res["model_conforms"] = {
                "offline_reference": ref, "assisted": ass, "n_wrong_anchors": int(wrong.sum()),
                "n_planted": int(np.sum(anc != np.array(L["a_ind"]))),
                "rescue_offline": ref["rescue_rate"], "rescue_assisted": ass["rescue_rate"],
                "copied_wrong_anchor_independent": float(np.mean(b_ans[wrong] == anc[wrong])) if wrong.any() else None,
                "copied_wrong_anchor_assisted": float(np.mean(b_anc[wrong] == anc[wrong])) if wrong.any() else None,
                "model_accuracy_independent": float(b_ok.mean()), "model_accuracy_assisted": float(ba_ok.mean()),
                "switched_answers": int(np.sum(b_anc != b_ans)),
                "switched_right_to_wrong": int(np.sum(b_ok & ~ba_ok)), "switched_wrong_to_right": int(np.sum(~b_ok & ba_ok))}
        if "a_anc" in L:  # clinician sees the AI suggestion first (automation bias)
            anc = np.array(L["anchor_for_clinician"]); a_anc = np.array(L["a_anc"]); aa_ok = a_anc == gold
            wrong = anc != gold
            sug_ok = anc == gold
            res["clinician_defers"] = {
                "offline_reference": paired(a_ok, sug_ok), "assisted": paired(aa_ok, sug_ok), "n_wrong_suggestions": int(wrong.sum()),
                "n_planted": int(np.sum(anc != np.array(L["b_ind"]))),
                "copied_wrong_suggestion_independent": float(np.mean(a_ans[wrong] == anc[wrong])) if wrong.any() else None,
                "copied_wrong_suggestion_assisted": float(np.mean(a_anc[wrong] == anc[wrong])) if wrong.any() else None,
                "clinician_acc_when_ai_wrong_independent": float(a_ok[wrong].mean()) if wrong.any() else None,
                "clinician_acc_when_ai_wrong_assisted": float(aa_ok[wrong].mean()) if wrong.any() else None,
                "clinician_accuracy_independent": float(a_ok.mean()), "clinician_accuracy_assisted": float(aa_ok.mean())}
            cd = res["clinician_defers"]
            if wrong.any():
                cd["accuracy_drop_pp_when_ai_wrong"] = 100 * (cd["clinician_acc_when_ai_wrong_independent"] - cd["clinician_acc_when_ai_wrong_assisted"])
        res["assisted"] = ass
        res["gates"] = gates(res["model_conforms"]["offline_reference"] if ass else off, ass)
        if ass:  # gate 1 / model-only part always judged on the real offline pair
            g = gates(off, None); res["gates"]["gate1_accuracy_and_low_overlap"] = g["gate1_accuracy_and_low_overlap"]
            res["gates"]["gate2_model_only_part"] = g["gate2_model_only_part"]
            if res["gates"]["gate2_model_only_harm_and_preserved_independence"] is not None:
                res["gates"]["gate2_model_only_harm_and_preserved_independence"] = bool(
                    g["gate2_model_only_part"] and res["gates"]["rescue_retained"] >= GATES["rescue_retained"])
        cd = res.get("clinician_defers")
        if cd and cd.get("clinician_acc_when_ai_wrong_independent"):  # the clinician's own independent judgment
            ret = cd["clinician_acc_when_ai_wrong_assisted"] / cd["clinician_acc_when_ai_wrong_independent"]
            res["gates"]["clinician_judgment_retained"] = ret
            g2 = res["gates"]["gate2_model_only_harm_and_preserved_independence"]
            res["gates"]["gate2_model_only_harm_and_preserved_independence"] = bool(
                (g2 if g2 is not None else res["gates"]["gate2_model_only_part"]) and ret >= GATES["rescue_retained"])
        strata = {}
        for k in ["diagnosis", "management", "mechanism/other"]:
            m = np.array([r["stratum"] == k for r in L["items"]])
            if m.sum() >= 4:
                st = paired(a_ok[m], b_ok[m]); st["gate1"] = bool(st["model_accuracy"] >= GATES["accuracy"] and st["double_fault"] <= GATES["double_fault"])
                strata[k] = st
        res["strata"] = strata
        res["partial_deployment_strata"] = [k for k, v in strata.items() if v["gate1"]]
        res["per_item"] = [{"id": int(r["idx"]), "stratum": r["stratum"], "gold": g, "clinician": a, "model": b,
                            "model_assisted": L.get("b_anc", [None] * len(gold))[i], "clinician_assisted": L.get("a_anc", [None] * len(gold))[i]}
                           for i, (r, g, a, b) in enumerate(zip(L["items"], L["gold"], L["a_ind"], L["b_ind"]))]
    global SIM_CLIN
    SIM_CLIN = round(res["offline"]["clinician_accuracy"], 2)
    res["simulator"] = simulator()
    figures(res); card(res)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=lambda o: None))
    o = res["offline"]; g = res["gates"]
    log(f"done: N={o['n']} acc clin {o['clinician_accuracy']:.2f} model {o['model_accuracy']:.2f}; double-fault "
        f"{o['double_fault']:.3f} (indep {o['double_fault_if_independent']:.3f}); Q {o['yules_q']:.2f}; gate1 "
        f"{g['gate1_accuracy_and_low_overlap']} gate2 {g['gate2_model_only_harm_and_preserved_independence']}; "
        f"{res.get('llm_calls', 0)} LLM calls")


# ---------------------------------------------------------------- figures and card

def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.0f}%"


def figures(res):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    rows = [("Offline: proxy clinician\nvs model (independent)", res["offline"])]
    mc, cd = res.get("model_conforms"), res.get("clinician_defers")
    if mc:
        if mc["n_planted"]:
            rows.append(("Shown impression vs model,\nmodel answering blind", mc["offline_reference"]))
        rows.append(("Model answers second\n(sees the impression)", mc["assisted"]))
    elif res.get("assisted"):
        rows.append(("Assisted workflow (your counts)", res["assisted"]))
    if cd:
        if cd["n_planted"]:
            rows.append(("Clinician blind vs\nshown AI suggestion", cd["offline_reference"]))
        rows.append(("Clinician answers second\n(sees the AI suggestion)", cd["assisted"]))
    fig, ax = plt.subplots(figsize=(6.4, 0.9 + 0.75 * len(rows)))
    for i, (lbl, st) in enumerate(rows[::-1]):
        left = 0
        for cname, col in zip(CELLS, CELL_COL):
            v = st[cname.replace(" ", "_").replace("-", "_")] / st["n"]
            ax.barh(i, v, left=left, color=col, height=0.6)
            if v >= 0.045:
                ax.text(left + v / 2, i, f"{st[cname.replace(' ', '_').replace('-', '_')]}", ha="center", va="center",
                        color="white" if col != "#ced4da" else INK, fontsize=9, fontweight="bold")
            left += v
        ax.text(1.01, i, f"DF {st['double_fault']:.0%}\nQ {st['yules_q']:+.2f}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=8.5)
    ax.set_xlim(0, 1); ax.set_xlabel(f"Share of {res['offline']['n']} cases")
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in CELL_COL], CELLS, ncol=4, fontsize=7, frameon=False,
              loc="lower center", bbox_to_anchor=(0.45, 1.0), handlelength=1.2, columnspacing=1.0)
    fig.tight_layout(); fig.savefig(OUT / "fig_paired_2x2.png", dpi=160); plt.close(fig)

    if res["mode"] == "llm" and (mc or cd):
        fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.0))
        ax = axs[0]; labels, ind, assd = [], [], []
        if res.get("model_conforms") and res["model_conforms"]["n_wrong_anchors"]:
            mc = res["model_conforms"]; labels.append(f"model copies wrong\nclinician impression\n(n={mc['n_wrong_anchors']})")
            ind.append(mc["copied_wrong_anchor_independent"]); assd.append(mc["copied_wrong_anchor_assisted"])
        if res.get("clinician_defers") and res["clinician_defers"]["n_wrong_suggestions"]:
            cd = res["clinician_defers"]; labels.append(f"clinician copies\nwrong AI suggestion\n(n={cd['n_wrong_suggestions']})")
            ind.append(cd["copied_wrong_suggestion_independent"]); assd.append(cd["copied_wrong_suggestion_assisted"])
        x = np.arange(len(labels))
        ax.bar(x - 0.18, ind, 0.36, color=MUTED, label="answering blind")
        ax.bar(x + 0.18, assd, 0.36, color=ACC, label="after seeing it")
        for xi, (u, v) in enumerate(zip(ind, assd)):
            ax.text(xi - 0.18, u + 0.02, pct(u), ha="center", fontsize=8); ax.text(xi + 0.18, v + 0.02, pct(v), ha="center", fontsize=8)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.5); ax.set_ylim(0, 1.1); ax.set_ylabel("share giving the same wrong answer")
        ax.legend(frameon=False, fontsize=7.5, loc="upper left")
        ax = axs[1]
        pts = ([("model\nblind", mc["offline_reference"]), ("model\n2nd", mc["assisted"])] if mc else []) \
            + ([("clinician\nblind", cd["offline_reference"]), ("clinician\n2nd", cd["assisted"])] if cd else [])
        for i, (lbl, st) in enumerate(pts):
            ax.errorbar(i, st["double_fault"], yerr=[[st["double_fault"] - st["double_fault_ci"][0]], [st["double_fault_ci"][1] - st["double_fault"]]],
                        fmt="o", color=INK, capsize=3)
            ax.plot(i, st["double_fault_if_independent"], "_", color=ACC, ms=16, mew=2)
        ax.set_xticks(range(len(pts))); ax.set_xticklabels([p[0] for p in pts], fontsize=7.5)
        ax.set_ylabel("double-fault rate vs shown answer"); ax.set_title("● observed   — expected if independent", fontsize=8, loc="left")
        ax.set_xlim(-0.5, len(pts) - 0.5)
        fig.tight_layout(); fig.savefig(OUT / "fig_conformity.png", dpi=160); plt.close(fig)

    sim = res["simulator"]
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    for i, m in enumerate(sim["models"]):
        bottom = 0
        for cname, col in zip(CELLS, CELL_COL):
            v = m["cells_per_1000"][cname] / 1000
            ax.bar(i, v, bottom=bottom, color=col, width=0.6); bottom += v
        ax.text(i, 1.02, f"DF {m['double_fault']:.1%}\nrescue {pct(m['rescue_rate'])}", ha="center", fontsize=7.5)
    ax.set_xticks(range(3)); ax.set_xticklabels([m["name"] for m in sim["models"]], fontsize=8)
    ax.set_ylim(0, 1.18); ax.set_ylabel("share of cases")
    ax.set_title(f"All three models are {sim['model_accuracy']:.0%} accurate\n(clinician {sim['clinician_accuracy']:.0%})", fontsize=8.5, loc="left")
    ax = axs[1]
    ns = np.unique(np.round(np.logspace(np.log10(20), np.log10(3000), 60)).astype(int))
    for m, col in zip(sim["models"], [BLUE, MUTED, INK]):
        hw = [(wilson(m["double_fault"] * n, n)[1] - wilson(m["double_fault"] * n, n)[0]) / 2 for n in ns]
        ax.plot(ns, hw, color=col, lw=1.5, label=f"true DF {m['double_fault']:.1%}")
    ax.set_xscale("log"); ax.set_ylim(0, None); top = ax.get_ylim()[1]
    ax.axvline(res["offline"]["n"], color=ACC, ls="--", lw=1); ax.text(res["offline"]["n"] * 1.08, top * 0.55, f"your n={res['offline']['n']}", color=ACC, fontsize=7.5)
    ax.axvline(1000, color=GOOD, ls=":", lw=1); ax.text(1000 / 1.08, top * 0.04, "paper ~1,000", color=GOOD, fontsize=7.5, ha="right")
    ax.set_xlabel("adjudicated cases"); ax.set_ylabel("95% CI half-width of DF"); ax.legend(frameon=False, fontsize=7, loc="upper right", bbox_to_anchor=(1.0, 1.12))
    fig.tight_layout(); fig.savefig(OUT / "fig_simulator.png", dpi=160); plt.close(fig)

    if res.get("strata"):
        st = res["strata"]; ks = list(st)
        fig, ax = plt.subplots(figsize=(6.4, 2.7))
        x = np.arange(len(ks))
        for j, (key, col, lbl) in enumerate([("clinician_accuracy", BLUE, "clinician-proxy accuracy"), ("model_accuracy", GOOD, "model accuracy"),
                                             ("double_fault", INK, "double-fault rate")]):
            ax.bar(x + (j - 1) * 0.26, [st[k][key] for k in ks], 0.26, color=col, label=lbl)
        for i, k in enumerate(ks):
            ax.text(i, 1.04, f"n={st[k]['n']} · Q {st[k]['yules_q']:+.2f} · gate1 {'PASS' if st[k]['gate1'] else 'FAIL'}", ha="center", fontsize=7.5)
        ax.axhline(GATES["double_fault"], color=ACC, ls="--", lw=1)
        ax.text(len(ks) - 0.5, GATES["double_fault"] + 0.02, f"DF gate ≤ {GATES['double_fault']:.0%}", color=ACC, fontsize=7.5, ha="right")
        ax.set_xticks(x); ax.set_xticklabels(ks); ax.set_ylim(0, 1.15); ax.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
        fig.tight_layout(); fig.savefig(OUT / "fig_strata.png", dpi=160); plt.close(fig)


def card(res):
    o, g = res["offline"], res["gates"]
    gtxt = lambda v: "n/a" if v is None else ("PASS" if v else "FAIL")
    tiles = [{"label": "Double-fault rate (both wrong)", "value": f"{o['double_fault']:.1%}",
              "sub": f"{o['shared_error']}/{o['n']} cases · {o['double_fault_if_independent']:.1%} if errors were independent · "
                     f"95% CI {o['double_fault_ci'][0]:.0%}–{o['double_fault_ci'][1]:.0%}", "tone": "accent"},
             {"label": "Error association (Yule's Q)", "value": f"{o['yules_q']:+.2f}",
              "sub": ("CI " + f"[{o['yules_q_ci'][0]:+.2f}, {o['yules_q_ci'][1]:+.2f}] · " if o.get("yules_q_ci") else "")
                     + "+1 = fail together, 0 = independent, −1 = complementary", "tone": "warn" if o["yules_q"] > 0.3 else "good"}]
    mc, cd = res.get("model_conforms"), res.get("clinician_defers")
    conf = []
    if mc and mc["n_wrong_anchors"]:
        conf.append(("model", mc["copied_wrong_anchor_independent"], mc["copied_wrong_anchor_assisted"], mc["n_wrong_anchors"], "clinician impression"))
    if cd and cd["n_wrong_suggestions"]:
        conf.append(("proxy clinician", cd["copied_wrong_suggestion_independent"], cd["copied_wrong_suggestion_assisted"], cd["n_wrong_suggestions"], "AI suggestion"))
    if conf:
        conf.sort(key=lambda c: -(c[2] - c[1]))
        w, a, b, n, what = conf[0]
        other = "" if len(conf) < 2 else f" · {conf[1][0]}: {pct(conf[1][1])} → {pct(conf[1][2])}"
        tiles.append({"label": f"Wrong answers copied by the {w}", "value": f"{pct(a)} → {pct(b)}",
                      "sub": f"blind → after seeing a wrong {what} (n={n}){other}", "tone": "warn" if b - a > 0.1 else "good"})
    elif res.get("assisted"):
        tiles.append({"label": "Rescue potential, offline → assisted", "value": f"{pct(o['rescue_rate'])} → {pct(res['assisted']['rescue_rate'])}",
                      "sub": "share of clinician errors the model gets right", "tone": "warn"})
    else:
        tiles.append({"label": "Rescue potential", "value": pct(o["rescue_rate"]), "sub": "share of clinician errors the model gets right (offline only)", "tone": "neutral"})
    tiles.append({"label": "Go / no-go gates", "value": f"{gtxt(g['gate1_accuracy_and_low_overlap'])} · {gtxt(g['gate2_model_only_harm_and_preserved_independence'])}",
                  "sub": f"Gate 1: model acc ≥ {GATES['accuracy']:.0%} & DF ≤ {GATES['double_fault']:.0%}. Gate 2: model-only ≤ {GATES['model_only']:.0%} & "
                         f"rescue (and clinician accuracy on AI-wrong cases) retained ≥ {GATES['rescue_retained']:.0%}; illustrative site thresholds",
                  "tone": "good" if g["gate1_accuracy_and_low_overlap"] and g["gate2_model_only_harm_and_preserved_independence"] else "accent"})
    if res["mode"] == "llm":
        inputs = {"clinician proxy": res["models"]["clinician_proxy"], "model under audit": res["models"]["audit_model"],
                  "items": f"{o['n']} MedQA-USMLE", "case mix": MIX, "anchoring": ANCHOR, "anchor source": ANCHOR_SRC,
                  "LLM calls": res["llm_calls"]}
    else:
        inputs = {"mode": "your paired counts", "offline counts": BYO.split("|")[0].strip(),
                  "assisted counts": BYO.split("|")[1].strip() if "|" in BYO else "—"}
    sim = res["simulator"]["models"]
    compare = [
        {"metric": "Same accuracy, different overlap", "paper": "“Two models can both be 90% accurate while one fails exactly where clinicians fail and the other catches clinician misses.”",
         "yours": f"Simulator at {SIM_ACC:.0%}: DF {sim[0]['double_fault']:.1%} (rescue {pct(sim[0]['rescue_rate'])}) vs {sim[2]['double_fault']:.1%} (rescue {pct(sim[2]['rescue_rate'])})", "note": "no LLM; exact 2x2"},
        {"metric": "Sizing principle", "paper": "“a serious-harm outcome near 1% prevalence implies a sample on the order of 1,000 adjudicated cases to expect 10 such events”",
         "yours": f"n = {o['n']}; DF 95% CI {o['double_fault_ci'][0]:.0%}–{o['double_fault_ci'][1]:.0%}"
                  + (f"; ~{o['cases_to_expect_10_shared_errors']} cases to expect 10 shared errors" if o['cases_to_expect_10_shared_errors'] else ""), "note": "this run is a demo, not an audit"}]
    if mc and mc["n_wrong_anchors"]:
        compare.append({"metric": "Model conforms when it answers second", "paper": "model reproduced all of the clinician’s listed diagnoses in 48% of cases when it answered second versus 3% when it answered first (Everett et al., 2026, cited)",
                        "yours": f"copied a wrong impression {pct(mc['copied_wrong_anchor_assisted'])} vs {pct(mc['copied_wrong_anchor_independent'])} blind", "note": "different measure; LLM-vs-LLM proxy"})
    if cd and cd.get("accuracy_drop_pp_when_ai_wrong") is not None:
        compare.append({"metric": "Automation bias", "paper": "Incorrect LLM recommendations lowered physicians’ accuracy by 14 to 18 percentage points (Qazi et al., 2026, cited)",
                        "yours": f"proxy-clinician accuracy on AI-wrong cases: {pct(cd['clinician_acc_when_ai_wrong_independent'])} → {pct(cd['clinician_acc_when_ai_wrong_assisted'])} ({cd['accuracy_drop_pp_when_ai_wrong']:.0f}-point drop)", "note": "small-model proxy, not physicians"})
    if res["mode"] == "llm":
        compare.append({"metric": "Human–model vs model–model diversity", "paper": "human-model error diversity exceeded model-model diversity (Zoller et al., 2025, cited)",
                        "yours": f"model–model Q {o['yules_q']:+.2f}, disagreement {o['disagreement']:.0%}", "note": "this run is model–model only"})
    figs = [{"path": "fig_paired_2x2.png", "title": "Where do the two readers fail: on the same cases or on different ones?",
             "caption": "The paper's paired 2x2 per workflow. Orange = model-only error (substitution risk), blue = clinician-only error "
                        "(rescue potential), dark = shared error (common-mode failure). DF = double-fault rate; Q = Yule's Q."}]
    if (OUT / "fig_conformity.png").exists():
        figs.append({"path": "fig_conformity.png", "title": "Does independence survive once one reader sees the other's answer?",
                     "caption": "Left: on cases where the shown answer was wrong, how often the second reader gave that same wrong answer when blind vs after "
                                "seeing it. Right: double-fault rate per workflow with 95% Wilson CI; the orange tick is what independence would give."})
    if (OUT / "fig_strata.png").exists():
        figs.append({"path": "fig_strata.png", "title": "Does the answer change with case mix?",
                     "caption": "Per-stratum accuracy and double-fault rate (question type parsed from the stem). Strata that pass Gate 1 are the candidates "
                                "for partial deployment; with ~12 cases each these are illustrations, not estimates."})
    figs.append({"path": "fig_simulator.png", "title": "Why accuracy alone cannot answer the question",
                 "caption": f"Left: three hypothetical models, all {SIM_ACC:.0%} accurate next to a {SIM_CLIN:.0%}-accurate clinician, with minimum, independent "
                            "and maximum overlap. Right: how many adjudicated cases it takes to pin the double-fault rate down."})
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 1, "title": "Complementary Vulnerabilities: Auditing and Governing Clinician–LLM Error Overlap",
                  "authors": "Mohsen Amoei, Kathleen Fraser, Dan Poenaru", "url": "https://drive.google.com/file/d/1_bJ_5DA5k0V2X1XuuxliKg5WdLPq1SMP/view?usp=sharing", "affiliation": "McGill University · RI-MUHC · Mila · University of Ottawa"},
        "inputs": inputs, "tiles": tiles, "figures": figs, "compare": compare,
        "runbook": {"name": "smash-01-complementary-vulnerabilities", "url": P.get("runbook_url", "")}}, indent=2))


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
