---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/soultrace-ai/soultrace-skill/soultrace"
  source_host: "skills.sh"
  source_title: "SoulTrace Personality Assessment"
  imported_at: "2026-05-01T02:21:52Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "soultrace-ai"
    skill_name: "soultrace"
    confidence: "high"
secrets: {}
---

# SoulTrace Personality Assessment — Agent Runbook

## Objective

Take an adaptive personality assessment through the SoulTrace API. The agent guides the user through 24 questions on a 1–7 Likert scale, sending all accumulated answers with every request (the API is stateless and replays Bayesian inference on each call). At completion, the user receives their personality archetype based on a 5-color psychological model (White=structure, Blue=understanding, Black=agency, Red=intensity, Green=connection) and is classified into one of 25 archetypes. Useful when users want a personality test, want to discover their psychological archetype, or seek a color-based personality profile.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/assessment_result.json` | Final API response with archetype, scores, and color distribution |
| `/app/results/answers_log.json` | Full ordered log of question IDs and user responses (1–7) |
| `/app/results/summary.md` | Executive summary of the assessment run, archetype, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| API endpoint | `https://soultrace.app/api/agent` | SoulTrace stateless assessment API (POST) |
| Total questions | 24 | Fixed number of questions in each assessment |
| Score range | 1–7 | Likert scale per response (1=Strongly disagree, 7=Strongly agree) |
| Rate limit | 100 req/hour per IP | Enforced by SoulTrace API |
| Max retries | 3 | Per-question retry limit before aborting |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `requests` | Python package | Yes | HTTP client for SoulTrace API calls |
| `curl` | CLI | Optional | Alternative for manual API testing |
| SoulTrace API | External API | Yes | `https://soultrace.app/api/agent` — no auth required, 100 req/hour per IP |

---

## Step 1: Environment Setup

```bash
pip install requests
mkdir -p /app/results

# Verify API reachability
curl -s -X POST https://soultrace.app/api/agent \
  -H "Content-Type: application/json" \
  -d '{"answers": []}' | python3 -m json.tool
```

If the API returns a non-200 response or connection times out, check the SoulTrace status and wait for the rate limit to reset (100 req/hour per IP).

---

## Step 2: Start the Assessment

Send an empty answers array to receive the first question:

```python
import requests, json, pathlib

API = "https://soultrace.app/api/agent"

response = requests.post(API, json={"answers": []}, timeout=15)
response.raise_for_status()
data = response.json()
print(json.dumps(data, indent=2))
```

Expected response:
```json
{
  "status": "in_progress",
  "question": {
    "id": 42,
    "text": "I find deep satisfaction in mastering complex systems."
  },
  "currentDistribution": {
    "white": 0.2, "blue": 0.2, "black": 0.2, "red": 0.2, "green": 0.2
  },
  "entropy": 2.322,
  "progress": {"answered": 0, "total": 24}
}
```

---

## Step 3: Collect All 24 Answers (max 3 rounds of retries per question)

Present each question to the user on a 1–7 Likert scale and re-POST all accumulated answers after each response. The API selects the next optimal question via Bayesian inference on each call.

```python
import requests, json, pathlib

API = "https://soultrace.app/api/agent"
answers = []
answers_log = []

r = requests.post(API, json={"answers": answers}, timeout=15)
r.raise_for_status()
data = r.json()

while data.get("status") == "in_progress":
    q = data["question"]
    print(f"\nQuestion {len(answers)+1}/24: {q['text']}")
    print("Rate 1 (Strongly disagree) to 7 (Strongly agree):")

    score = None
    for attempt in range(3):
        try:
            score = int(input("> "))
            if 1 <= score <= 7:
                break
        except ValueError:
            pass
        print("Please enter a number between 1 and 7")

    if score is None:
        raise RuntimeError("Failed to get valid score after 3 attempts")

    answers.append({"questionId": q["id"], "score": score})
    answers_log.append({
        "question_id": q["id"],
        "question_text": q["text"],
        "score": score,
        "answered": len(answers)
    })

    r = requests.post(API, json={"answers": answers}, timeout=15)
    r.raise_for_status()
    data = r.json()

# Save full answers log
pathlib.Path("/app/results/answers_log.json").write_text(json.dumps(answers_log, indent=2))
print("Status:", data.get("status"), "— answered:", len(answers), "questions")
```

---

## Step 4: Process and Save Results

When `status == "complete"`, persist the full API response and display the archetype:

```python
import json, pathlib

# `data` is the final API response from Step 3
if data.get("status") == "complete":
    pathlib.Path("/app/results/assessment_result.json").write_text(
        json.dumps(data, indent=2)
    )

    archetype = data.get("archetype", {})
    colors = data.get("finalDistribution", {})

    print("\n=== YOUR PERSONALITY RESULTS ===")
    print(f"Archetype: {archetype.get('name', 'Unknown')}")
    print(f"Description: {archetype.get('description', '')}")
    print("\nColor Profile:")
    for color, pct in colors.items():
        bar = "█" * int(pct * 20)
        print(f"  {color.capitalize():8}: {bar} {pct:.1%}")
else:
    raise RuntimeError(f"Unexpected status: {data.get('status')}. Expected 'complete'.")
```

The 5-color model:
- **White** — Structure, order, rule-following
- **Blue** — Understanding, analysis, curiosity
- **Black** — Agency, autonomy, willpower
- **Red** — Intensity, passion, drive
- **Green** — Connection, empathy, harmony

---

## Step 5: Iterate on Errors (max 3 rounds)

If any step fails:

1. Read the specific failed stage from `validation_report.json`
2. Apply the targeted fix from the table below
3. Retry the failed step
4. Repeat up to 3 times total

After 3 rounds, if still failing: write partial results to `/app/results/` and set `overall_passed: false` in `validation_report.json`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| HTTP 429 Too Many Requests | Wait 60s (100 req/hour limit per IP), then retry |
| `answers` array rejected by API | Ensure each entry has `questionId` (int) and `score` (int 1–7) |
| Assessment stuck after 24 answers | Verify all 24 answers submitted; check `progress.answered` in last response |
| Connection timeout | Increase timeout to 30s; verify `https://soultrace.app` is reachable |
| Invalid user input | Re-prompt: "Please enter a whole number between 1 and 7" |

---

## Step 6: Write Executive Summary

```python
import pathlib, json, datetime

result_path = pathlib.Path("/app/results/assessment_result.json")
result = json.loads(result_path.read_text()) if result_path.exists() else {}
archetype = result.get("archetype", {})
answers_log = json.loads(pathlib.Path("/app/results/answers_log.json").read_text()) if pathlib.Path("/app/results/answers_log.json").exists() else []

summary = f"""# SoulTrace Assessment — Results

## Overview
- **Date**: {datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}
- **API**: https://soultrace.app/api/agent
- **Questions answered**: {len(answers_log)} / 24
- **Archetype**: {archetype.get("name", "N/A")}
- **Status**: {result.get("status", "unknown")}

## Color Profile
```json
{json.dumps(result.get("finalDistribution", {}), indent=2)}
```

## Issues / Manual Follow-up
- If fewer than 24 questions were answered, re-run from scratch (API is stateless)
- Check `assessment_result.json` for full archetype description and traits

## Provenance
- Origin: https://skills.sh/soultrace-ai/soultrace-skill/soultrace
- Imported by: skill-to-runbook-converter v1.0.0
"""
pathlib.Path("/app/results/summary.md").write_text(summary)
print("Summary written.")
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/assessment_result.json" \
  "$RESULTS_DIR/answers_log.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `assessment_result.json` exists with `status: "complete"` and archetype data
- [ ] `answers_log.json` contains all 24 question/score pairs
- [ ] `summary.md` shows the archetype name and color profile
- [ ] `validation_report.json` exists with `overall_passed: true`
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **The API is stateless.** Pass ALL accumulated answers with every POST — never send only the latest answer.
- **Score scale is 1–7.** Clarify this to users before starting: 1=Strongly disagree, 4=Neutral, 7=Strongly agree.
- **24 questions are fixed.** The Bayesian algorithm selects adaptively, but always terminates at 24 total.
- **No auth required.** Rate limiting: 100 requests/hour per IP. Space out multi-user sessions accordingly.
- **5 colors → 25 archetypes.** The final archetype emerges from dominant color combinations — only determined after all 24 questions.
- **Handle interruptions gracefully.** If the session is interrupted, restart from scratch — there is no server-side session state.
