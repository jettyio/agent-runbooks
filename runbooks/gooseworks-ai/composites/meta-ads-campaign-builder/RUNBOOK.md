---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/meta-ads-campaign-builder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/meta-ads-campaign-builder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Meta Ads Campaign Builder
  imported_at: '2026-05-03T02:36:05Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: meta-ads-campaign-builder
    confidence: high
secrets: null
---

# Meta Ads Campaign Builder - Agent Runbook

## Objective

Build a complete Meta Ads campaign structure for Facebook and Instagram from a product, ICP, objective, budget, and tracking context. The runbook produces audience targeting recommendations, ad set structure, copy frameworks per placement, budget allocation, tracking checks, launch checks, and early monitoring guidance. It is focused on campaign architecture and planning quality, not creative asset generation or direct Ads Manager execution.

If competitor names are supplied, research public Meta Ad Library examples and use the findings to improve positioning, audience assumptions, and copy angles. Keep all recommendations tied to the supplied objective, available budget, landing pages, and whether the campaign is B2B or B2C.

## REQUIRED OUTPUT FILES (MANDATORY)

All files MUST be written under `{{ results_dir }}`. The task is incomplete until each required file exists and is non-empty.

| File | Description |
|---|---|
| `meta_campaign_plan.md` | Complete campaign brief with overview, campaign structure, audience targeting, ad copy, budget and bidding plan, tracking setup checklist, launch checklist, and week 1-2 monitoring plan. |
| `campaign_structure.csv` | Structured export of campaigns, ad sets, audience definitions, placements, budgets, bidding strategy, and copy variants. |
| `summary.md` | Executive summary of the generated campaign plan, key assumptions, and any constraints or follow-up needs. |
| `validation_report.json` | Programmatic validation report covering input completeness, output generation, structural checks, and final file verification. |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `{{ results_dir }}` | `/app/results` | Output directory for all required files. |
| Product name | `{{ product_name }}` | required | Product, brand, or offer being advertised. |
| Product URL | `{{ product_url }}` | required | Website or page used to understand the product and offer. |
| Campaign objective | `{{ campaign_objective }}` | required | One of awareness, traffic, lead_generation, conversions, or app_installs. |
| ICP | `{{ icp }}` | required | Target buyer role, company size, industry, pains, buying triggers, and exclusions. |
| Monthly budget | `{{ monthly_budget }}` | required | Budget allocated to Meta Ads for this campaign. |
| Landing pages | `{{ landing_pages }}` | required | One or more landing pages traffic will use. |
| Competitor names | `{{ competitor_names }}` | optional | Competitors or alternatives for public ad research. |
| Tracking status | `{{ tracking_status }}` | unknown | Meta Pixel, Conversions API, custom events, and analytics status. |
| Business type | `{{ business_type }}` | required | B2B or B2C. Changes audience strategy and exclusions. |
| Geographic targeting | `{{ geographic_targeting }}` | optional | Countries, regions, cities, or markets to target or exclude. |
| Output format | `{{ output_format }}` | markdown_and_csv | Controls whether to emit markdown only or markdown plus CSV. |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search | Tool | Yes | Research Meta audience options, competitor ads, and relevant interests. |
| Meta Ad Library | Website | Optional | Public competitor ad research when competitors are provided. |
| Python 3 | Runtime | Yes | Used for final output validation and JSON/CSV checks. |
| CSV writer | Python stdlib | Yes | Produces `campaign_structure.csv` without hand-formatted CSV errors. |

## Step 1: Environment Setup

1. Create the results directory.
2. Validate required parameters are present: product name, product URL, objective, ICP, monthly budget, landing pages, and business type.
3. Normalize the objective to one of `awareness`, `traffic`, `lead_generation`, `conversions`, or `app_installs`.
4. Initialize `validation_report.json` with a `setup` stage.

```bash
mkdir -p "{{ results_dir }}"
python - <<'PY'
import json, os, pathlib
results = pathlib.Path(os.environ.get('RESULTS_DIR', '{{ results_dir }}'))
results.mkdir(parents=True, exist_ok=True)
required = ['product_name', 'product_url', 'campaign_objective', 'icp', 'monthly_budget', 'landing_pages', 'business_type']
missing = [name for name in required if not os.environ.get(name.upper())]
report = {'version':'1.0.0','stages':[{'name':'setup','passed':not missing,'message':'Missing: '+', '.join(missing) if missing else 'Required inputs present'}]}
(results / 'validation_report.json').write_text(json.dumps(report, indent=2))
if missing:
    raise SystemExit(1)
PY
```

## Step 2: Intake and Objective Selection

Collect or confirm the campaign intake:

| Intake Field | Required Decision |
|---|---|
| Product name and URL | What is being advertised and where users land. |
| Campaign objective | Awareness, traffic, lead generation, conversions, or app installs. |
| ICP | Role, firmographics or demographics, pain points, buying triggers, exclusions. |
| Monthly Meta budget | Determines ad set count, daily budget, and testing scope. |
| Landing pages | Determines conversion event and copy promise. |
| Tracking status | Determines whether conversion optimization is viable at launch. |
| B2B or B2C | Determines targeting precision and retargeting emphasis. |

Select the Meta objective using this mapping:

| Business Goal | Meta Objective | Why |
|---|---|---|
| Get demos or leads | Lead Generation or Conversions | Lead forms produce more volume; website conversions usually produce stronger qualification. |
| Drive free trial sign-ups | Conversions | Optimize to the on-site conversion event. |
| Build launch awareness | Awareness | Maximize reach in the chosen market. |
| Retarget visitors | Conversions | Bring warm traffic back to convert. |
| Promote content | Traffic | Optimize for clicks to a resource or blog. |

Write the selected objective and rationale into `meta_campaign_plan.md`.

## Step 3: Research Audiences and Competitors

Run bounded research for targeting and messaging. Use max 3 rounds: one round for product/category targeting, one for ICP-specific interests or behaviors, and one for competitor Meta Ad Library findings when competitor names are available.

Suggested searches:

```text
[product category] Meta Ads targeting options
[ICP role] Facebook ad audience interests
site:facebook.com/ads/library "[competitor name]"
"[competitor name]" Meta Ads examples
```

Capture only findings that directly change audience selection, exclusions, placements, or copy angles. For B2B campaigns, prefer customer-list lookalikes and retargeting where possible; Meta job-title targeting can be incomplete and should be treated as a weak signal.

## Step 4: Build Campaign Architecture

Design the campaign tree with enough consolidation to exit learning phase where possible.

```text
Campaign: [Product Name] - [Objective]
- Ad Set 1: Prospecting - Interest-Based
  - Ad 1: Pain angle
  - Ad 2: Outcome angle
  - Ad 3: Product-led angle
- Ad Set 2: Prospecting - Lookalike
  - Ad 1-3: Same creative variants adapted to lookalike audience
- Ad Set 3: Retargeting - Website Visitors
  - Ad 1-3: Retargeting-specific proof and urgency
- Ad Set 4: Retargeting - Engagement
  - Ad 1-3: Engagement retargeting creative
```

Use these audience size and structure rules:

| Campaign Condition | Recommendation |
|---|---|
| Prospecting audience | Target roughly 500K-2M where the market allows it. |
| Budget cannot support 50 conversions per ad set per week | Consolidate ad sets or optimize to an earlier funnel event. |
| Customer list exists | Build 1% lookalike as the strongest cold audience. |
| Pixel has converter history | Build 1% converter lookalike and website retargeting. |
| B2B precision is critical | Use Meta for retargeting and awareness; document limits clearly. |

## Step 5: Generate Copy Framework and Budget Plan

For each ad set, generate 3-5 copy variants using these angles: pain, outcome, social proof, contrarian, and product-led. Include placement-specific guidance for Feed, Stories, Reels, Right Column, and Audience Network.

Budget allocation:

| Budget Tier | Prospecting | Retargeting | Testing |
|---|---:|---:|---:|
| Less than $1K/mo | 60% | 30% | 10% |
| $1K-5K/mo | 50% | 30% | 20% |
| $5K+/mo | 45% | 25% | 30% |

Bidding guidance:

| Objective | Starting Bid Strategy | Switch Criteria |
|---|---|---|
| Conversions | Lowest Cost | Consider Cost Cap after about 50 conversions. |
| Lead Generation | Lowest Cost | Usually sufficient for lead forms. |
| Traffic | Lowest Cost per Click | Keep setup simple. |
| Awareness | Lowest Cost per 1K impressions | Maximize reach. |

## Step 6: Write Outputs

Write `meta_campaign_plan.md` with this structure:

1. Campaign Overview
2. Campaign Structure
3. Audience Targeting
4. Ad Copy
5. Budget and Bidding
6. Tracking Setup Checklist
7. Launch Checklist
8. Week 1-2 Monitoring Plan
9. Assumptions and Risks

Write `campaign_structure.csv` with columns:

```text
campaign_name,objective,ad_set_name,audience_type,audience_definition,placements,daily_budget,bid_strategy,ad_variant,copy_angle,primary_text,headline,description,cta,landing_page
```

Use a structured CSV writer rather than manual comma-separated text.

## Step 7: Evaluate Outputs

Run programmatic checks and update `validation_report.json`:

| Check | Pass Criteria |
|---|---|
| Required files | `meta_campaign_plan.md`, `campaign_structure.csv`, `summary.md`, and `validation_report.json` exist and are non-empty. |
| Campaign overview | Includes objective, monthly budget, target audience, placements, and conversion event or tracking note. |
| Audience strategy | Includes prospecting and retargeting, or explains why one is omitted. |
| Copy variants | Includes at least 3 variants for the primary ad set. |
| Budget plan | Includes allocation and bidding strategy. |
| CSV structure | CSV parses and includes the required header columns. |

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails or finds partial coverage, perform up to max 3 rounds of targeted fixes. Fix missing files first, then missing sections, then weak assumptions or unsupported recommendations. Stop early once all required checks pass.

### Common Fixes

| Issue | Fix |
|---|---|
| Campaign plan missing required section | Insert the missing heading and fill it from the intake and research notes. |
| CSV does not parse | Re-write it with Python `csv.DictWriter`. |
| Retargeting omitted | Add retargeting or explicitly explain why no warm audience exists. |
| Budget split inconsistent with monthly budget | Recalculate daily budgets from monthly budget divided by 30.4. |
| Tracking setup unclear | Add Pixel, Conversions API, UTM, custom audience, and test-conversion checklist items. |

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{ results_dir }}"
for f in   "$RESULTS_DIR/meta_campaign_plan.md"   "$RESULTS_DIR/campaign_structure.csv"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'PY'
import csv, json, os, pathlib, sys
results = pathlib.Path(os.environ.get('RESULTS_DIR', '{{ results_dir }}'))
required = ['campaign_name','objective','ad_set_name','audience_type','audience_definition','placements','daily_budget','bid_strategy','ad_variant','copy_angle','primary_text','headline','description','cta','landing_page']
with (results / 'campaign_structure.csv').open(newline='') as fh:
    reader = csv.DictReader(fh)
    missing = [c for c in required if c not in (reader.fieldnames or [])]
    rows = list(reader)
if missing or not rows:
    print('FAIL: campaign_structure.csv missing columns or rows')
    sys.exit(1)
report = json.loads((results / 'validation_report.json').read_text())
if not report.get('overall_passed', False):
    print('FAIL: validation_report.json overall_passed is not true')
    sys.exit(1)
print('PASS: structured outputs validated')
PY
```

## Tips

- Do not treat boosted posts as a campaign plan; build objective, audience, placement, copy, budget, tracking, and testing structure together.
- For small budgets, fewer larger ad sets usually beat many narrow ad sets because the learning phase needs enough conversion volume.
- For B2B campaigns, document Meta targeting uncertainty and lean on customer lists, website retargeting, and lookalikes when available.
- Use competitor ads as directional messaging input, not as copy to duplicate.
