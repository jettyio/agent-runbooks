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
    skill_name: smash-22-spoiled-expertise
    confidence: high
---

# Damned If You Do: Map Your Own Spoiled Expertise (SMASH 2026 · Paper #22)

## Objective

This runbook is an interactive companion to the SMASH 2026 paper **"Damned if You Do(n't): How Epistemic Technology Spoils Expertise"** (Ayman Ajaj, Mayur Joshi, Mathieu Bouchard).
Read the paper: https://prefigurationlab.com/docs/SMASH_2026_Spolied_Expertise_CameraReady.pdf

The paper is **conceptual**. Building on Goffman's stigma, it argues that expertise can be *spoiled*, devalued through
stigma attached to a stance toward an epistemic technology rather than through lost competence. Crossing **stance of adoption**
(adopt / not adopt) with **locus of evaluation** (self / others) gives four forms: **Slopped** (adopt, self), **Lagging**
(not adopt, self), **Shunned** (adopt, others) and **Outdated** (not adopt, others). Experts are therefore "damned if they do, damned
if they don't". The paper also describes transitions between forms, stigma-management tactics, and governance implications.

This runbook is an **interpretive aid, not a measurement instrument**. It does two things:
1. **Your case.** You describe your profession, how you use (or refuse) AI, and the reactions you have met; presets are a
   radiologist and a lawyer. An LLM with the paper's definitions quoted verbatim as its codebook places the case in the 2×2 and quotes
   evidence from **your** text. Deterministic code checks every quote verbatim, checks that any transition labelled "paper" is one
   the paper actually describes, and relabels the rest as extrapolation. A second model gives an independent reading, each statement
   is coded separately by two judges, and the **mirror quadrant** shows the "damned if you don't" alternative.
2. **Discourse mapper.** Two independent LLM judges (Claude Haiku 4.5 and Claude Sonnet 4.6) code a corpus of comments on
   stance × locus × spoiled. The default corpus is 36 synthetic comments across five professions, 6 of them deliberately ambiguous;
   you can paste your own. Deterministic code computes **Cohen's κ** with a bootstrap CI, per-axis κ, the confusion matrix
   and the quadrant distribution. This tests whether the 2×2 can be coded reliably, a first step on the paper's proposed empirical agenda.

Output: a shareable **result card**. Target wall-clock: **under 5 minutes.** The experiment makes 12 LLM calls (about 50 s).

### The paper's framework (quote exactly)
- Table 1: Adoption/Self = **Slopped Expertise**; Non-Adoption/Self = **Lagging Expertise**; Adoption/Others = **Shunned
  Expertise**; Non-Adoption/Others = **Outdated Expertise**.
- Transitions (§4): "early adopters may initially experience internal doubt (slopped expertise) but later revalue their hybrid
  expertise, and shift toward shunned expertise if their environment exhibits antagonism toward epistemic technology";
  non-adopters in outdated expertise "may reluctantly adopt, coming to self-doubt their expertise's authenticity (slopped expertise)".
- Stigma management (§5): "techniques of information control"; "redefining what counts as real expertise by emphasizing tasks
  and relational capacities that machines cannot perform".
- Governance (§6): "mandates to document overrides may be read as bias or incompetence"; "incorporating expert reasoning into
  system design, and avoiding features that publicly tag experts as resistant".
- Boundary (§7): "Excel spreadsheets and statistical models are less likely to spoil expertise than a Generative AI system".
- The paper reports **no empirical data**: there are no numbers to reproduce, and the κ on this card is this runbook's own test.

## REQUIRED OUTPUT FILES (MANDATORY)

All in `{{results_dir}}`:

| File | Description |
|---|---|
| `result_card.html` | **Primary output.** Self-contained, shareable one-page result card |
| `results.json` | All codes, κ statistics, the case reading (written by `experiment.py`) |
| `card_data.json` | Numbers/figures for the card (written by `experiment.py`) |
| `narrative.json` | Your interpretation of this run (Step 4) |
| `fig_*.png` | Figures (written by `experiment.py`) |
| `summary.md` | 5–10 line plain-text summary |
| `validation_report.json` | Evals v2 report: steps, code checks, checklist (see Write Validation Report) |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Case preset | `{{case}}` | `radiologist` | `radiologist` (adopts an AI triage tool), `lawyer` (refuses generative AI), or `custom` (use the fields below) |
| Your profession | `{{profession}}` | — | **Bring your own**: e.g. `Clinical pharmacist`. Blank = the preset's |
| How you use AI | `{{ai_use}}` | — | **Bring your own**: what you use (or refuse) and how. Blank = the preset's |
| Reactions / quotes | `{{peer_reactions}}` | — | **Bring your own**: what colleagues, clients or patients said, or what you feel, separated by `\|\|`. Blank = the preset's |
| Corpus | `{{corpus}}` | — | Optional: paste 8–40 comments about AI use in a profession, separated by `\|\|`. Blank = the built-in synthetic 36-comment corpus |
| Judge B | `{{judge_b}}` | `large` | `large` (Claude Sonnet 4.6, a different model from judge A) or `small` (Haiku again, to test shared-model bias) |

## Dependencies

numpy and matplotlib (preinstalled in `python312-uv`). LLM calls go through the embedded `llm.py`, which uses whatever key the
sandbox provides. No downloads.

## Step 1: Set up

```bash
mkdir -p {{results_dir}} /app/work && cd /app/work
python -c "import numpy, matplotlib" 2>/dev/null || uv pip install --system -q numpy matplotlib
```

Write `/app/work/params.json`. Every value is a JSON string. If a value still looks like an unsubstituted `{{…}}`
placeholder, use the table default (blank for the free-text fields). **Escape** quotes, backslashes and newlines in the free text so
the file is valid JSON (check with `python -m json.tool params.json`). If the participant filled `profession`, `ai_use` or
`peer_reactions`, set `case` to `custom` unless they chose a preset explicitly.

```json
{"case": "{{case}}", "profession": "{{profession}}", "ai_use": "{{ai_use}}", "peer_reactions": "{{peer_reactions}}",
 "corpus": "{{corpus}}", "judge_b": "{{judge_b}}", "runbook_url": ""}
```

## Step 2: Get the code (extract it, don't retype it)

The tested implementation is embedded in the **Appendix** at the end of this runbook. Do not rewrite, "improve", or
re-derive it. In particular, **do not edit the codebook, the prompts or the default corpus**. **Always run the command below first, exactly as written.** It copies the files out of this runbook's text (which the sandbox exposes to running processes) in about a second, and it is far faster and more reliable than retyping several hundred lines. Do not skip it on the assumption that it won't work: run it and read its output:

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
python3 extract.py experiment.py render_card.py validate.py llm.py
```

If it exits non-zero or prints `MISSING`, write each missing file from the Appendix **exactly as given**, one
heredoc per file (quoted delimiter, e.g. `cat > experiment.py <<'PYEOF'`). If a later step fails, fix only
environment problems (missing package, network retry), never the methodology.

## Step 3: Run the experiment

```bash
cd /app/work && export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 SMASH_CPUS=4 && timeout 300 python -W ignore experiment.py params.json {{results_dir}}
```

Expected: 30–90 s. It ends with a `done:` line: your case's quadrant (and the second judge's), the mirror quadrant, verified
quotes, corpus κ with CI, per-axis κ, the most common form and the number of LLM calls.

The sandbox has 4 CPUs even though `nproc` may report more; the exports keep numpy/BLAS and process pools from oversubscribing them.

## Step 4: Interpret: write `narrative.json`

Read `{{results_dir}}/results.json` and `card_data.json`, and look at every `fig_*.png`. Write
`{{results_dir}}/narrative.json` with keys `headline`, `idea` (exactly 3), `findings` (2–4), `try_next` (2–3),
`caveats` (2–4):

- **headline** (≤ 30 words): the participant's quadrant (`case.quadrant`) and the mirror (`case.mirror_quadrant`), plus at most
  one number such as `corpus.kappa_quadrant` (2 decimals) or the corpus size. Phrase it as a reading ("reads as"), not a verdict.
- **idea**: the spoiled-expertise concept; the two axes and four forms; the damned-if-you-do/don't dilemma.
- **findings**: (1) the case reading with 1–2 of its **verified** evidence quotes (`case.llm_output.evidence` where
  `verified_verbatim` is true; never quote an unverified one as the person's words) and whether the second judge agreed;
  (2) the mirror quadrant, and the transitions and moves in `case.llm_output`, saying which are from the paper and which are extrapolations
  (`sources_relabelled`); (3) corpus reliability: κ with CI, stance/locus κ, clear vs ambiguous agreement, and where the judges disagree
  (`corpus.disagreements`); (4) for a participant corpus only, the distribution (`corpus.distribution`).
- **try_next**: 2–3 runs with exact values, using only the keys `case, profession, ai_use, peer_reactions, corpus, judge_b`.
  Good contrasts: the other preset; a custom case; `judge_b` `small`.
- **caveats**: an interpretive aid, not measurement or diagnosis; the default corpus is synthetic and written to fit the quadrants,
  so its distribution means nothing about the world; both judges are Claude models; extrapolated transitions and moves go beyond the paper.
  Add any `caveats_from_inputs`.

## Step 5: Render the card and summary

```bash
cd /app/work && python render_card.py {{results_dir}}/card_data.json {{results_dir}}/narrative.json {{results_dir}}/result_card.html
```

Write `{{results_dir}}/summary.md` (5–10 lines: the case, its quadrant and mirror, verified quotes, corpus κ, the headline).

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
python3 - "{{results_dir}}" "case,profession,ai_use,peer_reactions,corpus,judge_b" <<'PY'
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
cd /app/work && python3 validate.py {{results_dir}} case,profession,ai_use,peer_reactions,corpus,judge_b 240 checklist.json
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
"""Spoiled-expertise mapper — SMASH 2026 paper #22 (Ayman Ajaj, Mayur Joshi, Mathieu Bouchard).

The paper is conceptual: a 2x2 of spoiled expertise = adoption stance (adopt / not adopt an epistemic technology)
x locus of evaluation (self / others) -> Slopped, Lagging, Shunned, Outdated; plus transitions and stigma management.
This runbook makes the framework usable and puts it to a reliability test. It is an INTERPRETIVE AID, NOT MEASUREMENT.

  1. Your case: an LLM (codebook = the paper's definitions, quoted verbatim) places your profession / AI use / peer
     reactions in the 2x2, quoting evidence from YOUR text (quotes are verified deterministically), with a second
     judge for agreement, the mirror quadrant ("damned if you don't"), the paper's transitions and stigma-management /
     governance moves (paper-sourced vs. extrapolated are labelled).
  2. Discourse mapper: two independent LLM judges (different models) code a corpus of comments on stance x locus x
     spoiled; deterministic code computes Cohen's kappa (with bootstrap CI), per-axis kappa and the quadrant distribution.

usage: python experiment.py params.json outdir
"""
import json, re, sys, time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from llm import chat, chat_many, parse_json, backend, model_name, save_cache

T0 = time.time()
P = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
caveats = []


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def sval(k, d=""):
    v = str(P.get(k, d) if P.get(k) is not None else d).strip()
    return "" if v.startswith("{{") else v


# ---------------------------------------------------------------- the paper's codebook (quoted verbatim, §3-6)
DEF = {
    "Slopped": ("adoption, self", "This form captures experts who adopt epistemic technology and see their own expertise "
                "devalued by such adoption. Experts internalize the discourse that epistemic technologies are more objective, "
                "accurate, and efficient than humans and, therefore, reinterpret their own judgment and skills as insufficient "
                "or intrinsically flawed in comparison."),
    "Lagging": ("non-adoption, self", "This form captures experts who do not adopt epistemic technologies, but who internalize "
                "societal discourse that valorizes the capabilities and outputs of these technologies. They perceive their "
                "non-adoption stance as backward and lazy, even when their actual work performance continues to meet or exceed "
                "established organizational standards."),
    "Shunned": ("adoption, others", "This form captures experts who adopt epistemic technologies, and are stigmatized by others "
                "for doing so. This adoption is perceived by the expert's audience as signaling lesser expertise, and the expert "
                "as simply an operator or executor whose reliance on technology may indicate a troubling abdication of "
                "professional responsibility and weak moral judgment."),
    "Outdated": ("non-adoption, others", "This form illustrates experts who do not adopt epistemic technologies and are "
                 "stigmatized by others for this resistance. These non-adopters become symbols of obstruction to progress and "
                 "are considered outdated, unwilling to modernize their expertise in line with professional, organizational "
                 "and societal expectations about what experts should look like nowadays."),
}
QUAD = {("adopt", "self"): "Slopped", ("non-adopt", "self"): "Lagging", ("adopt", "others"): "Shunned", ("non-adopt", "others"): "Outdated"}
MIRROR = {"Slopped": "Lagging", "Lagging": "Slopped", "Shunned": "Outdated", "Outdated": "Shunned"}
CATS = ["Slopped", "Lagging", "Shunned", "Outdated", "Not spoiled / unclear"]
PAPER_TRANSITIONS = [
    {"from": "Slopped", "to": "Shunned", "quote": "early adopters may initially experience internal doubt (slopped expertise) but "
     "later revalue their hybrid expertise, and shift toward shunned expertise if their environment exhibits antagonism toward "
     "epistemic technology"},
    {"from": "Outdated", "to": "Slopped", "quote": "non-adopters may ignore the obsolescence framing raised by their peers "
     "(outdated expertise), but as narratives about redundancy gain force they may reluctantly adopt, coming to self-doubt "
     "their expertise's authenticity (slopped expertise)"},
]
PAPER_MOVES = [
    "“techniques of information control” (deciding when and how to disclose a devalued identity)",
    "redefining what counts as real expertise by emphasizing tasks and relational capacities that machines cannot perform",
    "incorporating expert reasoning into system design",
    "avoiding features that publicly tag experts as resistant",
    "(caution) mandates to document overrides may be read as bias or incompetence, discouraging the human oversight that "
    "responsible deployment requires",
]
BOUNDARY = ("Most applicable where epistemic technologies are capable of generating and advancing knowledge claims, rather than "
            "merely supporting expert judgment: Excel spreadsheets and statistical models are less likely to spoil expertise "
            "than a Generative AI system.")
CODEBOOK = "\n".join(f"- {k} expertise ({v[0]}): {v[1]}" for k, v in DEF.items())

# ---------------------------------------------------------------- inputs
PRESETS = {
    "radiologist": {
        "profession": "Radiologist at a community hospital",
        "ai_use": "For two years I've read chest CTs with an AI triage tool that pre-flags possible nodules and pulmonary "
                  "emboli. I review every flag and overrule it roughly once a week.",
        "peer_reactions": "At a case conference a senior colleague said: 'If the software reads it first, what exactly are we "
                          "paying you for?' || A patient asked whether a real doctor had looked at her scan or just the computer. "
                          "|| Our department dashboard lists each radiologist's AI override rate, and mine is the highest; the "
                          "chief asked me to justify it. || Some nights I wonder whether I'd still catch the small nodules "
                          "without the overlay."},
    "lawyer": {
        "profession": "Senior associate at a mid-size litigation firm",
        "ai_use": "I don't use generative AI for research or drafting. I do my own case-law research and write every brief myself.",
        "peer_reactions": "A partner told the team that associates who refuse the tools won't make partner. || A client asked "
                          "why our research bills are three times what a competitor quoted with AI. || The junior associates "
                          "call my process artisanal. || I'm starting to feel slow and stubborn, even though my win rate is fine."},
}
case_name = sval("case", "radiologist").lower() or "radiologist"
if case_name not in PRESETS and case_name != "custom":
    caveats.append(f"case '{case_name}' unknown; used radiologist"); case_name = "radiologist"
base = PRESETS.get(case_name, PRESETS["radiologist"])
PROF = sval("profession") or base["profession"]
USE = sval("ai_use") or base["ai_use"]
REACT = sval("peer_reactions") or base["peer_reactions"]
custom_fields = [k for k in ("profession", "ai_use", "peer_reactions") if sval(k)]
if case_name == "custom" and not custom_fields:
    caveats.append("case 'custom' but no text supplied; used the radiologist preset")
STATEMENTS = [s.strip() for s in re.split(r"\|\||\n", REACT) if s.strip()][:10]
CASE_TEXT = f"PROFESSION: {PROF}\nHOW I USE (OR DON'T USE) AI: {USE}\nREACTIONS / EXPERIENCES:\n" + "\n".join(f"- {s}" for s in STATEMENTS)
JUDGE_B = "large" if sval("judge_b", "large").lower() != "small" else "small"

DEFAULT_CORPUS = [  # SYNTHETIC comments written for this runbook (profession, text, author-intended quadrant)
    ("medicine", "Since we got the nodule-detection tool I second-guess every read where I disagree with it. Maybe my eye was never as good as I thought.", "Slopped"),
    ("medicine", "The attending joked at handover that I'm just the AI's proofreader now because I keep the triage overlay on.", "Shunned"),
    ("medicine", "Our chair keeps asking why I'm still reading chest films without the algorithm, like I'm the department dinosaur.", "Outdated"),
    ("medicine", "I don't use the AI scribe, and honestly I feel like I'm falling behind, even though my notes are fine and nobody has complained.", "Lagging"),
    ("medicine", "Patients ask whether a computer read their scan, and when I say yes some of them ask for a second opinion from a real doctor.", "Shunned"),
    ("medicine", "I turned on the sepsis decision support last month; it's useful and I still make the call. No drama.", "Not spoiled / unclear"),
    ("law", "Partners here let it be known that anyone who drafts with a chatbot is not a real lawyer, so I keep it out of sight.", "Shunned"),
    ("law", "Opposing counsel sneered that our brief read like a bot wrote it. It was me plus the research tool, and the clerk heard every word.", "Shunned"),
    ("law", "I've refused to use AI for contract review and the younger associates openly call my methods artisanal, and not as a compliment.", "Outdated"),
    ("law", "After a year on the review platform I can't tell anymore whether I actually know the case law or just know how to prompt.", "Slopped"),
    ("law", "Clients ask why my bill is so high when AI can do discovery. I don't use it, and I'm starting to think they're right about me.", "Lagging"),
    ("law", "The tool does first-pass review; I tell the juniors that part is clerical anyway and the real lawyering starts after.", "Not spoiled / unclear"),
    ("accounting", "The audit committee asked us to stop advertising our ML anomaly detection; they worry clients will think we don't do real audits.", "Shunned"),
    ("accounting", "I still tick and tie by hand. The managers have started routing the interesting engagements to the AI-fluent team.", "Outdated"),
    ("accounting", "Using the forecasting model every day has made me feel like my own judgment is a rounding error.", "Slopped"),
    ("accounting", "I haven't touched the new analytics suite and I feel lazy about it, even though my reviews pass QA every time.", "Lagging"),
    ("accounting", "We use the reconciliation bot for bank recs. It saves time. Nobody really talks about it.", "Not spoiled / unclear"),
    ("accounting", "My manager praised me in front of the team for catching an error the AI missed.", "Not spoiled / unclear"),
    ("journalism", "Readers in the comments accused me of AI slop because I disclosed that I used a transcription assistant.", "Shunned"),
    ("journalism", "Editors keep holding up the AI-assisted desk as the model and asking why my pieces take three days.", "Outdated"),
    ("journalism", "I use the summarizer for wire copy and lately I wonder if I'd even recognize a good lede without it.", "Slopped"),
    ("journalism", "I've avoided all the AI tools, and when I see colleagues filing faster I feel like a relic, even though my editor likes my work.", "Lagging"),
    ("journalism", "I disclose AI use in a footnote now and haven't had a single reader complaint.", "Not spoiled / unclear"),
    ("journalism", "A source refused to talk once she heard our newsroom uses AI drafting: she said she wasn't giving quotes to a machine.", "Shunned"),
    ("teaching", "The principal introduced me at the staff meeting as our last holdout on the AI lesson planner.", "Outdated"),
    ("teaching", "Parents emailed asking whether a chatbot wrote the feedback on their kids' essays; I had only used it to fix grammar.", "Shunned"),
    ("teaching", "Since using the lesson generator my own lesson plans feel thin and amateurish to me.", "Slopped"),
    ("teaching", "I don't use AI for grading and I quietly worry I'm the lazy one for refusing to learn it, even with good evaluations.", "Lagging"),
    ("teaching", "Colleagues at the conference treated my refusal to use AI tutors as old-fashioned stubbornness.", "Outdated"),
    ("teaching", "I tried the quiz generator, kept what worked, dropped the rest. It's a tool.", "Not spoiled / unclear"),
    # deliberately ambiguous / mixed comments (no single intended label)
    ("medicine", "I use the AI for first-draft reports and my team loves the turnaround, but privately I feel like a fraud.", None),
    ("law", "Management mandated the drafting assistant; I open it when the partners are watching and ignore it otherwise.", None),
    ("journalism", "My desk mocked me for using AI transcription, and now half of them use it too.", None),
    ("medicine", "I stopped using the diagnostic AI after a colleague's remark, and now the residents call me old school.", None),
    ("teaching", "Is it cheating if the AI writes my lesson objectives? I genuinely don't know anymore.", None),
    ("accounting", "Everyone says the models will replace us. I haven't decided whether to use them, and it eats at me.", None),
]
corpus_raw = sval("corpus")
if corpus_raw:
    items = [c.strip() for c in re.split(r"\|\||\n", corpus_raw) if len(c.strip()) > 10][:40]
    CORPUS = [("your corpus", c, None) for c in items]
    if len(items) < 8:
        caveats.append(f"only {len(items)} corpus comments supplied; kappa is very uncertain")
    CORPUS_KIND = "participant-supplied"
else:
    CORPUS = DEFAULT_CORPUS; CORPUS_KIND = "default (synthetic, written for this runbook)"
log(f"case '{case_name}' ({PROF}); {len(STATEMENTS)} statements; corpus {CORPUS_KIND}: {len(CORPUS)} comments")

# ---------------------------------------------------------------- LLM coding
SYS_CODER = ("You are a careful qualitative coder applying a published codebook (Ajaj, Joshi & Bouchard, 'Damned if You Do(n't)'). "
             "Code only what the text says; do not infer beyond it. Use 'unclear' or 'none' when the text does not say.")
CODER_TASK = f"""CODEBOOK: four forms of spoiled expertise (stance of adoption x locus of evaluation)
{CODEBOOK}
Expertise is 'spoiled' when its perceived authority or worth is devalued through stigma attached to a technological stance,
not through a loss of competence. Neutral or positive experiences are NOT spoiled.

For EACH numbered comment return:
 "stance": "adopt" | "non-adopt" | "unclear"   (the expert's own stance toward the AI / epistemic technology)
 "locus":  "self" | "others" | "none"         (who devalues the expertise: the expert themself, or an audience; 'none' if nobody)
 "spoiled": true | false
 "cue": a short VERBATIM fragment of the comment that drives the code
Return ONLY a JSON list: [{{"id": <number>, "stance": ..., "locus": ..., "spoiled": ..., "cue": ...}}, ...]

COMMENTS:
"""


def code_batch(texts, size, offset=0):
    prompts = []
    for k in range(0, len(texts), 10):
        chunk = texts[k:k + 10]
        prompts.append(CODER_TASK + "\n".join(f"{offset + k + i + 1}. {t}" for i, t in enumerate(chunk)))
    return prompts


def to_cat(c):
    if not isinstance(c, dict) or not c.get("spoiled") or str(c.get("spoiled")).lower() == "false":
        return "Not spoiled / unclear"
    return QUAD.get((str(c.get("stance", "")).lower(), str(c.get("locus", "")).lower()), "Not spoiled / unclear")


def parse_codes(replies, n):
    out = {}
    for r in replies:
        try:
            for c in parse_json(r):
                if isinstance(c, dict) and "id" in c:
                    out[int(c["id"])] = c
        except (ValueError, TypeError):
            continue
    return [out.get(i + 1, {}) for i in range(n)]


texts = [c[1] for c in CORPUS]
pA = code_batch(texts, "small"); pS = code_batch(STATEMENTS, "small")
CASE_PROMPT = f"""CODEBOOK (quoted from the paper):
{CODEBOOK}
Boundary condition (paper): {BOUNDARY}
Transitions described in the paper:
{chr(10).join(f"- {t['from']} -> {t['to']}: {t['quote']}" for t in PAPER_TRANSITIONS)}
Stigma-management and governance moves named in the paper:
{chr(10).join(f"- {m}" for m in PAPER_MOVES)}

A knowledge worker describes their situation:
{CASE_TEXT}

Return ONLY JSON:
{{"quadrant": "Slopped|Lagging|Shunned|Outdated|Not spoiled",
  "stance": "adopt|non-adopt|mixed", "locus": "self|others|both|none",
  "secondary": ["other quadrant(s) also present, if any"],
  "evidence": [{{"quote": "<VERBATIM fragment of the description>", "axis": "stance|locus|spoiling", "why": "<one sentence>"}}],
  "boundary_condition": {{"generates_knowledge_claims": true|false, "why": "<one sentence>"}},
  "transitions": [{{"to": "<quadrant>", "trigger": "<what would move them>", "source": "paper|extrapolation"}}],
  "moves": [{{"move": "<a concrete stigma-management or governance move for THIS case>", "source": "paper|extrapolation"}}],
  "confidence": "low|medium|high"}}
Use 3-5 evidence quotes, 1-3 transitions, 3-5 moves. Mark anything not stated in the paper as "extrapolation"."""
log(f"LLM backend {backend()}: judge A {model_name('small')}, judge B {model_name(JUDGE_B)}")
rA = chat_many(pA + pS, SYS_CODER, size="small", max_tokens=1600)
rB = chat_many(pA + pS, SYS_CODER, size=JUDGE_B, max_tokens=1600)
case_rep = chat_many([CASE_PROMPT], "You apply the paper's framework faithfully and quote only what the person wrote.",
                     size="large", max_tokens=1800)[0]
case_small = chat_many([CASE_PROMPT], "You apply the paper's framework faithfully and quote only what the person wrote.",
                       size="small", max_tokens=1800)[0]
save_cache()
nA = len(pA)
codesA, codesB = parse_codes(rA[:nA], len(texts)), parse_codes(rB[:nA], len(texts))
stA, stB = parse_codes(rA[nA:], len(STATEMENTS)), parse_codes(rB[nA:], len(STATEMENTS))
catA, catB = [to_cat(c) for c in codesA], [to_cat(c) for c in codesB]
scatA, scatB = [to_cat(c) for c in stA], [to_cat(c) for c in stB]
n_llm = 2 * (len(pA) + len(pS)) + 2
log(f"coded {len(texts)} comments + {len(STATEMENTS)} statements with two judges ({n_llm} LLM calls)")


# ---------------------------------------------------------------- deterministic analysis
def kappa(a, b, cats):
    a, b = np.asarray(a), np.asarray(b); n = len(a)
    if n == 0:
        return float("nan")
    po = float((a == b).mean())
    pe = sum(float((a == c).mean()) * float((b == c).mean()) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def boot_ci(a, b, cats, n=2000, seed=0):
    r = np.random.default_rng(seed); a, b = np.asarray(a), np.asarray(b); ks = []
    for _ in range(n):
        i = r.integers(0, len(a), len(a)); k = kappa(a[i], b[i], cats)
        if np.isfinite(k):
            ks.append(k)
    return [float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))]


k_quad = kappa(catA, catB, CATS); k_ci = boot_ci(catA, catB, CATS)
sA = [str(c.get("stance", "unclear")).lower() for c in codesA]; sB = [str(c.get("stance", "unclear")).lower() for c in codesB]
lA = [str(c.get("locus", "none")).lower() for c in codesA]; lB = [str(c.get("locus", "none")).lower() for c in codesB]
k_stance = kappa(sA, sB, ["adopt", "non-adopt", "unclear"]); k_locus = kappa(lA, lB, ["self", "others", "none"])
agree = float(np.mean(np.array(catA) == np.array(catB)))
consensus = [a if a == b else None for a, b in zip(catA, catB)]
dist = {c: {"judge_a": catA.count(c), "judge_b": catB.count(c), "consensus": consensus.count(c)} for c in CATS}
conf = np.array([[sum(1 for a, b in zip(catA, catB) if a == ra and b == cb) for cb in CATS] for ra in CATS])
author = [c[2] for c in CORPUS]
has_author = any(au is not None for au in author)
ia = [i for i, au in enumerate(author) if au is not None]
k_author_a = kappa([catA[i] for i in ia], [author[i] for i in ia], CATS) if has_author else None
k_author_b = kappa([catB[i] for i in ia], [author[i] for i in ia], CATS) if has_author else None
amb = [i for i, au in enumerate(author) if au is None] if has_author else []
agree_clear = float(np.mean([catA[i] == catB[i] for i in ia])) if has_author else None
agree_amb = float(np.mean([catA[i] == catB[i] for i in amb])) if amb else None
disagreements = [{"text": t, "judge_a": a, "judge_b": b, **({"author_intent": au} if au else {})}
                 for t, a, b, au in zip(texts, catA, catB, author) if a != b]
by_prof = {}
for (prof, _, _), c in zip(CORPUS, consensus):
    by_prof.setdefault(prof, {k: 0 for k in CATS + ["judges disagree"]})
    by_prof[prof][c or "judges disagree"] += 1

# your case
try:
    case = parse_json(case_rep)
except ValueError:
    case = {"quadrant": "unparsed", "evidence": []}
try:
    case2 = parse_json(case_small)
except ValueError:
    case2 = {"quadrant": "unparsed"}


def normq(s):
    s = str(s).lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[\s\"']+", " ", s).strip(" .,;:")


SRC_NORM = normq(CASE_TEXT)
ev = case.get("evidence") or []
for e in ev:
    e["verified_verbatim"] = bool(normq(e.get("quote", ""))) and normq(e.get("quote", "")) in SRC_NORM
n_ver = sum(e["verified_verbatim"] for e in ev)
# deterministic source check: a transition may only claim "paper" if the paper describes that exact move
PAIRS = {(t["from"], t["to"]) for t in PAPER_TRANSITIONS}
qn0 = str(case.get("quadrant", "")).split()[0].capitalize() if case.get("quadrant") else ""
case["transitions"] = [t for t in (case.get("transitions") or []) if isinstance(t, dict)
                       and str(t.get("to", "")).split()[0].capitalize() != qn0]
relabelled = 0
for t in case["transitions"]:
    if str(t.get("source")) == "paper" and (qn0, str(t.get("to", "")).split()[0].capitalize()) not in PAIRS:
        t["source"] = "extrapolation (relabelled: not a transition the paper describes)"; relabelled += 1
KEYS = ["information control", "disclos", "redefin", "machines cannot", "system design", "expert reasoning", "tag", "override"]
for m in case.get("moves") or []:
    if isinstance(m, dict) and str(m.get("source")) == "paper" and not any(k in str(m.get("move", "")).lower() for k in KEYS):
        m["source"] = "extrapolation (relabelled: no matching move in the paper)"; relabelled += 1
quad = str(case.get("quadrant", "unparsed")).split()[0].capitalize() if case.get("quadrant") else "unparsed"
quad = quad if quad in DEF else ("Not spoiled" if "not" in str(case.get("quadrant", "")).lower() else quad)
quad2 = str(case2.get("quadrant", "unparsed")).split()[0].capitalize()
mirror = MIRROR.get(quad)
paper_tr = [t for t in PAPER_TRANSITIONS if t["from"] == quad]
stmt_votes = {c: scatA.count(c) + scatB.count(c) for c in CATS}
log(f"your case: {quad} (second judge: {quad2}); {n_ver}/{len(ev)} quotes verified; corpus kappa {k_quad:.2f} "
    f"[{k_ci[0]:.2f}, {k_ci[1]:.2f}]")

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False})
INK, ACC, BLUE, MUTED = "#1f2a44", "#d9480f", "#1971c2", "#868e96"
POS = {"Slopped": (0, 1), "Lagging": (1, 1), "Shunned": (0, 0), "Outdated": (1, 0)}

fig, ax = plt.subplots(figsize=(6.4, 4.2))
for qn, (x, y) in POS.items():
    hl = qn == quad
    ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor="#fff4e6" if hl else "#f8f9fa", edgecolor=ACC if hl else "#ced4da",
                               lw=2.2 if hl else 1))
    ax.text(x + 0.05, y + 0.9, f"{qn} expertise", fontsize=10.5, fontweight="bold", color=ACC if hl else INK, va="top")
    ax.text(x + 0.05, y + 0.78, DEF[qn][0], fontsize=8, color=MUTED, va="top")
r = np.random.default_rng(3)
for cats_, mk, col, lab in [(scatA, "o", BLUE, f"your statements · judge A"), (scatB, "s", INK, f"your statements · judge B")]:
    for c in cats_:
        if c in POS:
            x, y = POS[c]
            ax.scatter(x + 0.2 + 0.6 * r.random(), y + 0.15 + 0.45 * r.random(), marker=mk, s=40, color=col, alpha=0.8,
                       edgecolor="white", lw=0.5)
    ax.scatter([], [], marker=mk, color=col, label=lab)
if quad in POS:
    x, y = POS[quad]; ax.scatter(x + 0.85, y + 0.85, marker="*", s=260, color=ACC, zorder=5, label=f"your case: {quad}")
if mirror in POS:
    x, y = POS[mirror]; ax.annotate("", xy=(x + 0.5, y + 0.5), xytext=(POS[quad][0] + 0.5, POS[quad][1] + 0.5),
                                    arrowprops=dict(arrowstyle="->", color=MUTED, ls="--", lw=1.2))
    ax.text(x + 0.5, y + 0.42, "if you had made the\nopposite choice", fontsize=7.5, color=MUTED, ha="center", va="top")
ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["Adoption", "Non-adoption"])
ax.set_yticks([0.5, 1.5]); ax.set_yticklabels(["Others", "Self"]); ax.set_ylabel("Locus of evaluation")
ax.set_xlabel("Stance of adoption"); ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
fig.tight_layout(); fig.savefig(OUT / "fig_quadrant.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.9))
x = np.arange(len(CATS)); w = 0.27
ax.bar(x - w, [dist[c]["judge_a"] for c in CATS], w, color=BLUE, label=f"judge A ({model_name('small').split('/')[-1]})")
ax.bar(x, [dist[c]["judge_b"] for c in CATS], w, color=INK, label=f"judge B ({model_name(JUDGE_B).split('/')[-1]})")
if has_author:
    ax.bar(x + w, [author.count(c) for c in CATS], w, color="white", edgecolor=MUTED, hatch="///",
           label=f"author's intended label ({len(amb)} ambiguous items have none)")
ax.set_xticks(x); ax.set_xticklabels([c.replace(" / ", "/\n") for c in CATS], fontsize=8.5)
ax.set_ylabel("comments"); ax.set_ylim(0, max(max(v.values()) for v in dist.values()) * 1.55)
ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
ax.set_title(f"Cohen's κ (A vs B) = {k_quad:.2f}  [95% CI {k_ci[0]:.2f}, {k_ci[1]:.2f}],  n = {len(texts)}", fontsize=9, loc="left")
fig.tight_layout(); fig.savefig(OUT / "fig_corpus.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.imshow(conf, cmap="Blues")
short = ["Slopped", "Lagging", "Shunned", "Outdated", "Not spoiled"]
ax.set_xticks(range(5)); ax.set_xticklabels(short, fontsize=8, rotation=25, ha="right"); ax.set_yticks(range(5)); ax.set_yticklabels(short, fontsize=8.5)
for i in range(5):
    for j in range(5):
        if conf[i, j]:
            ax.text(j, i, int(conf[i, j]), ha="center", va="center", fontsize=10, color="white" if conf[i, j] > conf.max() / 2 else INK)
ax.set_ylabel("judge A"); ax.set_xlabel("judge B")
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "fig_confusion.png", dpi=160); plt.close(fig)

# ---------------------------------------------------------------- results + card
res = {"params": P, "caveats_from_inputs": caveats, "backend": backend(), "judge_a": model_name("small"),
       "judge_b": model_name(JUDGE_B), "case_model": model_name("large"), "llm_calls": n_llm,
       "case": {"preset": case_name, "custom_fields": custom_fields, "profession": PROF, "ai_use": USE, "statements": STATEMENTS,
                "quadrant": quad, "second_opinion_quadrant": quad2, "judges_agree": quad == quad2, "mirror_quadrant": mirror,
                "llm_output": case, "quotes_verified": n_ver, "quotes_total": len(ev), "sources_relabelled": relabelled,
                "paper_transitions_from_here": paper_tr, "statement_codes": {"judge_a": scatA, "judge_b": scatB},
                "statement_votes": stmt_votes},
       "corpus": {"kind": CORPUS_KIND, "n": len(texts), "kappa_quadrant": k_quad, "kappa_ci95": k_ci,
                  "kappa_stance": k_stance, "kappa_locus": k_locus, "raw_agreement": agree, "distribution": dist,
                  "confusion_rows_judge_a_cols_judge_b": conf.tolist(), "categories": CATS,
                  "kappa_judge_a_vs_author": k_author_a, "kappa_judge_b_vs_author": k_author_b,
                  "n_ambiguous": len(amb), "agreement_clear_items": agree_clear, "agreement_ambiguous_items": agree_amb,
                  "by_profession_consensus": by_prof, "disagreements": disagreements[:12],
                  "unparsed_a": sum(1 for c in codesA if not c), "unparsed_b": sum(1 for c in codesB if not c)},
       "paper_moves": PAPER_MOVES, "boundary_condition": BOUNDARY}
top = max(CATS[:4], key=lambda c: dist[c]["consensus"])
tiles = [
    {"label": "Your case", "value": f"{quad}" + (" expertise" if quad in DEF else ""),
     "sub": f"{PROF}; {DEF[quad][0] if quad in DEF else ''} · second judge: {quad2} "
            f"({'agree' if quad == quad2 else 'disagree'}) · {n_ver}/{len(ev)} quotes verified verbatim", "tone": "accent"},
    {"label": "Damned if you don't", "value": mirror or "—",
     "sub": "the quadrant the same audience points to had you made the opposite adoption choice", "tone": "warn"},
    {"label": "Two-judge agreement (κ)", "value": f"{k_quad:.2f}",
     "sub": f"95% CI [{k_ci[0]:.2f}, {k_ci[1]:.2f}] on {len(texts)} comments · stance κ {k_stance:.2f}, locus κ {k_locus:.2f}",
     "tone": "good" if k_quad >= 0.6 else "neutral"},
    {"label": "Most common form (both judges agree)", "value": top,
     "sub": f"{dist[top]['consensus']} of {len(texts)} comments · {CORPUS_KIND.split(' (')[0]} corpus", "tone": "neutral"},
]
compare = [{"metric": f"{k} expertise ({v[0]})", "paper": v[1][:150] + "…",
            "yours": f"A {dist[k]['judge_a']} · B {dist[k]['judge_b']} · agreed {dist[k]['consensus']}", "note": "corpus counts"}
           for k, v in DEF.items()]
compare += [{"metric": "Transitions", "paper": "Slopped → Shunned; Outdated → Slopped (§4)",
             "yours": "; ".join(f"{quad} → {t.get('to')} ({t.get('source')})" for t in (case.get("transitions") or [])[:3]) or "—",
             "note": "'extrapolation' = not in the paper"},
            {"metric": "Empirical measurement", "paper": "none (conceptual paper; proposes an empirical research agenda)",
             "yours": f"κ = {k_quad:.2f} between two LLM coders", "note": "codability, not prevalence"}]
if has_author and amb:
    compare.append({"metric": "Agreement: clear-cut vs deliberately ambiguous comments", "paper": "—",
                    "yours": f"{100 * agree_clear:.0f}% vs {100 * agree_amb:.0f}%", "note": f"{len(ia)} vs {len(amb)} comments"})
if k_author_a is not None:
    compare.append({"metric": "Judges vs the corpus author's intended labels", "paper": "—",
                    "yours": f"κ A {k_author_a:.2f} · B {k_author_b:.2f}", "note": "synthetic corpus"})
Path(OUT / "card_data.json").write_text(json.dumps({
    "paper": {"num": 22, "title": "Damned if You Do(n't): How Epistemic Technology Spoils Expertise",
              "authors": "Ayman Ajaj, Mayur Joshi, Mathieu Bouchard", "url": "https://prefigurationlab.com/docs/SMASH_2026_Spolied_Expertise_CameraReady.pdf", "affiliation": "University of Ottawa"},
    "inputs": {"case": case_name if not custom_fields else "custom", "profession": PROF[:60],
               "statements": len(STATEMENTS), "corpus": f"{len(texts)} comments ({CORPUS_KIND.split(' (')[0]})",
               "judge A": model_name("small").split("/")[-1], "judge B": model_name(JUDGE_B).split("/")[-1]},
    "tiles": tiles,
    "figures": [{"path": "fig_quadrant.png", "title": "Where does your situation sit in the 2×2?",
                 "caption": "★ = the overall reading of your case. Dots = each of your statements coded separately by the two judges. "
                            "The dashed arrow points to the mirror quadrant: the 'damned if you don't' alternative."},
                {"path": "fig_corpus.png", "title": "Can the 2×2 be coded reliably?",
                 "caption": "Two LLM judges (different models, same codebook: the paper's definitions) coded every comment independently. "
                            "Counts reflect the corpus as written, not how common each form is in the world."},
                {"path": "fig_confusion.png", "title": "Where do the judges disagree?",
                 "caption": "Rows = judge A, columns = judge B. Off-diagonal cells are the ambiguous cases worth reading."}],
    "compare": compare, "runbook": {"name": "smash-22-spoiled-expertise", "url": P.get("runbook_url", "")}}, indent=2))
res["runtime_sec"] = round(time.time() - T0, 1)
(OUT / "results.json").write_text(json.dumps(res, indent=2))
log(f"done: your case {quad} (2nd judge {quad2}), mirror {mirror}; quotes {n_ver}/{len(ev)}; corpus kappa {k_quad:.2f} "
    f"[{k_ci[0]:.2f}, {k_ci[1]:.2f}], stance {k_stance:.2f}, locus {k_locus:.2f}; most common {top}; {n_llm} LLM calls")
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
