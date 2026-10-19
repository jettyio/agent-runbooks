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
    skill_name: smash-11-masq-questionnaire
    confidence: high
---

# MASQ: Screen a Multi-Agent System, Then Watch It Fail (SMASH 2026 · Paper #11)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"MASQ: The Multi-Agent System Questionnaire"** (Nils Kiele, Niki Mehri, Aaron Arellano, Samira Ebrahimi Kahou).
Read the paper: https://drive.google.com/file/d/1Rp0p5g3H-GnNNV-2aCJPC3Ke3VbRcm0C/view?usp=sharing

The paper's claim: miscoordination failures in LLM multi-agent systems (MAS) are catalogued after the fact by
MAST (14 failure modes, Cemri et al.), but developers need a way to **anticipate** them from design choices and then
**check** them against execution. MASQ is a three-stage questionnaire: **Stage 1** records five design dimensions;
**Stage 2** rates each of the 14 MAST failure modes Low / Mid / High through a fixed dimension→mode mapping;
**Stage 3** compares those anticipations with execution traces. On ChatDev, the authors' Stage 2 correctly
anticipated 8/14 modes; their biggest miss was rating "No or incomplete verification" Low while it occurred in
11/30 traces.

The participant pastes a description of their MAS (default: ChatDev, exactly as the paper describes it; a second
group-chat example is built in). An LLM fills Stage 1 and classifies, for each failure mode, whether the design
protects against it with an **explicit guardrail**, **prompt-only** constraints, or whether the risk is
**architectural**; code applies the paper's rule (Low / Mid / High). For ChatDev the result is overlaid on the
authors' Table 2 and scored against the paper's 30 annotated traces. Then **Stage 3 runs for real**: a tiny
ChatDev-shaped chat chain (CTO → programmer ⇄ reviewer → tester, capped rounds) solves small coding tasks whose
requests are slightly underspecified, hidden unit tests check the final code, an LLM annotates every trace against
MAST, and code flags where anticipated ≠ observed. Output: a shareable **result card**.

Target wall-clock: **under 4 minutes.** The experiment takes ~40 s (about 35 small LLM calls).

### The method, as in the paper
- Stage 1 dimensions (Table 1): agent configuration; network topology; communication; task dynamics; memory state architecture.
- Stage 2 mapping (fixed, Table 2 sections): agent configuration → FM-1.2, FM-2.6; network topology → FM-1.3, FM-2.5;
  communication → FM-2.2, FM-2.4; task dynamics → FM-3.1, FM-1.1, FM-1.5, FM-2.3, FM-3.2, FM-3.3; memory → FM-1.4, FM-2.1.
  (Section boundaries are read from the order of Table 2's rows.)
- Rule (§3): "Low risk likelihood if explicit guardrails mitigate the risk, Mid for reliance on prompt-based soft
  constraints rather than hard system limits, and High for risks inherent to the architecture itself."
- Stage 3 match rule (this runbook's reconstruction, which reproduces all 14 of the paper's (!) flags): Low fits
  ≤ 2/30 of traces, Mid fits 2/30–8/30, High fits ≥ 8/30.

### Paper numbers (quote exactly)
- "Stage 2 correctly predicts 8/14 MAST risks, but significantly underestimates the failure mode 'No or incomplete verification,' occurring in 11/30 traces."
- "we overestimated five risk categories: High memory-loss and Mid role-drift and premature termination rarely manifested (≤ 2/30)."
- Table 2 (risk; Stage 3 of 30): FM-1.2 Mid 0 (!); FM-2.6 Mid 5; FM-1.3 Mid 7; FM-2.5 Low 1; FM-2.2 Low 2; FM-2.4 Mid 1 (!);
  FM-3.1 Mid 1 (!); FM-1.1 Mid 8; FM-1.5 Low 2; FM-2.3 Mid 2; FM-3.2 Low 11 (!); FM-3.3 Mid 5; FM-1.4 High 2 (!); FM-2.1 High 1 (!).
- "role-prompting does not substitute for formal, mechanical verification."

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | Stage 1–3 outputs and all computed numbers (written by `experiment.py`) |
| `traces.json` | Full Stage-3 transcripts with MAST annotations (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| System preset | `{{system_preset}}` | `chatdev` | `chatdev` (the paper's ChatDev description; overlaid on Table 2) or `groupchat` (a hypothetical research-assistant group chat written for this runbook) |
| Your system | `{{system_description}}` | — | Paste a description of **your** multi-agent system (roles, who talks to whom, how they communicate, termination and verification, memory). Overrides the preset |
| Run Stage 3 | `{{run_stage3}}` | `true` | Run the mini chat chain and annotate its traces (`false` = Stages 1–2 only, ~10 s) |
| Traces | `{{n_traces}}` | `5` | Number of Stage-3 traces (2–6; one coding task each) |
| Mini-MAS verification | `{{mas_verification}}` | `prompt` | `prompt` (tester reads the code, like ChatDev's role-prompted tester) or `tests` (tester's asserts are actually executed) |
| Mini-MAS memory | `{{mas_memory}}` | `drop` | `drop` (only the final artefact passes between phases, like ChatDev) or `shared` (full history visible) |
| Review rounds | `{{max_rounds}}` | `2` | Hard cap on reviewer ⇄ programmer rounds (1–3) |
| Annotator size | `{{annotator_size}}` | `small` | `small` (Claude Haiku) or `large` (Claude Sonnet) for the MAST trace annotation |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). No downloads. LLM access: `llm.py` (embedded) uses the
sandbox's OpenRouter/Anthropic/OpenAI key. Stage 3 executes the agents' generated Python functions (and, with
`tests`, their assert statements) in a separate `python -I` process with a 10 s timeout inside the sandbox.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json`. If a value still looks like an unsubstituted `{{…}}` placeholder use the table
default; use `""` for a blank `system_description`. Convert `run_stage3` to a JSON boolean. Put
`system_description` into a JSON string with proper escaping (write the file with Python `json.dump` if it contains
quotes or newlines). Clamp `n_traces` to [2, 6] and `max_rounds` to [1, 3]; record any change as a caveat.

```json
{"system_preset": "{{system_preset}}", "system_description": "{{system_description}}", "run_stage3": {{run_stage3}},
 "n_traces": {{n_traces}}, "mas_verification": "{{mas_verification}}", "mas_memory": "{{mas_memory}}",
 "max_rounds": {{max_rounds}}, "annotator_size": "{{annotator_size}}", "runbook_url": ""}
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

Expected: ~40 s, ending with a `done:` line (ChatDev agreement and anticipated-correctly score, mini-MAS score,
hidden-test pass rate, LLM calls). On an HTTP error run it once more; finished calls are cached in `/app/work/llm_cache.json`.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` (`stage1`, `stage2` with rationales, `chatdev`, `mini`, `traces`) and
`card_data.json`, skim `traces.json` for one concrete example, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the most striking result of *this* run with 1–2 numbers from `results.json`, e.g. the
  LLM screen's ChatDev score vs the authors' 8/14, or how many mini-MAS traces declared the work verified while hidden
  tests failed (`declared_done_but_hidden_fail`), or a confident Low that Stage 3 contradicted.
- **idea**: (1) MASQ turns MAST's after-the-fact failure taxonomy into a design-time screen; (2) the fixed mapping
  from 5 design dimensions to 14 failure modes plus the guardrail / prompt-only / architectural rule; (3) Stage 3
  confronts the stated assumptions with traces, and mismatches are the useful output.
- **findings**: (1) Stage 2 for the described system: risk profile, notable rationales; for ChatDev, agreement with
  the authors (`agree_with_authors`) and the score against the paper's traces (`llm_screen_correct_vs_paper_traces`
  vs 8/14), especially FM-3.2 and the memory modes; (2) Stage 3: anticipated vs observed for the mini chain
  (`correctly_anticipated`, which modes carry (!)); (3) verification: `declared_done_but_hidden_fail` and what the
  hidden tests caught (often an ambiguous variant nobody asked about: FM-2.2 / FM-1.1); relate to the paper's
  "role-prompting does not substitute for formal, mechanical verification".
- **try_next**: 2–3 runs with exact values using only the keys `system_preset, system_description, run_stage3,
  n_traces, mas_verification, mas_memory, max_rounds, annotator_size`. Good contrasts: `mas_verification` `tests`
  (does mechanical verification fix it, and does the screen now rate FM-3.2 Low?); `mas_memory` `shared`;
  `system_preset` `groupchat`; or the participant's own `system_description`.
- **caveats**: the Stage-2 ratings are an LLM's judgement, not the authors'; the mini chain is a ChatDev-shaped toy
  written for this runbook, not ChatDev, and its traces are annotated by an LLM (MAST's own annotations were also
  LLM-based, with a different model); with 2–6 traces observed rates are very coarse against a rule calibrated on
  30; the dimension boundaries and the match rule are reconstructed from Table 2.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: system, Stage-2 risk counts, ChatDev comparison if any, mini-MAS
anticipated vs observed, verification finding, headline).

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
python3 - "{{results_dir}}" "system_preset,system_description,run_stage3,n_traces,mas_verification,mas_memory,max_rounds,annotator_size" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} system_preset,system_description,run_stage3,n_traces,mas_verification,mas_memory,max_rounds,annotator_size 300 checklist.json
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
"""MASQ: the Multi-Agent System Questionnaire — SMASH 2026 paper #11 (Kiele, Mehri, Arellano, Kahou).

Stage 1: an LLM records the five design dimensions of a described multi-agent system (MAS).
Stage 2: for each of the 14 MAST failure modes (fixed 5→14 dimension mapping, paper Table 2) an LLM classifies the
         design's protection as explicit guardrail / prompt-only / architectural; code maps that to Low / Mid / High
         with the paper's rule.
Stage 3: a tiny ChatDev-shaped chat chain (CTO → programmer ⇄ reviewer → tester; LLM calls, capped rounds) solves
         small coding tasks with hidden unit tests; an LLM annotates each trace against MAST; code compares
         anticipated vs observed with a matching rule that reproduces the paper's (!) flags exactly.
For the ChatDev default, the LLM screen is overlaid on the authors' Table 2 (8/14 correctly anticipated).

usage: python experiment.py params.json outdir
"""
import concurrent.futures as cf, json, re, subprocess, sys, tempfile, textwrap, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
INK, ACC, BLUE, MUTED, GOOD, AMBER = "#1f2a44", "#d9480f", "#1971c2", "#868e96", "#2b8a3e", "#f59f00"
RISK_COL = {"Low": "#b2f2bb", "Mid": "#ffe066", "High": "#ffa8a8", "?": "#e9ecef"}
FENCE = "`" * 3


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def s(key, default):
    v = P.get(key, default)
    return default if v is None or (isinstance(v, str) and (v.strip() == "" or v.strip().startswith("{{"))) else v


PRESET = str(s("system_preset", "chatdev")); DESC = str(s("system_description", "")).strip()
RUN3 = str(s("run_stage3", "true")).lower() in ("true", "1", "yes")
N_TRACES = int(min(6, max(2, int(float(s("n_traces", 5))))))
VERIF = str(s("mas_verification", "prompt")); MEMORY = str(s("mas_memory", "drop"))
ROUNDS = int(min(3, max(1, int(float(s("max_rounds", 2))))))
ANNOT = str(s("annotator_size", "small"))

# ---------------------------------------------------------------- MASQ / MAST constants (paper Table 2)
DIMS = ["Agent configuration", "Network topology", "Communication", "Task dynamics", "Memory state architecture"]
DIM_WHAT = {  # paper Table 1
    "Agent configuration": "Models and modalities, agent roles, tools, autonomy, relevant training, prompting choices.",
    "Network topology": "Which agents communicate, interaction orchestration, overall communication structure.",
    "Communication": "Task-relevant information exchange, sharing expectations, and clarification mechanisms.",
    "Task dynamics": "System/agent-level objectives, execution order, termination conditions, and verification.",
    "Memory state architecture": "How memory and state are shared, synchronized, retained, and available across agents."}
MODES = [  # (id, name, dimension, short definition paraphrased from MAST, Cemri et al.)
    ("FM-1.2", "Disobey role specification", "Agent configuration", "an agent acts outside its assigned role or responsibilities"),
    ("FM-2.6", "Reasoning-action mismatch", "Agent configuration", "an agent's stated reasoning and its actual output/action disagree"),
    ("FM-1.3", "Step repetition", "Network topology", "steps or exchanges are needlessly repeated (e.g. propose/reject loops)"),
    ("FM-2.5", "Ignored other agent's input", "Network topology", "an agent disregards instructions, feedback or results from another agent"),
    ("FM-2.2", "Fail to ask for clarification", "Communication", "an agent proceeds on ambiguous or missing information instead of asking"),
    ("FM-2.4", "Information withholding", "Communication", "relevant information one agent has is not passed to the agents that need it"),
    ("FM-3.1", "Premature termination", "Task dynamics", "the dialogue or task ends before the objective is met"),
    ("FM-1.1", "Disobey task specification", "Task dynamics", "the output violates or invents task requirements/constraints"),
    ("FM-1.5", "Unaware of termination conditions", "Task dynamics", "agents do not recognise when they should stop"),
    ("FM-2.3", "Task derailment", "Task dynamics", "the conversation drifts away from the intended objective"),
    ("FM-3.2", "No or incomplete verification", "Task dynamics", "outputs are not checked, or only partially checked, before completion"),
    ("FM-3.3", "Incorrect verification", "Task dynamics", "a check is performed but wrongly passes a faulty output"),
    ("FM-1.4", "Loss of conversation history", "Memory state architecture", "earlier context is lost so agents work from an outdated or partial state"),
    ("FM-2.1", "Conversation reset", "Memory state architecture", "a dialogue restarts and progress or agreements are lost"),
]
MODE_IDS = [m[0] for m in MODES]
PAPER = {  # ChatDev, paper Table 2: (Stage-2 risk, Stage-3 count out of 30, flagged as mismatch)
    "FM-1.2": ("Mid", 0, True), "FM-2.6": ("Mid", 5, False), "FM-1.3": ("Mid", 7, False), "FM-2.5": ("Low", 1, False),
    "FM-2.2": ("Low", 2, False), "FM-2.4": ("Mid", 1, True), "FM-3.1": ("Mid", 1, True), "FM-1.1": ("Mid", 8, False),
    "FM-1.5": ("Low", 2, False), "FM-2.3": ("Mid", 2, False), "FM-3.2": ("Low", 11, True), "FM-3.3": ("Mid", 5, False),
    "FM-1.4": ("High", 2, True), "FM-2.1": ("High", 1, True)}
RULE = {"explicit_guardrail": "Low", "prompt_only": "Mid", "architectural": "High"}  # paper §3, Stage 2


def matches(risk, rate):
    """Anticipated-vs-observed rule reverse-engineered from the paper's (!) flags (reproduces all 14, i.e. 8/14):
    Low fits <= 2/30 of traces, Mid fits 2/30 .. 8/30, High fits >= 8/30."""
    k = rate * 30
    if risk == "Low":
        return k <= 2 + 1e-9
    if risk == "Mid":
        return 2 - 1e-9 <= k <= 8 + 1e-9
    if risk == "High":
        return k >= 8 - 1e-9
    return False


assert sum(matches(r, c / 30) for r, c, _ in PAPER.values()) == 8
assert all(matches(r, c / 30) != f for r, c, f in PAPER.values())

CHATDEV = (  # paper §3, Stage 1 paragraph (ChatDev, Qian et al. 2024)
    "ChatDev instantiates LLMs via inception prompting into specialized roles (CEO, CTO, programmer, reviewer, and tester). "
    "Its network topology is a sequential \"chat chain,\" mirroring the waterfall model and confining interactions to "
    "instructor-assistant pairs per phase. For communication, these pairs engage in multi-turn dialogues of natural and "
    "programming languages, using a \"communicative dehallucination\" mechanism to actively request more specific details "
    "before responding. The task dynamics dictate that sub-tasks advance only after agent consensus or forceful termination "
    "(hard limit of 10 conversation rounds or two unchanged code modifications). The memory state architecture uses two types "
    "of memory: short-term, to retain the full dialogue history within a single phase, and long-term, containing only the "
    "final solutions passed on by each sub-task. The user prompt is a short software request such as \"Develop a Gomoku game\".")
GROUPCHAT = (  # a second, hypothetical example written for this runbook
    "A research-assistant group chat with four LLM agents sharing one model: a Planner that decomposes the user's question, "
    "a Searcher that calls a web-search tool, a Coder that writes and runs Python in a sandbox (real execution with stdout "
    "returned), and a Critic. All agents see one shared, ever-growing transcript; a manager LLM picks the next speaker each turn "
    "based on the transcript. Agents may ask the user a clarifying question only at the start. The chat ends when any agent "
    "writes TERMINATE or after 20 turns. The Critic reviews the final answer by reading it; code outputs are checked only by the "
    "Coder's own run. No long-term memory beyond the transcript.")


def mini_description():
    return ("A three-phase sequential chat chain modelled on ChatDev. Roles are set by short system prompts: CTO, programmer, "
            "reviewer, tester (all the same small LLM). Phase 1: the CTO turns a one-sentence user request into a specification "
            "(single turn, no clarification channel to the user). Phase 2: the programmer writes a Python function from the "
            f"specification; the reviewer comments and the programmer revises, until the reviewer writes <APPROVED> or {ROUNDS} "
            "review rounds have passed (hard cap). Phase 3: "
            + ("the tester writes assert-based unit tests that are actually executed; failures go back to the programmer for one fix. "
               if VERIF == "tests" else "the tester reads the code and replies <PASS> or lists issues (no code is executed); one fix round. ")
            + ("Between phases only the final artefact (specification or code) is passed on; dialogue history is dropped."
               if MEMORY == "drop" else "All agents see the full conversation history from every earlier phase."))


# ---------------------------------------------------------------- Stage 1 and 2 (LLM judgement, code scoring)

def stage12(desc):
    from llm import chat, parse_json
    p1 = ("You are completing Stage 1 of MASQ (Multi-Agent System Questionnaire). Record the system's architecture along five "
          "dimensions WITHOUT judging safety:\n" + "\n".join(f"- {d}: {w}" for d, w in DIM_WHAT.items()) +
          f"\n\nSystem description:\n{desc}\n\nReturn ONLY JSON: " + '{"' + '": "<= 45 words", "'.join(DIMS) + '": "<= 45 words"}')
    prof = parse_json(chat(p1, system="You are a careful multi-agent systems analyst. Reply with JSON only.", size="small", max_tokens=700))
    modes = "\n".join(f"- {i} {n} [dimension: {d}]: {df}" for i, n, d, df in MODES)
    p2 = ("You are completing Stage 2 of MASQ. For each MAST failure mode below, look at the design choices in the dimension it "
          "is mapped to and classify how the design addresses that risk:\n"
          "- explicit_guardrail: a hard, explicit mechanism in the system mitigates it (code, enforced limit, executed checks, "
          "a dedicated mechanism)\n- prompt_only: the system relies on prompt-based soft constraints (role prompts, instructions)\n"
          "- architectural: the risk is inherent to the architecture itself (the design creates it)\n\n"
          f"Stage 1 profile:\n{json.dumps(prof, indent=1)}\n\nFull description:\n{desc}\n\nFailure modes:\n{modes}\n\n"
          'Return ONLY JSON: {"FM-1.2": {"class": "prompt_only", "rationale": "<= 20 words, architecture-based"}, ...} for all 14 modes.')
    raw = chat(p2, system="You are a careful multi-agent systems analyst. Reply with JSON only.", size="small", max_tokens=1600)
    try:
        cls = parse_json(raw)
    except ValueError:
        cls = {}
    out = {}
    for mid in MODE_IDS:
        v = cls.get(mid) or {}
        c = str(v.get("class", "")).strip().lower().replace(" ", "_").replace("-", "_") if isinstance(v, dict) else ""
        out[mid] = {"class": c, "risk": RULE.get(c, "?"), "rationale": v.get("rationale", "") if isinstance(v, dict) else ""}
    return prof, out


# ---------------------------------------------------------------- Stage 3: the mini chat chain

TASKS = [  # (user request, function name, hidden tests as (expression, expected repr))
    ("Write a function parse_duration(s) that converts durations like '1h30m' into seconds.", "parse_duration",
     [("parse_duration('1h30m')", "5400"), ("parse_duration('45s')", "45"), ("parse_duration('2h')", "7200"),
      ("parse_duration('10m5s')", "605"), ("parse_duration('1h 30m')", "5400")]),
    ("Write a function roman_to_int(s) that converts a Roman numeral to an integer.", "roman_to_int",
     [("roman_to_int('MCMXCIV')", "1994"), ("roman_to_int('IV')", "4"), ("roman_to_int('LVIII')", "58"),
      ("roman_to_int('xiv')", "14"), ("roman_to_int('MMXXV')", "2025")]),
    ("Write a function merge_intervals(intervals) that merges overlapping intervals.", "merge_intervals",
     [("merge_intervals([[1,3],[2,6],[8,10]])", "[[1, 6], [8, 10]]"), ("merge_intervals([[8,10],[1,3]])", "[[1, 3], [8, 10]]"),
      ("merge_intervals([[1,2],[2,3]])", "[[1, 3]]"), ("merge_intervals([])", "[]"), ("merge_intervals([[1,4],[2,3]])", "[[1, 4]]")]),
    ("Write a function slugify(title) that turns a title into a URL slug.", "slugify",
     [("slugify('Hello, World!')", "'hello-world'"), ("slugify('  Multiple   spaces ')", "'multiple-spaces'"),
      ("slugify('Café au lait')", "'cafe-au-lait'"), ("slugify('A--B')", "'a-b'"), ("slugify('Python 3.12 Release')", "'python-3-12-release'")]),
    ("Write a function next_business_day(date_str) that returns the next business day as 'YYYY-MM-DD'.", "next_business_day",
     [("next_business_day('2025-01-03')", "'2025-01-06'"), ("next_business_day('2025-01-04')", "'2025-01-06'"),
      ("next_business_day('2025-01-06')", "'2025-01-07'"), ("next_business_day('2024-02-28')", "'2024-02-29'"),
      ("next_business_day('2025-12-31')", "'2026-01-01'")]),
    ("Write a function top_words(text, n) that returns the n most common words.", "top_words",
     [("top_words('the cat and the hat', 1)", "['the']"), ("top_words('Dog dog DOG cat', 1)", "['dog']"),
      ("top_words('a, b. a! c', 2)", "['a', 'b']"), ("top_words('x y z', 2)", "['x', 'y']"), ("top_words('', 3)", "[]")]),
]

SYS = {"cto": "You are the CTO in a software company of AI agents. You write precise specifications.",
       "programmer": "You are the Programmer in a software company of AI agents. You write correct, clean Python.",
       "reviewer": "You are the Code Reviewer in a software company of AI agents.",
       "tester": "You are the Software Test Engineer in a software company of AI agents."}


def extract_code(t):
    m = re.findall(FENCE + r"(?:python|py)?\s*\n(.*?)" + FENCE, t, re.S)
    return max(m, key=len) if m else t


def run_code(code, tests_src, timeout=10):
    """Execute candidate code plus a test harness in a separate, isolated Python process."""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "t.py"
        f.write_text(code + "\n\n" + tests_src)
        try:
            r = subprocess.run([sys.executable, "-I", str(f)], capture_output=True, text=True, timeout=timeout, cwd=d)
            return r.stdout[-3000:], r.stderr[-1500:]
        except subprocess.TimeoutExpired:
            return "", "timeout"


def hidden_tests(code, tests):
    harness = "import json\n_n = lambda v: json.loads(json.dumps(v))  # tuples == lists\n_r = []\n" + "".join(
        f"try:\n    _r.append(_n({e}) == _n({exp}))\nexcept Exception:\n    _r.append(False)\n" for e, exp in tests) \
        + "print('HIDDEN' + json.dumps(_r))\n"
    out, err = run_code(code, harness)
    m = re.search(r"HIDDEN(\[.*\])", out)
    return json.loads(m.group(1)) if m else [False] * len(tests)


def own_tests(code, test_src):
    lines = [l for l in test_src.splitlines() if l.strip().startswith("assert")][:8]
    harness = "import json\n_r = []\n" + "".join(
        f"try:\n    {l.strip()}\n    _r.append([{l.strip()[:120]!r}, 'ok'])\nexcept Exception as _e:\n    _r.append([{l.strip()[:120]!r}, repr(_e)[:120]])\n"
        for l in lines) + "print('OWN' + json.dumps(_r))\n"
    out, err = run_code(code, harness)
    m = re.search(r"OWN(\[.*\])", out)
    return json.loads(m.group(1)) if m else [["(test harness failed)", err[-200:]]]


def run_trace(ti):
    from llm import chat
    req, fname, tests = TASKS[ti]
    msgs, calls = [], 0

    def say(role, prompt, mt=900):
        nonlocal calls
        hist = ""
        if MEMORY == "shared" and msgs:
            hist = "Conversation so far:\n" + "\n".join(f"[{m['role']}] {m['text'][:900]}" for m in msgs[-8:]) + "\n\n"
        t = chat(hist + prompt, system=SYS[role], size="small", max_tokens=mt); calls += 1
        msgs.append({"phase": phase, "role": role, "text": t}); return t
    phase = "design"
    msgs.append({"phase": phase, "role": "ceo", "text": req})
    spec = say("cto", f"The CEO says: \"{req}\"\nWrite the specification for the programmer: signature, behaviour, edge cases. "
               "Wrap the final specification in <SOLUTION>...</SOLUTION>. Keep it under 150 words.", 400)
    m = re.search(r"<SOLUTION>(.*?)</SOLUTION>", spec, re.S); spec_s = (m.group(1) if m else spec).strip()
    phase = "coding"
    code_msg = say("programmer", f"Specification:\n{spec_s}\n\nImplement `{fname}` in Python (standard library only). "
                   "Reply with one python code block.", 900)
    code = extract_code(code_msg); approved = False; rounds = 0
    for r in range(ROUNDS):
        rounds += 1
        rev = say("reviewer", f"Specification:\n{spec_s}\n\nCode:\n{FENCE}python\n{code}\n{FENCE}\n\nReview the code against the specification. "
                  "If it is correct and complete reply exactly <APPROVED>; otherwise list concrete problems (<= 80 words).", 300)
        if "<APPROVED>" in rev:
            approved = True; break
        code_msg = say("programmer", f"Reviewer comments:\n{rev}\n\nCurrent code:\n{FENCE}python\n{code}\n{FENCE}\n\nRevise `{fname}`. "
                       "Reply with one python code block.", 900)
        code = extract_code(code_msg)
    phase = "testing"; test_pass = None; own = []
    if VERIF == "tests":
        tmsg = say("tester", f"Specification:\n{spec_s}\n\nCode:\n{FENCE}python\n{code}\n{FENCE}\n\nWrite 5 assert statements that test "
                   f"`{fname}` (one per line, plain python, no imports needed). Reply with one python code block.", 400)
        own = own_tests(code, extract_code(tmsg))
        fails = [o for o in own if o[1] != "ok"]
        msgs.append({"phase": phase, "role": "executor", "text": "Executed tests: " + json.dumps(own)[:900]})
        if fails:
            code = extract_code(say("programmer", f"These tests failed when executed:\n{json.dumps(fails)[:900]}\n\nCode:\n{FENCE}python\n{code}\n{FENCE}\n\n"
                                    f"Fix `{fname}` (if a test itself is wrong, keep the code). Reply with one python code block.", 900))
            own = own_tests(code, extract_code(tmsg))
        test_pass = all(o[1] == "ok" for o in own)
    else:
        tmsg = say("tester", f"Specification:\n{spec_s}\n\nCode:\n{FENCE}python\n{code}\n{FENCE}\n\nTest this code by reasoning about it. "
                   "If it works reply exactly <PASS>; otherwise list the failing cases (<= 80 words).", 300)
        test_pass = "<PASS>" in tmsg
        if not test_pass:
            code = extract_code(say("programmer", f"Tester report:\n{tmsg}\n\nCode:\n{FENCE}python\n{code}\n{FENCE}\n\nFix `{fname}`. "
                                    "Reply with one python code block.", 900))
    hidden = hidden_tests(code, tests)
    declared_done = approved or bool(test_pass)
    return {"task": req, "function": fname, "messages": msgs, "calls": calls, "review_rounds": rounds, "approved": approved,
            "tester_pass": test_pass, "hidden_pass": sum(hidden), "hidden_total": len(hidden),
            "declared_done_but_hidden_fail": bool(declared_done and sum(hidden) < len(hidden)), "final_code": code[:3000]}


def annotate(trace):
    from llm import chat, parse_json
    cut = lambda t: t if len(t) <= 2600 else t[:2600] + "\n[... message shortened for annotation; the agent's message was complete ...]"
    tr = "\n\n".join(f"[{m['phase']} | {m['role']}]\n{cut(m['text'])}" for m in trace["messages"])
    defs = "\n".join(f"- {i} {n}: {d}" for i, n, _, d in MODES)
    p = (f"Annotate this multi-agent execution trace with the MAST failure taxonomy.\n\nFailure modes:\n{defs}\n\n"
         f"Context: the final code passed {trace['hidden_pass']}/{trace['hidden_total']} hidden unit tests that the agents never saw "
         f"(hidden tests check reasonable handling of the user's request; the agents could not see them, so never fault an agent for not running or reporting them, only for what the trace shows).\n\n"
         f"TRACE:\n{tr}\n\nFINAL CODE (complete):\n{trace['final_code']}\n\nMark a mode present only if the trace shows concrete evidence. Return ONLY JSON: "
         '{"FM-1.1": {"present": true, "evidence": "<= 15 words"}, ...} for all 14 modes.')
    try:
        d = parse_json(chat(p, system="You are an expert annotator of multi-agent LLM system failures. Reply with JSON only.",
                            size=ANNOT, max_tokens=1400))
    except ValueError:
        d = {}
    return {mid: bool((d.get(mid) or {}).get("present")) if isinstance(d.get(mid), dict) else False for mid in MODE_IDS}, \
           {mid: (d.get(mid) or {}).get("evidence", "") if isinstance(d.get(mid), dict) else "" for mid in MODE_IDS}


# ---------------------------------------------------------------- main

def main():
    import llm
    desc = DESC or (GROUPCHAT if PRESET == "groupchat" else CHATDEV)
    sysname = "your system" if DESC else ("ChatDev (paper)" if PRESET != "groupchat" else "Group-chat example")
    is_chatdev = not DESC and PRESET != "groupchat"
    jobs = {"described": desc}
    if RUN3:
        jobs["mini"] = mini_description()
    with cf.ThreadPoolExecutor(8) as ex:
        fut12 = {k: ex.submit(stage12, v) for k, v in jobs.items()}
        traces = list(ex.map(run_trace, range(N_TRACES))) if RUN3 else []
        s12 = {k: f.result() for k, f in fut12.items()}
    llm.save_cache()
    log(f"stages 1-2 done for {list(jobs)}; {len(traces)} traces run")
    calls = 4 * len(jobs) // 2 + sum(t["calls"] for t in traces)
    res = {"params": P, "backend": llm.backend(), "model": llm.model_name("small"), "annotator_model": llm.model_name(ANNOT),
           "system": sysname, "description": desc, "stage1": s12["described"][0], "stage2": s12["described"][1]}
    st2 = res["stage2"]
    res["risk_counts"] = {r: sum(v["risk"] == r for v in st2.values()) for r in ("Low", "Mid", "High", "?")}
    if is_chatdev:
        agree = sum(st2[m]["risk"] == PAPER[m][0] for m in MODE_IDS)
        within = sum(abs(["Low", "Mid", "High"].index(PAPER[m][0]) - (["Low", "Mid", "High"].index(st2[m]["risk"]) if st2[m]["risk"] in RULE.values() else 9)) <= 1 for m in MODE_IDS)
        llm_ok = {m: matches(st2[m]["risk"], PAPER[m][1] / 30) for m in MODE_IDS}
        res["chatdev"] = {"agree_with_authors": agree, "within_one_level": within, "llm_screen_correct_vs_paper_traces": sum(llm_ok.values()),
                          "authors_correct": 8, "llm_ok": llm_ok,
                          "verification_rating": st2["FM-3.2"]["risk"]}
    if RUN3:
        with cf.ThreadPoolExecutor(8) as ex:
            ann = list(ex.map(annotate, traces))
        llm.save_cache(); calls += len(traces)
        mini2 = s12["mini"][1]
        obs = {m: float(np.mean([a[0][m] for a in ann])) for m in MODE_IDS}
        flags = {m: not matches(mini2[m]["risk"], obs[m]) for m in MODE_IDS}
        for t, a in zip(traces, ann):
            t["mast"] = a[0]; t["mast_evidence"] = a[1]
        res["mini"] = {"description": jobs["mini"], "stage1": s12["mini"][0], "stage2": mini2, "observed_rate": obs,
                       "mismatch": flags, "correctly_anticipated": 14 - sum(flags.values()),
                       "hidden_pass_rate": sum(t["hidden_pass"] for t in traces) / sum(t["hidden_total"] for t in traces),
                       "declared_done_but_hidden_fail": sum(t["declared_done_but_hidden_fail"] for t in traces),
                       "approved_in_review": sum(t["approved"] for t in traces), "n_traces": len(traces),
                       "settings": {"verification": VERIF, "memory": MEMORY, "max_rounds": ROUNDS}}
        res["traces"] = [{k: v for k, v in t.items() if k != "messages"} | {"n_messages": len(t["messages"])} for t in traces]
        (OUT / "traces.json").write_text(json.dumps(traces, indent=1))
        log(f"stage 3 annotated: {res['mini']['correctly_anticipated']}/14 anticipated correctly; hidden-test pass "
            f"{res['mini']['hidden_pass_rate']:.0%}")
    res["llm_calls"] = calls
    figures(res, is_chatdev); card(res, is_chatdev)
    res["runtime_sec"] = round(time.time() - T0, 1)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    cd = res.get("chatdev"); mi = res.get("mini")
    log("done: " + (f"ChatDev agreement {cd['agree_with_authors']}/14, LLM screen correct vs paper traces "
                    f"{cd['llm_screen_correct_vs_paper_traces']}/14 (authors 8/14); " if cd else f"risks {res['risk_counts']}; ")
        + (f"mini-MAS {mi['correctly_anticipated']}/14, hidden pass {mi['hidden_pass_rate']:.0%}; " if mi else "") + f"{calls} LLM calls")


# ---------------------------------------------------------------- figures and card

def grid(ax, cols, title):
    """cols: list of (header, [cell text per mode], [colour per mode])."""
    n = len(MODES)
    ax.set_xlim(0, 3.8 + len(cols)); ax.set_ylim(n + 0.9, -1.2); ax.axis("off")
    for j, (h, _, _) in enumerate(cols):
        ax.text(3.8 + j + 0.45, -0.55, h, ha="center", va="center", fontsize=6.0, fontweight="bold")
    prev = None
    for i, (mid, name, dim, _) in enumerate(MODES):
        if dim != prev:
            ax.plot([0, 3.8 + len(cols)], [i - 0.02, i - 0.02], color=INK, lw=0.6)
            ax.text(0.02, i + 0.06, dim.upper(), fontsize=5.2, color=MUTED, va="top")
            prev = dim
        ax.text(0.02, i + 0.62, f"{mid} {name}", fontsize=6.6, va="center")
        for j, (_, txt, col) in enumerate(cols):
            ax.add_patch(plt.Rectangle((3.8 + j + 0.05, i + 0.3), 0.8, 0.62, color=col[i]))
            ax.text(3.8 + j + 0.45, i + 0.62, txt[i], ha="center", va="center", fontsize=6.4,
                    fontweight="bold" if "!" in txt[i] else "normal", color=ACC if "!" in txt[i] else INK)
    ax.set_title(title, fontsize=8.5, loc="left")


def figures(res, is_chatdev):
    st2 = res["stage2"]
    cols = []
    if is_chatdev:
        cols.append(("Authors\nStage 2", [PAPER[m][0] for m in MODE_IDS], [RISK_COL[PAPER[m][0]] for m in MODE_IDS]))
    cols.append(("LLM\nStage 2", [st2[m]["risk"] for m in MODE_IDS], [RISK_COL.get(st2[m]["risk"], "#e9ecef") for m in MODE_IDS]))
    if is_chatdev:
        cols.append(("Paper\nStage 3", [f"{PAPER[m][1]}/30" + (" (!)" if PAPER[m][2] else "") for m in MODE_IDS], ["#f1f3f5"] * 14))
        cols.append(("LLM vs\nStage 3", ["ok" if res["chatdev"]["llm_ok"][m] else "(!)" for m in MODE_IDS], ["#f8f9fa"] * 14))
    fig, ax = plt.subplots(figsize=(6.4, 4.9))
    grid(ax, cols, f"MASQ Stage 2 for {res['system']}" + (" (Table 2 layout; (!) = anticipated ≠ observed)" if is_chatdev else ""))
    fig.tight_layout(); fig.savefig(OUT / "fig_stage2_grid.png", dpi=160); plt.close(fig)

    if "mini" in res:
        mi = res["mini"]; n = mi["n_traces"]
        cols = [("Anticipated\n(Stage 2)", [mi["stage2"][m]["risk"] for m in MODE_IDS], [RISK_COL.get(mi["stage2"][m]["risk"], "#e9ecef") for m in MODE_IDS]),
                ("Observed\n(Stage 3)", [f"{round(mi['observed_rate'][m] * n)}/{n}" + (" (!)" if mi["mismatch"][m] else "") for m in MODE_IDS], ["#f1f3f5"] * 14)]
        for k, t in enumerate(res["traces"]):
            cols.append((f"T{k + 1}", ["●" if t["mast"][m] else "" for m in MODE_IDS], ["#ffd8a8" if t["mast"][m] else "#f8f9fa" for m in MODE_IDS]))
        fig, ax = plt.subplots(figsize=(6.4, 4.9))
        grid(ax, cols, f"Mini chat chain: anticipated vs observed over {n} traces ({mi['correctly_anticipated']}/14 match)")
        fig.tight_layout(); fig.savefig(OUT / "fig_stage3_mini.png", dpi=160); plt.close(fig)

        T = res["traces"]
        fig, ax = plt.subplots(figsize=(6.4, 2.6))
        x = np.arange(len(T))
        ax.bar(x, [t["hidden_pass"] / t["hidden_total"] for t in T], color=[ACC if t["declared_done_but_hidden_fail"] else GOOD for t in T], width=0.6)
        for i, t in enumerate(T):
            ax.text(i, t["hidden_pass"] / t["hidden_total"] + 0.03, f"{t['hidden_pass']}/{t['hidden_total']}\n"
                    + ("approved" if t["approved"] else "not approved") + ", " + ("tester ✓" if t["tester_pass"] else "tester ✗"),
                    ha="center", fontsize=6.5)
        ax.set_xticks(x); ax.set_xticklabels([t["function"] for t in T], fontsize=7.5, rotation=15)
        ax.set_ylim(0, 1.35); ax.set_ylabel("hidden tests passed")
        ax.set_title("Orange = the agents declared the work verified, hidden tests disagree", fontsize=8.5, loc="left")
        fig.tight_layout(); fig.savefig(OUT / "fig_traces.png", dpi=160); plt.close(fig)


def card(res, is_chatdev):
    st2 = res["stage2"]; rc = res["risk_counts"]
    tiles = []
    if is_chatdev:
        cd = res["chatdev"]
        tiles.append({"label": "LLM screen agrees with authors", "value": f"{cd['agree_with_authors']}/14",
                      "sub": f"exact Low/Mid/High match with the paper's Stage 2; {cd['within_one_level']}/14 within one level", "tone": "neutral"})
        tiles.append({"label": "Anticipated correctly (ChatDev)", "value": f"{cd['llm_screen_correct_vs_paper_traces']}/14",
                      "sub": f"LLM screen vs MAST's 30 annotated ChatDev traces; authors: 8/14. Verification (FM-3.2) rated {cd['verification_rating']} (authors Low, observed 11/30)",
                      "tone": "good" if cd["llm_screen_correct_vs_paper_traces"] >= 8 else "warn"})
    else:
        top = [f"{m}" for m in MODE_IDS if st2[m]["risk"] == "High"]
        tiles.append({"label": f"Risk profile: {res['system']}", "value": f"{rc['High']} High · {rc['Mid']} Mid · {rc['Low']} Low",
                      "sub": "High: " + (", ".join(top) if top else "none"), "tone": "warn" if rc["High"] else "neutral"})
    if "mini" in res:
        mi = res["mini"]
        tiles.append({"label": "Mini-MAS: anticipated = observed", "value": f"{mi['correctly_anticipated']}/14",
                      "sub": f"{mi['n_traces']} traces of a ChatDev-shaped chain ({mi['settings']['verification']} verification, history {mi['settings']['memory']})",
                      "tone": "neutral"})
        tiles.append({"label": "Declared done, hidden tests fail", "value": f"{mi['declared_done_but_hidden_fail']} of {mi['n_traces']}",
                      "sub": f"hidden-test pass rate {mi['hidden_pass_rate']:.0%}; reviewer approved {mi['approved_in_review']}/{mi['n_traces']}",
                      "tone": "accent" if mi["declared_done_but_hidden_fail"] else "good"})
    inputs = {"system": res["system"], "LLM": res["model"], "Stage 3": f"{res['mini']['n_traces']} mini-MAS traces" if "mini" in res else "off",
              "verification": VERIF if "mini" in res else "—", "memory between phases": MEMORY if "mini" in res else "—",
              "review rounds": ROUNDS, "LLM calls": res["llm_calls"]}
    compare = []
    if is_chatdev:
        cd = res["chatdev"]
        compare += [{"metric": "Correctly anticipated (ChatDev)", "paper": "Stage 2 correctly predicts 8/14 MAST risks", "yours": f"LLM screen: {cd['llm_screen_correct_vs_paper_traces']}/14", "note": "scored against the paper's own Stage 3 counts"},
                    {"metric": "No or incomplete verification (FM-3.2)", "paper": "Low; occurring in 11/30 traces", "yours": f"LLM: {st2['FM-3.2']['risk']}", "note": "the paper's main miss"},
                    {"metric": "Loss of conversation history (FM-1.4)", "paper": "High; 2/30 (!)", "yours": f"LLM: {st2['FM-1.4']['risk']}", "note": ""},
                    {"metric": "Conversation reset (FM-2.1)", "paper": "High; 1/30 (!)", "yours": f"LLM: {st2['FM-2.1']['risk']}", "note": ""},
                    {"metric": "Overestimated risks", "paper": "we overestimated five risk categories", "yours": f"LLM screen overestimated {sum(not cd['llm_ok'][m] and PAPER[m][1] <= 2 for m in MODE_IDS)}, underestimated {sum(not cd['llm_ok'][m] and PAPER[m][1] > 2 for m in MODE_IDS)}", "note": "(!) cells in the grid"}]
    if "mini" in res:
        mi = res["mini"]
        compare.append({"metric": "Role prompts vs mechanical verification", "paper": "role-prompting does not substitute for formal, mechanical verification",
                        "yours": f"{mi['declared_done_but_hidden_fail']}/{mi['n_traces']} mini-MAS traces declared done but failed hidden tests ({mi['settings']['verification']} verification)", "note": "runbook extension"})
    figs = [{"path": "fig_stage2_grid.png", "title": "Which failure modes does the design make plausible?",
             "caption": "MASQ Stage 2: each MAST failure mode, grouped by the Stage-1 dimension it is mapped to. The LLM classifies the design's protection "
                        "(explicit guardrail / prompt-only / architectural); code applies the paper's rule (Low / Mid / High)."
                        + (" Paper columns are the authors' Table 2; '(!)' marks anticipated ≠ observed." if is_chatdev else "")}]
    if "mini" in res:
        figs.append({"path": "fig_stage3_mini.png", "title": "Stage 3: did the anticipated failures show up in real traces?",
                     "caption": "A tiny ChatDev-shaped chat chain was screened (Stage 2) and then run on small coding tasks; an LLM annotated each trace (T1…) "
                                "against MAST. '(!)' uses a matching rule that reproduces the paper's flags: Low ≤ 2/30, Mid 2/30–8/30, High ≥ 8/30."})
        figs.append({"path": "fig_traces.png", "title": "When the agents say it's verified, is it?",
                     "caption": "Hidden unit tests (never shown to the agents) on each trace's final code, with whether the reviewer approved and the tester passed it."})
    Path(OUT / "card_data.json").write_text(json.dumps({
        "paper": {"num": 11, "title": "MASQ: The Multi-Agent System Questionnaire",
                  "authors": "Nils Kiele, Niki Mehri, Aaron Arellano, Samira Ebrahimi Kahou", "url": "https://drive.google.com/file/d/1Rp0p5g3H-GnNNV-2aCJPC3Ke3VbRcm0C/view?usp=sharing", "affiliation": "University of Calgary"},
        "inputs": inputs, "tiles": tiles[:4], "figures": figs, "compare": compare,
        "runbook": {"name": "smash-11-masq-questionnaire", "url": P.get("runbook_url", "")}}, indent=2, ensure_ascii=False))


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
