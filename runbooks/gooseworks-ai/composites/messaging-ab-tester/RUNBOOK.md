---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/messaging-ab-tester/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/messaging-ab-tester
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Messaging A/B Tester
  imported_at: '2026-05-03T02:46:12Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: messaging-ab-tester
    confidence: high
secrets: null
---

# Messaging A/B Tester — Agent Runbook

## Objective

Generate 3-5 distinct messaging variants for a value proposition, design a structured A/B test, and analyze channel results to identify which framing best resonates with the stated ICP. This runbook is intended for early-stage teams that lack enough website traffic for reliable site A/B tests but can still collect directional signal from LinkedIn organic posts, cold email splits, or both. It preserves the source skill's principle: make messaging decisions from measured response data, not internal preference.

Source summary: Generate 3-5 messaging variants for a value proposition, design structured A/B tests, and analyze results to determine which framing resonates most with ICP. Tests can run via LinkedIn organic posts, cold email subject line splits, or both. Pure reasoning for variant generation and analysis — the user deploys the tests through their own tools. Use when a team can't decide between messaging angles and needs data, not opinions.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/messaging_variants.md` | The generated 3-5 messaging variants with hypotheses and channel-specific copy |
| `/app/results/test_plan.md` | The LinkedIn, cold email, or combined test design with setup instructions and measurement plan |
| `/app/results/analysis_report.md` | The final winner analysis after result data is provided |
| `/app/results/summary.md` | Executive summary of inputs, selected channel, winner, and recommended deployment |
| `/app/results/validation_report.json` | Structured validation results for required inputs, generated outputs, and final checklist |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Directory where all required output files are written |
| Core value proposition | Required | The claim, product benefit, or positioning angle to test |
| Test goal | Required | The decision this test should inform, such as website headline, outbound angle, or content strategy |
| ICP | Required | The target audience, including title, company profile, and stage where known |
| Current messaging | Optional | Baseline copy or positioning to beat |
| Test channel | `both` | One of `linkedin`, `email`, or `both` |
| Sample size available | Optional | Typical LinkedIn impressions, email list size, or both |
| Number of variants | `3` | Generate 3-5 variants; use fewer when sample size is limited |
| Test duration | LinkedIn: 1 week; email: 3-5 days | Planned duration before collecting results |
| Results data | Optional until analysis phase | Metrics pasted manually, uploaded as CSV, or provided via screenshot transcription |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| LLM reasoning | Yes | Generate variants, hypotheses, scoring, and analysis |
| LinkedIn account or scheduler | Required for LinkedIn tests | Publish organic post variants and collect analytics |
| Outreach tool with A/B testing | Required for email tests | Run subject line or opening-hook splits; examples include Smartlead, Instantly, and Lemlist |
| Spreadsheet or CSV viewer | Optional | Normalize exported campaign metrics |

## Step 1: Environment Setup

1. Create the results directory if it does not exist.
2. Confirm the user supplied `core_value_prop`, `test_goal`, and `icp`.
3. Set `test_channel` to `linkedin`, `email`, or `both`; default to `both` when the user has both channels available.
4. Initialize `validation_report.json` with setup status and input completeness.

```bash
mkdir -p /app/results
python - <<'PY'
import json, pathlib, datetime
report = {
  "version": "1.0.0",
  "run_date": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
  "stages": [{"name": "setup", "passed": True, "message": "Results directory ready"}],
  "overall_passed": True
}
pathlib.Path("/app/results/validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
PY
```

## Step 2: Intake

Collect the decision context before writing variants:

1. Identify the core value proposition to test.
2. Capture the target ICP in enough detail to reason about motivations and objections.
3. Record the current messaging baseline if one exists.
4. Confirm available test channels and sample sizes.
5. Choose 3-5 variants, with 3 as the default when traffic or list size is limited.

Ask concise follow-up questions when required inputs are missing. Do not generate final variants until the value proposition, test goal, and ICP are clear.

## Step 3: Generate Messaging Variants

Create 3-5 variants that test different strategic angles, not superficial wording changes. Use these angle families where relevant:

| Type | What It Tests | Example |
|---|---|---|
| Outcome-driven | Leading with the result | `3x your pipeline in 30 days` |
| Pain-driven | Leading with the problem | `Tired of spending 4 hours a day on manual prospecting?` |
| Identity-driven | Leading with who the buyer is | `Built for growth teams who move fast` |
| Proof-driven | Leading with evidence | `How a customer went from 10 to 50 demos/month` |
| Contrast-driven | Leading with what the product is not | `Not another CRM. An outbound engine.` |

For each variant, write:

```markdown
## Variant [N]: [Type]

Hypothesis: [Why this framing should resonate with the ICP]

### LinkedIn Post
[100-200 words in native LinkedIn style]

### Email Subject Line
[Maximum 50 characters]

### Email Opening Hook
[First two sentences]

### Website Headline
[Maximum 10 words]
```

Save the completed variants to `/app/results/messaging_variants.md`.

## Step 4: Design and Deploy Tests

Choose the test design that matches `test_channel`.

### LinkedIn Organic

1. Schedule variants as consecutive posts, one per day, at the same time of day.
2. Keep length, format, and CTA similar so the message angle is the main variable.
3. Do not boost posts; use organic reach for cleaner comparison.
4. Measure each post after 48 hours.

Track impressions, reactions, comments, comment sentiment, profile visits when available, and DMs that mention the post.

### Cold Email

1. Create an A/B test campaign in the user's outreach tool.
2. Split the list evenly across variants, with at least 50 recipients per variant for directional signal and 200+ for stronger confidence.
3. Use the same sender, send time, body structure, and CTA unless the opening hook is the variable being tested.
4. Measure after 3-5 days.

Track sends, opens, replies, positive replies, and clicks when available.

### Both Channels

Run LinkedIn and email in parallel when possible. Treat channel disagreement as useful signal: a message can win in public social proof while another wins in private outbound.

Save the chosen setup and measurement plan to `/app/results/test_plan.md`.

## Step 5: Collect Results

Accept metrics in any usable form: pasted values, CSV export, screenshot transcription, or a concise manual summary. Normalize the data into tables before scoring.

For LinkedIn, require impressions plus at least one engagement metric per variant. For email, require sends plus at least one response metric per variant. If the user provides incomplete data, mark the missing fields and continue with directional analysis only.

## Step 6: Analyze Results

Use the scoring framework below and explain confidence based on sample size.

| Metric | Weight (LinkedIn) | Weight (Email) |
|---|---:|---:|
| Engagement rate | 30% | 0% |
| Comment quality | 30% | 0% |
| Impressions | 20% | 0% |
| Profile visits or clicks | 20% | 0% |
| Open rate | 0% | 30% |
| Reply rate | 0% | 40% |
| Positive reply rate | 0% | 30% |

For email tests, require more than a 20% relative difference in the primary metric before calling a winner. For LinkedIn tests, treat results under 500 impressions per post as directional.

Write `/app/results/analysis_report.md` with:

```markdown
# Messaging A/B Test Results — [DATE]

Value prop tested: [description]
ICP: [target audience]
Test duration: [dates]

## Winner: Variant [N] — [Type]

Primary metric: [metric and value]
Relative improvement: [percentage]
Confidence: [directional/moderate/strong]

## Why It Won
[Interpretation tied to ICP psychology and channel behavior]

## Recommended Deployment
- Website headline: [adapted version]
- Sales deck opening: [adapted version]
- LinkedIn bio or post theme: [adapted version]
- Cold email default: [adapted version]

## What to Test Next
1. [Next angle suggested by results]
2. [Segment or channel follow-up]
```

## Step 7: Iterate on Errors (max 3 rounds)

If required inputs, output files, or metrics are incomplete, perform up to max 3 rounds of targeted repair:

| Issue | Fix |
|---|---|
| Missing value proposition, goal, or ICP | Ask for the specific missing input before generating variants |
| Fewer than 3 variants requested | Warn that signal may be weak and generate 3 variants unless the user insists |
| No channel selected | Default to `both` if both are available; otherwise choose the available channel |
| Email sample below 50 per variant | Mark confidence as directional and avoid strong winner claims |
| LinkedIn impressions below 500 per post | Mark confidence as directional and recommend a follow-up test |
| Missing required output file | Recreate the file and rerun the final verification script |

After each repair, update `/app/results/validation_report.json`.

## Final Checklist

Write `/app/results/summary.md` with the selected winner, confidence level, recommended deployment, and any limitations. Then run this verification script:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/messaging_variants.md"   "$RESULTS_DIR/test_plan.md"   "$RESULTS_DIR/analysis_report.md"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Checklist:

- [ ] Variants test distinct strategic angles
- [ ] Test design controls timing, sender, CTA, and format where possible
- [ ] Metrics are normalized before scoring
- [ ] Winner confidence reflects sample size and relative lift
- [ ] `summary.md` and `validation_report.json` are present
- [ ] Verification script prints PASS for every required file

## Tips

- Test angles, not synonyms; each variant should represent a different strategic bet.
- Use organic LinkedIn and outbound email when website traffic is too low for useful site experiments.
- Treat small samples as directional and use the result to choose the next sharper test.
