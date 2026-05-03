---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/battlecard-generator/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/battlecard-generator
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Battlecard Generator
  imported_at: '2026-05-03T02:53:56Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: battlecard-generator
    confidence: high
secrets: {}
---

# Battlecard Generator — Agent Runbook

## Objective

Research one named competitor across public website messaging, reviews, ads, social/community signals, and pricing, then produce an opinionated sales battlecard for competitive deals. The battlecard should help a rep understand where to lead, where not to engage, which landmine questions to ask, and how to handle common objections. This runbook is adapted from the upstream `battlecard-generator` skill and preserves its phase structure while adding Jetty output, validation, and provenance requirements.

Source description: Research a specific competitor across their website, reviews, ads, social presence, and pricing — then produce a structured sales battlecard with positioning traps, objection handlers, landmine questions, and win/loss themes. Chains web research, review mining, and ad intelligence. Use when sales needs competitive ammo or when entering a new market with established incumbents.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/battlecard.md` | Final structured battlecard for the specified competitor |
| `/app/results/research_notes.md` | Notes from website, review, ad, social, and pricing research |
| `/app/results/evidence.json` | Structured evidence with URLs, claims, confidence, and timestamps |
| `/app/results/summary.md` | Executive summary of findings, strongest win themes, and caveats |
| `/app/results/validation_report.json` | Structured validation results with stages, counts, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Output directory for all required artifacts |
| Your product name | required | Product being positioned against the competitor |
| Your product URL | required | Website or canonical product page for your product |
| Competitor name | required | One competitor per run |
| Competitor URL | required | Competitor homepage or product page |
| Deal context | optional | ICP, segment, use case, and where the products overlap |
| Known win/loss signals | optional | Existing patterns from deals won or lost against this competitor |
| Sales team size | optional | Audience and language level for the battlecard |
| Existing positioning | optional | Current one-line positioning versus the competitor |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web search | Tool | Yes | Discover competitor messaging, reviews, ads, comparisons, social posts, and pricing context |
| Web fetch | Tool | Yes | Read competitor pages and source evidence |
| `review-site-scraper` | Skill/tool | Optional | Mine G2, Capterra, or similar reviews when available |
| `google-ad-scraper` | Skill/tool | Optional | Collect ad intelligence when available |
| Markdown writer | Runtime | Yes | Write the battlecard and research notes to `/app/results` |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Verify the required inputs are present: your product name, your product URL, competitor name, and competitor URL.
3. Initialize `research_notes.md`, `evidence.json`, `battlecard.md`, `summary.md`, and `validation_report.json`.
4. Record the run timestamp and the public URLs that will be researched.

## Step 2: Intake

Collect and normalize:

- Your product name and URL.
- Competitor name and URL.
- Deal context, including ICP overlap, segment, and competing use cases.
- Known win/loss signals.
- Sales audience details, including whether reps are technical or business-focused.
- Existing one-line positioning, if available.

If a required input is missing, stop before research and write `validation_report.json` with `overall_passed=false`.

## Step 3: Competitor Research

### Website & Messaging Analysis

Fetch the competitor homepage, pricing page, about page, and primary product pages. Search for positioning phrases such as `"we help"`, `"the only"`, `"unlike"`, case studies, and customer stories.

Extract the hero claim, category, target audience, emphasized features, social proof, and pricing structure.

### Review Intelligence

Search review sites and public mentions for praise, complaints, switching signals, and ICP patterns. Separate strengths that should not be attacked directly from complaints that can become positioning angles.

### Ad & Content Analysis

Search for advertisements, sponsored claims, comparison pages, alternatives pages, and recurring content themes. Record claims with source URLs and timestamps.

### Social & Community Signals

Search public communities and social platforms for complaints, feature requests, alternative-seeking posts, and sentiment patterns. Treat anecdotes as lower confidence unless corroborated.

### Pricing Deep Dive

Map pricing model, tiers, free plan, enterprise triggers, hidden costs, implementation fees, overages, and add-ons.

## Step 4: Competitive Analysis

Build a strengths and weaknesses matrix across feature areas, pricing, ease of use, support, integrations, onboarding, and strategic fit. Identify:

- Where we win and the evidence behind each win.
- Where we lose and how to avoid or reframe the issue.
- Where it is close and what narrative makes the difference.

## Step 5: Generate Battlecard

Write `/app/results/battlecard.md` with these sections:

- Quick Reference: their positioning, our counter-positioning, best-fit win/loss profiles, and best opening move.
- Competitor Overview: founding, funding, headcount, target market, pricing, and category when publicly available.
- Positioning Traps: early discovery questions that frame the evaluation in our favor.
- Landmine Questions: questions reps can ask casually that expose competitor limitations.
- Objection Handling: direct responses for pricing, maturity, feature count, customer logos, and incumbency.
- Feature Comparison: honest capability assessment with a verdict per row.
- Their Customers Say: review-based praise and complaints, clearly attributed.
- Pricing Comparison: entry price, mid-tier, enterprise, free tier, hidden costs, and attack angle.
- Win Themes and Loss Themes: patterns with evidence and mitigation.
- Quick Responses for Email/Chat: concise copy reps can reuse.

## Step 6: Iterate on Errors (max 3 rounds)

Run validation after the first draft. If required files, source citations, pricing caveats, or battlecard sections are missing, revise the artifacts and re-run validation. Stop after max 3 rounds and report any unresolved issue in `summary.md` and `validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing source URL | Add the evidence URL and timestamp to `evidence.json` and cite it in `research_notes.md` |
| Battlecard is neutral instead of opinionated | Add explicit win/loss guidance and rep-ready objection handling |
| Pricing data is stale or unavailable | State the access date and confidence level, then mark unknown fields clearly |
| Review evidence is anecdotal | Lower confidence and avoid treating a single quote as a broad market pattern |
| Required output file missing | Regenerate the missing artifact before final verification |

## Final Checklist

Before finishing:

- `/app/results/battlecard.md` is non-empty and includes Quick Reference, Positioning Traps, Landmine Questions, Objection Handling, Feature Comparison, Pricing Comparison, Win Themes, and Loss Themes.
- `/app/results/research_notes.md` contains research notes grouped by website, reviews, ads/content, social/community, and pricing.
- `/app/results/evidence.json` is valid JSON and includes source URLs for material claims.
- `/app/results/summary.md` summarizes the run, major findings, caveats, and confidence.
- `/app/results/validation_report.json` contains validation stages and `overall_passed`.

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/battlecard.md" \
  "$RESULTS_DIR/research_notes.md" \
  "$RESULTS_DIR/evidence.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python -m json.tool "$RESULTS_DIR/evidence.json" >/dev/null
python -m json.tool "$RESULTS_DIR/validation_report.json" >/dev/null
```

## Source Procedure Preserved

### Source: Phase 0: Intake

1. **Your product name + URL**
2. **Competitor name + URL** — One competitor per battlecard (focused > broad)
3. **Deal context** — Where do you compete? (same ICP, upmarket/downmarket, different use case?)
4. **Known win/loss signals** — Any patterns from deals you've won or lost against them?
5. **Sales team size** — Are reps technical or business-focused? (affects language level)
6. **Existing positioning** — Your one-line positioning vs this competitor (if any)

### Source: 1A: Website & Messaging Analysis

```
Fetch: [competitor] homepage, pricing page, about page, product page
Search: "[competitor]" "we help" OR "the only" OR "unlike"
Search: "[competitor]" case study OR customer story
```

Extract:
- **Hero claim** — their primary positioning
- **Category** — what category do they place themselves in?
- **Target audience** — who do they say they serve?
- **Key features emphasized** — what do they lead with?
- **Social proof** — customer logos, metrics, quotes
- **Pricing structure** — plans, pricing model, enterprise vs self-serve

### Source: 1B: Review Intelligence

```
Search: "[competitor]" site:g2.com OR site:capterra.com
Search: "[competitor]" reviews "switched from" OR "moved to"
```

From reviews, extract:
- **Top 5 praised features** (their moat — don't compete here directly)
- **Top 5 complaints** (your attack angles)
- **Switching signals** — why do customers leave?
- **ICP patterns** — what roles/company sizes review them?

### Source: 1C: Ad & Content Analysis

```
Search: "[competitor]" advertisement OR sponsored
Search: "[competitor]" vs OR alternative OR compare
```

Extract:
- **Ad messaging** — what claims do they pay to promote?
- **Comparison pages** — have they published "us vs X" pages?
- **Content themes** — what topics do they create content around?

### Source: 1D: Social & Community Signals

```
Search: "[competitor]" site:reddit.com OR site:twitter.com complaints OR issues
Search: "[competitor]" "looking for alternative" OR "anyone use"
```

Extract:
- **Common frustrations** discussed publicly
- **Feature requests** their users are vocal about
- **Sentiment patterns** — do users love or tolerate them?

### Source: 1E: Pricing Deep Dive

```
Fetch: [competitor] pricing page
Search: "[competitor]" pricing OR cost OR "how much"
```

Map their pricing:
- **Model:** Per seat / usage-based / flat rate / hybrid
- **Tiers:** What's in each tier?
- **Free tier:** What's included? What's gated?
- **Enterprise:** Custom pricing? What triggers enterprise sales?
- **Hidden costs:** Implementation, overages, add-ons?

## Tips

- Use focused evidence from multiple public angles; a strong battlecard is not a neutral feature list.
- Lead with claims the sales team can use in live deals, and keep caveats visible where public data is incomplete.
- Save battlecards with a competitor slug and date so stale competitive intelligence is easy to identify.
