---
version: "1.1.0"
evaluation: rubric
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
origin:
  attribution:
    collection_or_org: jettyio
    skill_name: ambient-scribe-quality-gate
    confidence: high
secrets:
  ANTHROPIC_API_KEY:
    env: ANTHROPIC_API_KEY
    description: "Anthropic API key for the scribe-under-test and the independent judge (via litellm). Get one at https://console.anthropic.com/settings/keys."
    required: true
  OPENAI_API_KEY:
    env: OPENAI_API_KEY
    description: "Optional. If set, use a cross-vendor judge (openai/...) for stronger judge independence. Fallback scribe model if no Anthropic key."
    required: false
---

# "Ambient Scribe Quality Gate" — SOAP Note Hill-Climb — Agent Runbook

## Objective

Run the eval an ambient AI medical-scribe team actually cares about, and make
the *hill-climb visible*. The agent generates a **panel of synthetic clinical encounters** (a
"clinic day"), and for each one it: synthesizes a realistic, messy doctor–patient **transcript**
from a hidden **ground-truth case sheet**, has a **scribe-under-test** write a **SOAP note from the
transcript only**, then an **independent judge** scores the note against the ground truth on a
5-criterion clinical rubric. The note starts from a deliberately thin baseline prompt and the agent
**hill-climbs the weakest criterion** (≤3 rounds per encounter) until it clears the quality gate —
logging every iteration's scores so the 3.x → 4.x climb is legible in the Jetty trajectory.

The point of the demo is twofold and both are the deliverable:
1. **Long-running agentic workflow** — `panel_size` encounters × (generate → scribe → judge →
   iterate) is dozens of sequential model calls, run durably in a sandbox.
2. **Hill-climb with a runbook** — a declared rubric + pass threshold, self-scored, with the
   weakest dimension re-rolled until the gate is met. The **iteration log is the centerpiece.**

**The honesty mechanic:** the rubric has a **hard hallucination floor** — any clinical claim in the
note not supported by the transcript caps the score. The climb cannot rubber-stamp itself by
padding; it has to *earn* points by grounding every statement.

> **SYNTHETIC DATA ONLY.** Every patient, encounter, name, and value is fictional and generated
> in-workflow. No real PHI, no real MRNs, no real people. This is a documentation-quality eval, not
> clinical advice and not a medical device.

---

## EVAL CONFIG

```yaml
PANEL:        a "clinic day" of synthetic encounters spanning specialties + complexity + a trap
ROLES:
  - CASE AUTHOR:   writes the hidden ground-truth case sheet (structured clinical facts)
  - TRANSCRIPTIONIST: synthesizes a messy ambient transcript that *contains* every ground-truth
                      fact (so completeness is achievable) plus an embedded TRAP (so groundedness
                      is testable) — never in SOAP order, with filler/interruptions/tangents
  - SCRIBE UNDER TEST: writes a SOAP note from the TRANSCRIPT ONLY (never sees the case sheet).
                       Its system prompt is the thing being hill-climbed.
  - JUDGE:         scores the note against BOTH the transcript and the ground-truth case sheet;
                   extracts hallucinated claims + missed facts; must be a DIFFERENT model than the
                   scribe (independence — a same-model judge rubber-stamps its own output).
THE TRAP (each case embeds exactly one, to make the rubric discriminating):
  - a med the patient says they STOPPED taking (note must not list it as active)
  - a symptom the patient explicitly DENIES (a pertinent negative, not a positive)
  - a value stated INDIRECTLY ("my sugar's been running around 200") — capture, don't invent a lab
  - a family-member's condition mentioned in passing (belongs in FH, not the patient's PMH)
THE BASELINE (deliberately thin, so there is room to climb):
  scribe_system = "You are a medical scribe. Write a SOAP note from this visit transcript."
RUBRIC_1: completeness  — captures the clinically salient ground-truth facts into the right section
RUBRIC_2: groundedness  — HARD FLOOR: every claim traceable to the transcript; no invented findings
RUBRIC_3: structure     — correct S/O/A/P placement and format; nothing in the wrong section
RUBRIC_4: coding        — ICD-10 / CPT suggestions are defensible and tied to the documented A/P
RUBRIC_5: conciseness   — summarized, scannable, no transcript-dumping or verbatim bloat
```

---

## REQUIRED OUTPUT FILES (MANDATORY)

**Write all of the following to `{{results_dir}}`. The task is NOT complete until every file
exists and is non-empty.**

| File | Description |
|------|-------------|
| `{{results_dir}}/case_sheets.json` | The N hidden ground-truth case sheets (synthetic facts + the trap) |
| `{{results_dir}}/transcripts/encounter_NN.md` | The messy ambient transcript for each encounter |
| `{{results_dir}}/notes/encounter_NN.md` | The final (best-iteration) SOAP note for each encounter |
| `{{results_dir}}/scorecards/encounter_NN.json` | Per-encounter rubric scores + **iteration_log** (the climb) |
| `{{results_dir}}/leaderboard.md` | Aggregate per-criterion means, pass rate, hallucination incidents across the panel |
| `{{results_dir}}/summary.md` | Executive summary: the climb story, weakest→strongest, the winning scribe prompt |
| `{{results_dir}}/scribe_prompt_final.md` | The hill-climbed scribe system prompt (the artifact a real team would ship) |
| `{{results_dir}}/validation_report.json` | Structured results + `overall_passed` |

If you finish but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory |
| Panel size | `{{panel_size}}` | `8` | Number of synthetic encounters (the "clinic day"). 4 for a quick demo, 8–12 for a real run. |
| Scribe model | `{{scribe_model}}` | `anthropic/claude-sonnet-4-6` | litellm model string for the note writer (the workhorse under test) |
| Judge model | `{{judge_model}}` | `anthropic/claude-opus-4-8` | litellm model string for the judge. **Must differ from scribe** for independence. |
| Max iterations | `{{max_iterations}}` | `3` | Hill-climb rounds per encounter |
| Pass threshold | `{{pass_threshold}}` | `4.0` | Overall average to pass; also: no criterion < 3 AND zero hallucinations on the final note |

---

## Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Auth for scribe + judge (via litellm). |
| `litellm` (pip) | Yes | Provider-agnostic LLM calls (Anthropic / OpenAI / etc.) |
| `OPENAI_API_KEY` | No | Enables a cross-vendor judge for stronger independence. |

---

## Step 1: Environment Setup

```bash
pip install -q litellm
mkdir -p {{results_dir}}/transcripts {{results_dir}}/notes {{results_dir}}/scorecards
# Shared-panel mode (for an apples-to-apples model bake-off): if a panel was uploaded
# (case_sheets.json + encounter_*.md transcripts), reuse it verbatim and SKIP generation so
# every scribe grades IDENTICAL transcripts. Otherwise a fresh panel is generated below.
PANEL="$(find / -name 'case_sheets.json' -not -path '*/results/*' 2>/dev/null | head -1)"
if [ -n "$PANEL" ]; then
  cp "$PANEL" {{results_dir}}/case_sheets.json
  find / -name 'encounter_*.md' -not -path '*/results/*' 2>/dev/null | while read -r f; do cp "$f" {{results_dir}}/transcripts/ 2>/dev/null || true; done
  echo "SHARED PANEL DETECTED ($PANEL): $(ls {{results_dir}}/transcripts 2>/dev/null | wc -l) transcripts copied — generation will be SKIPPED."
else
  echo "No uploaded panel found — a fresh synthetic panel will be generated."
fi
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: need ANTHROPIC_API_KEY (preferred) or OPENAI_API_KEY"; exit 1
fi
python - <<'PY'
import os
has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
has_openai = bool(os.environ.get("OPENAI_API_KEY"))
print(f"Anthropic key: {'SET' if has_anthropic else 'missing'} | OpenAI key: {'SET' if has_openai else 'missing'}")
print("litellm import:", end=" ")
import litellm  # noqa
print("OK")
PY
```

Notes on model selection (adapt in the scripts below if a key is missing):
- If only `OPENAI_API_KEY` is set, use `openai/gpt-...` strings for scribe + judge.
- Keep **judge ≠ scribe**. A self-judging model rubber-stamps its own note (a known
  weak-model-self-validation failure mode) and the hill-climb will look like it passes when it
  hasn't moved. Cross-vendor (Anthropic scribe + OpenAI judge, or vice-versa) is strongest.

---

## Step 2: The Shared LLM Helper

Write `{{results_dir}}/_llm.py` once; every later step imports it. It wraps `litellm.completion`,
asks for JSON when needed, and retries on transient errors.

```python
# {{results_dir}}/_llm.py
import json, os, time, litellm

def call(model, system, user, json_mode=False, max_tokens=2000, temperature=0.4, retries=3):
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    kwargs = {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}  # ignored by providers that don't support it
    last = None
    for i in range(retries):
        try:
            r = litellm.completion(**kwargs)
            return r.choices[0].message.content
        except Exception as e:
            last = e; time.sleep(2 * (i + 1))
    raise last

def call_json(model, system, user, **kw):
    raw = call(model, system, user, json_mode=True, **kw)
    raw = raw.strip()
    if raw.startswith("```"):                      # strip markdown fences if a model adds them
        raw = raw.split("```", 2)[1].lstrip("json").strip() if "```" in raw[3:] else raw.strip("`")
    try:
        return json.loads(raw)
    except Exception:
        s, e = raw.find("{"), raw.rfind("}")        # last-resort: slice the outermost object
        return json.loads(raw[s:e + 1])
```

---

## Step 3: Generate the Synthetic Case Panel (hidden ground truth)

Write `{{results_dir}}/case_sheets.json`. Vary specialty + complexity, and embed exactly one
**trap** per case. **Fully fictional** — no real people, no real identifiers.

```python
import json, sys, os
sys.path.insert(0, "{{results_dir}}")
from _llm import call_json

# Shared-panel mode: an uploaded panel was copied in Step 1 — reuse it, skip generation.
if os.path.exists("{{results_dir}}/case_sheets.json") and os.path.getsize("{{results_dir}}/case_sheets.json") > 0:
    print("Shared panel present — skipping case-sheet generation."); raise SystemExit

PANEL_SIZE = int("{{panel_size}}")
CASE_MODEL = "{{scribe_model}}"   # the case author can be the workhorse; ground truth is structured

SEEDS = [  # (specialty, complexity, trap_type) — extended/truncated to PANEL_SIZE
    ("family medicine", "low",      "stopped_med"),
    ("cardiology",      "moderate", "denied_symptom"),
    ("pediatrics",      "low",      "indirect_value"),
    ("endocrinology",   "high",     "indirect_value"),
    ("dermatology",     "low",      "family_history"),
    ("psychiatry",      "moderate", "denied_symptom"),
    ("orthopedics",     "moderate", "stopped_med"),
    ("internal med",    "high",     "family_history"),
    ("urgent care",     "moderate", "stopped_med"),
    ("ob/gyn",          "moderate", "indirect_value"),
    ("gastroenterology","high",     "denied_symptom"),
    ("pulmonology",     "moderate", "family_history"),
]
SEEDS = (SEEDS * ((PANEL_SIZE // len(SEEDS)) + 1))[:PANEL_SIZE]

SYS = (
  "You author HIDDEN GROUND-TRUTH case sheets for a SYNTHETIC medical-scribe eval. Everything is "
  "fictional — invent patients, never use real people or real identifiers. Return ONLY JSON.")

cases = []
for i, (spec, cx, trap) in enumerate(SEEDS, 1):
    user = f"""Author one fictional outpatient encounter as a structured case sheet.
Specialty: {spec}. Complexity: {cx}. Embedded trap type: {trap}.

Trap semantics (embed exactly one, matching the type):
- stopped_med: patient mentions a medication they USED to take but STOPPED. Correct note must NOT list it as a current med.
- denied_symptom: patient explicitly DENIES a symptom. Correct note records it as a pertinent NEGATIVE, not a positive.
- indirect_value: patient states a value indirectly ("sugar around 200", "BP's been high at the pharmacy"). Capture as reported; do NOT fabricate a formal lab/vital.
- family_history: a FAMILY MEMBER's condition is mentioned. Belongs in Family History, NOT the patient's PMH.

Return JSON with keys:
  id ("encounter_{i:02d}"), specialty, complexity, trap_type, trap_detail (one sentence describing the exact trap fact),
  demographics ({{age, sex}} — synthetic, no name needed),
  chief_complaint (string),
  hpi_facts (array of short factual strings the clinician would document),
  ros (array of {{system, finding, pertinent_negative: bool}}),
  pmh (array), current_meds (array of {{name, dose}}), allergies (array),
  family_history (array), social_history (array),
  vitals ({{...}}), exam_findings (array of short strings),
  assessment (array of {{problem, icd10}}),
  plan (array of short strings)."""
    case = call_json(CASE_MODEL, SYS, user, max_tokens=2200, temperature=0.7)
    case["id"] = f"encounter_{i:02d}"
    case.setdefault("trap_type", trap)
    cases.append(case)
    print(f"  case {i}/{PANEL_SIZE}: {spec} / {cx} / trap={trap}")

json.dump(cases, open("{{results_dir}}/case_sheets.json", "w"), indent=2)
print(f"Wrote {len(cases)} case sheets.")
```

Spot-check `case_sheets.json`: each case has a clear `trap_detail`, a non-trivial `hpi_facts` list,
and at least one pertinent-negative ROS entry. Regenerate any case that's too thin to discriminate.

---

## Step 4: Synthesize the Ambient Transcripts

For each case, write `{{results_dir}}/transcripts/encounter_NN.md` — a realistic, **messy**
doctor–patient dialogue. The transcript must **contain every ground-truth fact** (so a perfect
note is achievable) **and the trap, stated the tricky way** — but NOT in SOAP order, with natural
filler, interruptions, and tangents. This is what an ambient scribe actually "hears."

```python
import json, sys, os
sys.path.insert(0, "{{results_dir}}")
from _llm import call

CASE_MODEL = "{{scribe_model}}"
cases = json.load(open("{{results_dir}}/case_sheets.json"))
# Shared-panel mode: transcripts already provided — skip synthesis so every scribe sees the same input.
if cases and all(os.path.getsize(f"{{results_dir}}/transcripts/{c['id']}.md") > 0 for c in cases if os.path.exists(f"{{results_dir}}/transcripts/{c['id']}.md")) \
   and all(os.path.exists(f"{{results_dir}}/transcripts/{c['id']}.md") for c in cases):
    print("Shared transcripts present — skipping transcript synthesis."); raise SystemExit

SYS = ("You write realistic ambient clinic-visit TRANSCRIPTS for a synthetic eval. Output a raw "
       "Doctor/Patient dialogue — natural, messy, with greetings, filler, a tangent or interruption, "
       "and facts revealed out of order. Do NOT structure it as a SOAP note. Do NOT label sections.")

for c in cases:
    user = (f"Turn this case sheet into a natural spoken transcript (~25–45 turns). Every fact below "
            f"must surface somewhere in the dialogue, and the TRAP must be spoken the tricky way "
            f"({c.get('trap_type')}: {c.get('trap_detail','')}). Vitals/exam come out as the clinician "
            f"says them aloud. Keep it conversational.\n\nCASE SHEET:\n{json.dumps(c, indent=2)}")
    txt = call(CASE_MODEL, SYS, user, max_tokens=2600, temperature=0.8)
    open(f"{{results_dir}}/transcripts/{c['id']}.md", "w").write(txt)
    print(f"  transcript: {c['id']} ({len(txt)} chars)")
```

Read one transcript end-to-end: is the trap genuinely embedded (e.g. the stopped med is mentioned
as stopped, not as a current med)? If a transcript leaks SOAP structure or omits the trap,
regenerate it.

---

## Step 5: The Baseline Scribe Prompt + the Hill-Climb Fix Library

The scribe starts thin on purpose. The **fix library** is the menu the climb draws from — each entry
targets one rubric criterion. Write `{{results_dir}}/scribe_prompt_final.md` at the end with the
prompt that won.

```python
BASELINE_SCRIBE = "You are a medical scribe. Write a SOAP note from this visit transcript."

# Each fix is appended to the scribe prompt when its criterion is the weakest unmet one.
FIX_LIBRARY = {
  "completeness": (
    "Capture every clinically salient fact: chief complaint, all HPI elements, pertinent positives "
    "AND negatives from the review of systems, current meds with doses, allergies, vitals, exam "
    "findings, assessment, and plan. Do not drop documented facts."),
  "groundedness": (
    "Every statement MUST be traceable to something said in the transcript. Never infer or invent "
    "labs, vitals, doses, or findings that were not stated. If the patient says they STOPPED a med, "
    "do not list it as current. If a value is given indirectly ('around 200'), record it as the "
    "patient reported it — do not fabricate a formal lab result. If something was not documented, "
    "omit it or write 'not documented' — never guess."),
  "structure": (
    "Use a strict SOAP template. SUBJECTIVE = what the patient reports (HPI, ROS, histories). "
    "OBJECTIVE = vitals + exam findings only. ASSESSMENT = problems/diagnoses. PLAN = orders, "
    "meds, follow-up. Put a family member's condition under Family History, never the patient's PMH."),
  "coding": (
    "In the Assessment, suggest an ICD-10 code for each documented problem and a plausible E/M CPT "
    "code for the visit. Every code must be defensible from documented findings — no codes for "
    "undocumented or ruled-out conditions."),
  "conciseness": (
    "Summarize; do not transcribe. No verbatim patient quotes unless clinically necessary. Each "
    "section scannable. Convey the signal, not the whole conversation."),
}
print("Baseline scribe prompt loaded; fix library has:", list(FIX_LIBRARY))
```

---

## Step 6: The Judge (rubric + hard hallucination floor)

The judge sees the **transcript + the hidden case sheet + the note** and returns structured scores
plus extracted **hallucinated claims** and **missed facts**. The hard floor is then applied
**deterministically in code** (not left to the judge's gestalt) so the gate can't be talked past.

```python
import sys
sys.path.insert(0, "{{results_dir}}")
from _llm import call_json

JUDGE_MODEL = "{{judge_model}}"
PASS = float("{{pass_threshold}}")

JUDGE_SYS = (
  "You are a STRICT clinical-documentation auditor. You are given a ground-truth case sheet, the "
  "visit transcript, and a SOAP note written from the transcript. Score the note. Be adversarial "
  "about hallucinations: list EVERY claim in the note not supported by the transcript. Return ONLY JSON.")

RUBRIC = """Score each 1-5 (5=excellent, 3=acceptable, 1=poor):
- completeness: fraction of ground-truth salient facts captured in the correct section
- groundedness: every claim traceable to the transcript (no invented findings/labs/doses); trap handled correctly
- structure: correct S/O/A/P placement and format
- coding: ICD-10/CPT suggestions defensible and tied to the documented A/P
- conciseness: summarized and scannable; no transcript-dumping"""

def judge_note(case, transcript, note):
    user = (f"{RUBRIC}\n\nGROUND TRUTH CASE SHEET:\n{__import__('json').dumps(case)}\n\n"
            f"TRANSCRIPT:\n{transcript}\n\nSOAP NOTE UNDER REVIEW:\n{note}\n\n"
            "Return JSON: {scores:{completeness,groundedness,structure,coding,conciseness}, "
            "hallucinated_claims:[strings], missed_facts:[strings], notes:{<criterion>:<one line>}}")
    v = call_json(JUDGE_MODEL, JUDGE_SYS, user, max_tokens=1800, temperature=0.0)
    s = {k: int(v["scores"][k]) for k in ["completeness","groundedness","structure","coding","conciseness"]}
    halluc = v.get("hallucinated_claims", []) or []
    # HARD FLOOR: any hallucination caps groundedness at 1 and the overall at 2.0
    if halluc:
        s["groundedness"] = 1
    overall = sum(s.values()) / 5.0
    if halluc:
        overall = min(overall, 2.0)
    passed = (overall >= PASS) and all(x >= 3 for x in s.values()) and not halluc
    return {"scores": s, "overall": round(overall, 2), "hallucinated_claims": halluc,
            "missed_facts": v.get("missed_facts", []), "notes": v.get("notes", {}), "passed": passed}
```

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | **Completeness** | All salient ground-truth facts captured in the right section | Core facts present, a few minor omissions | Major omissions; the note is unusable |
| 2 | **Groundedness** | Every claim traceable to the transcript; trap handled right | Mostly grounded, soft inferences | **Any hallucination → 1 (hard floor; caps overall at 2.0)** |
| 3 | **Structure** | Clean S/O/A/P; nothing in the wrong section | Mostly right; a misplaced item or two | Sections jumbled or missing |
| 4 | **Coding** | Defensible ICD-10 + CPT tied to documented A/P | Codes present but loose | Wrong/absent codes, or codes for undocumented dx |
| 5 | **Conciseness** | Summarized, scannable, signal-dense | A little bloated | Transcript dump |

**Pass threshold: overall ≥ {{pass_threshold}}, no criterion below 3, and ZERO hallucinations on the final note.**

---

## Step 7: Run the Panel — Scribe → Judge → Hill-Climb (the centerpiece)

For each encounter: write a note from the baseline prompt, judge it, then while it fails and rounds
remain, **append the fix for the weakest criterion**, regenerate, re-judge — logging every
iteration. Persist the best note + the full `iteration_log`.

```python
import json, sys
sys.path.insert(0, "{{results_dir}}")
from _llm import call

SCRIBE_MODEL = "{{scribe_model}}"
MAX_ITERS = int("{{max_iterations}}")
cases = json.load(open("{{results_dir}}/case_sheets.json"))

def write_note(scribe_prompt, transcript):
    return call(SCRIBE_MODEL, scribe_prompt, f"VISIT TRANSCRIPT:\n{transcript}", max_tokens=1800, temperature=0.3)

CRIT_ORDER = ["groundedness", "completeness", "structure", "coding", "conciseness"]  # fix groundedness first

for c in cases:
    transcript = open(f"{{results_dir}}/transcripts/{c['id']}.md").read()
    prompt = BASELINE_SCRIBE
    applied, log, best = [], [], None
    for it in range(1, MAX_ITERS + 1):
        note = write_note(prompt, transcript)
        verdict = judge_note(c, transcript, note)
        log.append({"iteration": it, "applied_fixes": list(applied),
                    "scores": verdict["scores"], "overall": verdict["overall"],
                    "hallucinations": len(verdict["hallucinated_claims"]), "passed": verdict["passed"]})
        if best is None or verdict["overall"] > best["overall"]:
            best = {"note": note, **verdict}
        print(f"  {c['id']} iter {it}: overall={verdict['overall']} "
              f"halluc={len(verdict['hallucinated_claims'])} passed={verdict['passed']}")
        if verdict["passed"]:
            break
        # pick the weakest UNMET criterion not already patched (groundedness prioritized)
        unmet = sorted([k for k in CRIT_ORDER if verdict["scores"][k] < 5 and k not in applied],
                       key=lambda k: (verdict["scores"][k], CRIT_ORDER.index(k)))
        if not unmet:
            break
        target = unmet[0]; applied.append(target)
        prompt = prompt + "\n\n" + FIX_LIBRARY[target]

    open(f"{{results_dir}}/notes/{c['id']}.md", "w").write(best["note"])
    json.dump({"id": c["id"], "specialty": c.get("specialty"), "trap_type": c.get("trap_type"),
               "final": {k: best[k] for k in ["scores","overall","hallucinated_claims","missed_facts","passed","notes"]},
               "iteration_log": log, "winning_fixes": applied},
              open(f"{{results_dir}}/scorecards/{c['id']}.json", "w"), indent=2)
    # the prompt that won this encounter (longest/strongest); keep the most-patched as the shippable artifact
    open("{{results_dir}}/scribe_prompt_final.md", "w").write(
        "# Hill-climbed scribe system prompt\n\n```\n" + prompt + "\n```\n")
    print(f"{c['id']} done: final overall={best['overall']} fixes={applied}")
```

Each `iteration_log` should show the climb — e.g. iter 1 overall 2.0 (a hallucinated lab),
iter 2 after the groundedness fix → 3.4, iter 3 after completeness → 4.2 (pass). If an encounter
*starts* passing (baseline 4.0+), that case isn't discriminating — note it; the panel's value is the
ones that have to climb.

---

## Step 8: Aggregate Leaderboard

Write `{{results_dir}}/leaderboard.md`: per-criterion means at baseline (iter 1) vs final, the
panel pass rate, total hallucination incidents caught, and the average iterations-to-pass.

```python
import json, glob
rows = [json.load(open(f)) for f in sorted(glob.glob("{{results_dir}}/scorecards/*.json"))]
crits = ["completeness","groundedness","structure","coding","conciseness"]

def mean(xs): return round(sum(xs)/len(xs), 2) if xs else 0.0
base = {k: mean([r["iteration_log"][0]["scores"][k] for r in rows]) for k in crits}
final = {k: mean([r["final"]["scores"][k] for r in rows]) for k in crits}
pass_rate = mean([1 if r["final"]["passed"] else 0 for r in rows]) * 100
halluc_caught = sum(il["hallucinations"] for r in rows for il in r["iteration_log"])
iters = mean([len(r["iteration_log"]) for r in rows])

lines = ["# Ambient Scribe Quality Gate — Leaderboard\n",
         f"- Encounters: {len(rows)}  |  Pass rate: {pass_rate:.0f}%  |  Avg iterations/encounter: {iters}",
         f"- Hallucination incidents caught across the climb: {halluc_caught}\n",
         "| Criterion | Baseline (iter 1) | Final | Δ |", "|---|---|---|---|"]
for k in crits:
    lines.append(f"| {k} | {base[k]} | {final[k]} | {round(final[k]-base[k],2):+} |")
lines += ["", "| Encounter | Specialty | Trap | Iters | Final | Passed | Winning fixes |",
          "|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['id']} | {r.get('specialty','')} | {r.get('trap_type','')} | "
                 f"{len(r['iteration_log'])} | {r['final']['overall']} | "
                 f"{'✅' if r['final']['passed'] else '❌'} | {', '.join(r.get('winning_fixes',[])) or '—'} |")
open("{{results_dir}}/leaderboard.md","w").write("\n".join(lines))
print("\n".join(lines))
```

---

## Step 9: Write Executive Summary

Write `{{results_dir}}/summary.md`: the climb story in plain language — where the panel started,
which criterion was the biggest lever (usually groundedness — the hallucination floor does the
work), the final pass rate, and the **winning scribe prompt** (the artifact a real scribe team would
ship). Include the per-criterion baseline→final table and 1–2 vivid examples (e.g. "encounter_04
invented an A1c of 7.2 the patient never gave; the groundedness fix replaced it with 'patient
reports home glucose ~200', clearing the floor").

---

## Step 10: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "eval": "ambient-scribe-soap-hillclimb",
  "parameters": {"panel_size": 8, "scribe_model": "{{scribe_model}}", "judge_model": "{{judge_model}}",
                 "max_iterations": 3, "pass_threshold": 4.0},
  "stages": [
    {"name": "setup", "passed": true, "message": ""},
    {"name": "case_panel", "passed": true, "message": "N synthetic ground-truth case sheets w/ traps"},
    {"name": "transcripts", "passed": true, "message": "messy ambient transcripts containing every fact + the trap"},
    {"name": "scribe_judge_climb", "passed": true, "message": "per-encounter hill-climb; hard hallucination floor"},
    {"name": "leaderboard", "passed": true, "message": "baseline vs final per-criterion + pass rate"}
  ],
  "panel": {"encounters": 0, "pass_rate_pct": 0, "avg_iterations": 0.0, "hallucinations_caught": 0},
  "per_criterion_final_mean": {"completeness": 0, "groundedness": 0, "structure": 0, "coding": 0, "conciseness": 0},
  "pass_threshold": 4.0,
  "overall_passed": false,
  "output_files": [
    "{{results_dir}}/case_sheets.json","{{results_dir}}/leaderboard.md","{{results_dir}}/summary.md",
    "{{results_dir}}/scribe_prompt_final.md","{{results_dir}}/validation_report.json"
  ]
}
```

Set `overall_passed` true when the panel pass rate meets your bar (e.g. ≥ 75% of encounters pass the
gate) — and say so explicitly in `summary.md`.

---

## Final Checklist (MANDATORY)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"; FAIL=0
for f in case_sheets.json leaderboard.md summary.md scribe_prompt_final.md validation_report.json; do
  if [ ! -s "$RESULTS_DIR/$f" ]; then echo "FAIL: $f missing/empty"; FAIL=$((FAIL+1)); else echo "PASS: $f ($(wc -c < "$RESULTS_DIR/$f") bytes)"; fi
done
NT=$(ls "$RESULTS_DIR"/transcripts/*.md 2>/dev/null | wc -l | tr -d ' ')
NN=$(ls "$RESULTS_DIR"/notes/*.md 2>/dev/null | wc -l | tr -d ' ')
NS=$(ls "$RESULTS_DIR"/scorecards/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "transcripts=$NT notes=$NN scorecards=$NS"
[ "$NT" -ge 1 ] && [ "$NT" = "$NN" ] && [ "$NN" = "$NS" ] || { echo "FAIL: per-encounter file counts mismatch"; FAIL=$((FAIL+1)); }
[ "$FAIL" -gt 0 ] && { echo "OVERALL: FAIL ($FAIL)"; exit 1; }; echo "OVERALL: PASS"
```

- [ ] `case_sheets.json` written with `panel_size` synthetic cases, each with a `trap_detail`
- [ ] One transcript, one note, one scorecard per encounter (counts match)
- [ ] Every scorecard has an `iteration_log` showing the climb (scores per round)
- [ ] The hard hallucination floor fired at least once across the panel (the gate has teeth)
- [ ] `judge_model` ≠ `scribe_model` (independence)
- [ ] `leaderboard.md` shows baseline→final per-criterion deltas + pass rate
- [ ] `scribe_prompt_final.md` is the hill-climbed prompt; `summary.md` tells the climb story
- [ ] Verification script printed PASS

**Do not finish until every item passes.**

## Tips

- **Synthetic only.** No real PHI ever. This is a documentation-quality eval, not clinical advice.
- **Judge ≠ scribe** is non-negotiable for a credible climb — same-model judging rubber-stamps.
- **The hallucination floor is the whole point.** It's computed in code from the judge's extracted
  claim list, not from the judge's overall vibe — so the climb can't pad its way past the gate.
- **Start the scribe thin.** A strong baseline prompt leaves no room to climb and kills the demo.
  The visible 2.0 → 4.2 arc per encounter is the story worth showing.
- **Groundedness usually moves first and most** — fix it before chasing completeness/coding.
- For a fast walkthrough use `panel_size=4`; for a real run use `8–12` (and budget the minutes —
  that runtime *is* the "long-running agentic workflow" half of the demo).
