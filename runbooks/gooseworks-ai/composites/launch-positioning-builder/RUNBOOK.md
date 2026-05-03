---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/launch-positioning-builder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/launch-positioning-builder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Launch Positioning Builder
  imported_at: '2026-05-03T02:46:03Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: launch-positioning-builder
    confidence: high
secrets: null
---

# Launch Positioning Builder — Agent Runbook
## Objective

Research competitors, analyze their messaging, and generate a positioning document with category definition, differentiation claims, value propositions, and proof points. Chains web research, competitor site analysis, and review mining to produce a positioning doc ready for website copy and sales deck use. Use when a product marketing team needs to define or refresh positioning ahead of a launch, rebrand, or competitive shift. The runbook guides an agent through intake, competitive research, positioning framework selection, a positioning map, and final document assembly. The output should be opinionated, evidence-backed, and ready for website copy, sales decks, investor materials, and launch planning.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `summary.md` | Executive summary of the positioning work, inputs, key decisions, and output path |
| `validation_report.json` | Programmatic validation report for source research, generated positioning document, and required outputs |
| `positioning-[YYYY-MM-DD].md` | Final positioning document saved in the working directory or user-specified path |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory for `summary.md`, `validation_report.json`, and any copied final artifacts |
| `output_path` | `positioning-[YYYY-MM-DD].md` | Markdown file path for the final positioning document |
| `product_name_url` | required | What are you positioning? |
| `one_sentence_pitch` | required | How do you describe what you do today? |
| `top_2_3_competitors` | required | Names + URLs. Who does your buyer compare you to? |
| `icp` | required | Title, company type, stage (e.g., "Head of Growth at Series A B2B SaaS") |
| `key_differentiators` | required | What do you believe makes you different? (even if not yet articulated) |
| `existing_proof_points` | required | Customer wins, metrics, logos, quotes (anything you have) |
| `positioning_trigger` | required | Why now? (new launch, competitive pressure, rebrand, entering new segment) |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Web search capability | Yes | Find competitor websites, category pages, review pages, ad copy, and public proof points |
| Webpage fetch capability | Yes | Read homepages, pricing pages, about pages, and customer story pages |
| Markdown-capable filesystem access | Yes | Write the final positioning document and validation files |
| `review-site-scraper` or equivalent review access | Optional | Mine G2/Capterra reviews when available |

## Step 1: Environment Setup

1. Create `results_dir` if it does not exist.
2. Confirm `output_path` is writable.
3. Capture the current UTC date for the positioning document filename when no explicit `output_path` is supplied.
4. Initialize a validation report with stages for intake, research, synthesis, output writing, and final verification.

```bash
mkdir -p /app/results
python - <<'PY'
from pathlib import Path
for name in ['summary.md', 'validation_report.json']:
    assert Path('/app/results').exists(), 'results directory missing'
print('environment ready')
PY
```

## Step 2: Intake

1. **Product name + URL** — What are you positioning?
2. **One-sentence pitch** — How do you describe what you do today?
3. **Top 2-3 competitors** — Names + URLs. Who does your buyer compare you to?
4. **ICP** — Title, company type, stage (e.g., "Head of Growth at Series A B2B SaaS")
5. **Key differentiators** — What do you believe makes you different? (even if not yet articulated)
6. **Existing proof points** — Customer wins, metrics, logos, quotes (anything you have)
7. **Positioning trigger** — Why now? (new launch, competitive pressure, rebrand, entering new segment)

If any required intake item is missing, ask the operator for the missing value before continuing. Do not invent competitor URLs, customer proof, or ICP definitions.

## Step 3: Competitive Landscape Research



For each competitor, capture source URLs and short evidence notes. Prefer direct competitor pages and public reviews over secondary summaries.

## Step 4: Positioning Framework

Build the positioning doc using April Dunford's framework adapted for early-stage:

Choose the category approach explicitly and record the rationale. Map each unique attribute to customer value and a proof point before writing final copy.

## Step 5: Competitive Positioning Map

Create a 2x2 positioning matrix:

```
                    [Dimension A: e.g., Ease of Use]
                    High
                      |
         [You]        |       [Competitor A]
                      |
    ──────────────────┼──────────────────
                      |
      [Competitor C]  |       [Competitor B]
                      |
                    Low
        Low ──────────────────────── High
                    [Dimension B: e.g., Enterprise-readiness]
```

Choose dimensions where you win on at least one axis. Avoid dimensions where you lose on both.

Select axes where the product has a defensible advantage on at least one dimension. Include a short explanation of why the chosen dimensions matter to the ICP.

## Step 6: Generate the Positioning Document

```markdown
# Positioning Document — [Product Name]
Created: [DATE] | Trigger: [launch/rebrand/competitive shift]

---

Write the document to `output_path`. If `output_path` is not provided, use `positioning-[YYYY-MM-DD].md` in the current working directory.

## Step 7: Validate Outputs

Check that the positioning document includes a positioning statement, category rationale, competitive landscape, value propositions, proof points, audience messaging, positioning map, deployment table, and messaging guardrails. Write `/app/results/summary.md` and `/app/results/validation_report.json` with the validation results.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails, run up to max 3 rounds of targeted fixes. In each round, repair only missing or weak sections, preserve cited evidence, and re-run the validation checklist. Stop early once every required output is present and the positioning document is complete.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing proof point | Mark it as unavailable and suggest the strongest evidence to collect next |
| Competitor claims lack sources | Revisit competitor website or review sources and add URLs in notes |
| Category rationale is vague | Tie the choice to ICP search behavior, sales-call education burden, and existing category fit |
| Positioning statement is generic | Rewrite around the strongest differentiator, primary alternative, and measurable customer value |

## Step 9: Final Checklist

Run the final verification after writing all outputs.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
POSITIONING_FILE="${OUTPUT_PATH:-positioning-$(date -u +%Y-%m-%d).md}"
if [ ! -s "$POSITIONING_FILE" ]; then
  echo "FAIL: $POSITIONING_FILE is missing or empty"
else
  echo "PASS: $POSITIONING_FILE ($(wc -c < "$POSITIONING_FILE") bytes)"
fi
```

## Tips

Use the trigger phrases below to recognize this workflow. Keep the final positioning opinionated and backed by the strongest available evidence.

- "Build a positioning doc for [product]"
- "How should we position against [competitor]?"
- "We need positioning before our launch"
- "Run the positioning builder for [client]"
