---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/vercel-labs/skills/find-skills"
  source_host: "skills.sh"
  source_title: "Find Skills"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "vercel-labs"
    skill_name: "find-skills"
    confidence: "high"
---

# Find Skills — Agent Runbook

## Objective

This runbook enables an agent to help users discover and install skills from the open agent skills ecosystem. When a user asks "how do I do X", "find a skill for X", or expresses interest in extending agent capabilities, the agent searches the Skills CLI index and leaderboard, verifies quality signals (install count, source reputation, GitHub stars), and presents the best options with install commands. The agent also offers to install the selected skill immediately via `npx skills add`. If no matching skill is found, the agent helps directly and suggests `npx skills init` for custom skill creation.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata, search query, recommended skills, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/search_results.json` | Raw output from `npx skills find [query]` plus quality-verification metadata |
| `/app/results/recommendation.md` | Formatted skill recommendation(s) ready to present to the user |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Search query | *(required — from user request)* | Keywords describing the capability the user needs |
| Min install threshold | `1000` | Minimum install count to recommend without explicit caveat |
| Max results to present | `3` | Maximum number of skill options to present to the user |
| Global install flag | `true` | Whether to install with `-g` (user-level) flag |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npm` | Runtime | Yes | Required to run `npx skills` commands |
| `npx skills` | CLI | Yes | The Skills CLI — package manager for the agent skills ecosystem |
| `curl` | CLI | Optional | Used as a fallback to query the skills.sh API directly |
| `jq` | CLI | Optional | Parse JSON output from skills commands |
| Internet access | External | Yes | Must be able to reach `skills.sh` and `github.com` |

## Step 1: Environment Setup

Verify the environment can reach the Skills CLI and understand the user's intent.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify node/npx is available
command -v node >/dev/null || { echo "ERROR: node not found — install Node.js"; exit 1; }
command -v npx  >/dev/null || { echo "ERROR: npx not found — install Node.js"; exit 1; }

# Verify network access to skills.sh
curl -sf --max-time 10 https://skills.sh/ > /dev/null || echo "WARNING: skills.sh unreachable — results may be limited"

# Create output directory
mkdir -p /app/results

echo "Environment ready."
```

Record the user's original request verbatim in `/app/results/summary.md` before proceeding.

## Step 2: Understand What the User Needs

Analyze the user's request to identify:

1. **Domain** — e.g., React, testing, design, deployment, documentation
2. **Specific task** — e.g., writing tests, creating changelogs, reviewing PRs
3. **Search keywords** — derive 1–3 keyword phrases to feed into `npx skills find`

Write the derived keywords to `/app/results/work/search_keywords.txt`, one phrase per line.

```python
# Derive search keywords from the user's request
user_request = "<user's original question>"

# Example mapping:
# "how do I make my React app faster?" -> ["react performance", "react optimization"]
# "can you help me with PR reviews?"   -> ["pr review", "code review"]
# "I need to create a changelog"       -> ["changelog", "release notes"]

keywords = []  # populate from user request analysis
with open("/app/results/work/search_keywords.txt", "w") as f:
    f.write("\n".join(keywords))
```

## Step 3: Check the Leaderboard First

Before running a CLI search, consult the skills.sh leaderboard to see if a well-known skill covers the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

Known top-tier skill sources (100K+ installs):
- `vercel-labs/agent-skills` — React, Next.js, web design
- `anthropics/skills` — Frontend design, document processing
- `ComposioHQ/awesome-claude-skills` — Broad ecosystem catalog

If the domain matches a known leaderboard skill, record it as a candidate in `/app/results/work/leaderboard_candidates.json` and skip to Step 5.

## Step 4: Search for Skills

Run the find command for each keyword phrase derived in Step 2. Capture full output.

```bash
mkdir -p /app/results/work
KEYWORDS_FILE="/app/results/work/search_keywords.txt"
RESULTS_FILE="/app/results/search_results.json"

echo '{"queries": [], "raw_results": []}' > "$RESULTS_FILE"

while IFS= read -r kw; do
  echo "Searching: $kw"
  result=$(npx skills find "$kw" --json 2>/dev/null || npx skills find "$kw" 2>&1)
  # Append result per keyword (jq merge or simple append)
  echo "{\"keyword\": \"$kw\", \"output\": $(echo "$result" | jq -Rs .)}" \
    >> /app/results/work/raw_search.jsonl
done < "$KEYWORDS_FILE"
```

If `npx skills find` does not support `--json`, capture plain text output and parse skill names, descriptions, and install counts with regex.

## Step 5: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** For each candidate skill, verify:

| Signal | Threshold | Action if below |
|--------|-----------|-----------------|
| Install count | ≥ 1,000 | Add caveat: "relatively new skill" |
| Source reputation | Known org (`vercel-labs`, `anthropics`, `microsoft`) | Flag as unverified source |
| GitHub stars on source repo | ≥ 100 | Treat with skepticism; note in recommendation |

```bash
# For each candidate, check GitHub stars (optional but recommended)
OWNER_REPO="<owner>/<repo>"
STARS=$(gh api repos/"$OWNER_REPO" --jq '.stargazers_count' 2>/dev/null || echo "unknown")
echo "Stars for $OWNER_REPO: $STARS"
```

Write quality-annotated candidates to `/app/results/search_results.json`:

```json
{
  "queries": ["<keyword1>", "<keyword2>"],
  "candidates": [
    {
      "skill": "<owner/repo@skill-name>",
      "description": "...",
      "install_count": 185000,
      "source_org": "vercel-labs",
      "github_stars": 4200,
      "quality_tier": "high",
      "caveats": []
    }
  ]
}
```

## Step 6: Iterate on Errors (max 3 rounds)

If `npx skills find` fails or returns no results:

1. **Round 1**: Try alternative keywords (synonyms, broader terms)
2. **Round 2**: Query `https://skills.sh/` directly with `curl` and parse the leaderboard HTML for matching skills
3. **Round 3**: Acknowledge no skill was found; go to Step 7 (no-results path)

Track iteration count in `/app/results/work/iteration_count.txt`. After 3 rounds, do not retry — proceed with the best available result or the no-results path.

```bash
ROUND=$(cat /app/results/work/iteration_count.txt 2>/dev/null || echo 0)
ROUND=$((ROUND + 1))
echo "$ROUND" > /app/results/work/iteration_count.txt
if [ "$ROUND" -gt 3 ]; then
  echo "Max iterations reached — proceeding with best available results"
fi
```

## Step 7: Present Options or Handle No-Results

### If skills were found

Write the formatted recommendation to `/app/results/recommendation.md`:

```markdown
I found skills that might help!

### Option 1: `<owner/repo@skill-name>`
**What it does**: <description>
**Installs**: <count> | **Source**: <org> | **Quality**: <tier>

To install:
\`\`\`bash
npx skills add <owner/repo@skill-name>
\`\`\`

Learn more: https://skills.sh/<owner>/<repo>/<skill-name>
```

Present at most `3` options, ordered by quality tier then install count descending.

### If no skills were found

Write to `/app/results/recommendation.md`:

```markdown
I searched for skills related to "<query>" but didn't find any strong matches.

I can still help you with this task directly using my general capabilities.

If you do this often, you could create your own skill:
\`\`\`bash
npx skills init my-<query>-skill
\`\`\`
```

### Offer to install

If the user selects a skill, install it:

```bash
npx skills add <owner/repo@skill-name> -g -y
```

## Step 8: Write Executive Summary

Write `/app/results/summary.md` with:

```markdown
# Find Skills — Run Summary

## Overview
- **Date**: <run date>
- **User request**: <original request>
- **Search keywords**: <keyword1>, <keyword2>
- **Skills found**: <count>
- **Top recommendation**: <skill or "none">

## Search & Validation

| Stage | Status | Notes |
|---|---|---|
| Environment setup | ... | ... |
| Keyword extraction | ... | ... |
| Leaderboard check | ... | ... |
| CLI search | ... | ... |
| Quality verification | ... | ... |
| Recommendation | ... | ... |

## Issues / Manual Follow-up
- <Any skills below quality threshold>
- <Any search failures>
- <Any unresolved ambiguity in user intent>

## Provenance
- Origin: https://skills.sh/vercel-labs/skills/find-skills
- Imported by: skill-to-runbook-converter v1.0.0
```

## Step 9: Write Validation Report

Write `/app/results/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601>",
  "parameters": {
    "search_query": "<query>",
    "min_install_threshold": 1000,
    "max_results": 3
  },
  "stages": [
    { "name": "setup",                "passed": true,  "message": "Node/npx available, network reachable" },
    { "name": "keyword_extraction",   "passed": true,  "message": "Derived N keywords from user request" },
    { "name": "leaderboard_check",    "passed": true,  "message": "Leaderboard consulted" },
    { "name": "cli_search",           "passed": true,  "message": "Found N candidates" },
    { "name": "quality_verification", "passed": true,  "message": "All candidates above threshold" },
    { "name": "recommendation",       "passed": true,  "message": "Recommendation written" },
    { "name": "report_generation",    "passed": true,  "message": "All output files written" }
  ],
  "results": {
    "pass": 7,
    "partial": 0,
    "fail": 0
  },
  "overall_passed": true,
  "output_files": [
    "/app/results/summary.md",
    "/app/results/validation_report.json",
    "/app/results/search_results.json",
    "/app/results/recommendation.md"
  ]
}
```

## Step 10: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/search_results.json" \
  "$RESULTS_DIR/recommendation.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify overall_passed
PASSED=$(jq -r .overall_passed "$RESULTS_DIR/validation_report.json" 2>/dev/null)
if [ "$PASSED" = "true" ]; then
  echo "PASS: validation_report.json overall_passed=true"
else
  echo "FAIL: validation_report.json overall_passed is not true"
fi
```

### Checklist

- [ ] `summary.md` exists and records the user's original request and the top recommendation
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `search_results.json` contains quality-annotated candidates (or empty array if none found)
- [ ] `recommendation.md` exists and contains at least one option or the no-results message
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer the leaderboard for common domains.** Check skills.sh visually before running CLI searches — popular skills are usually immediately visible in the top listings.
- **Use specific keywords.** "react testing" outperforms "testing" because it narrows results to the relevant ecosystem.
- **Try alternative terms.** If "deploy" returns nothing, try "deployment", "ci-cd", or "devops".
- **Always verify install count.** A skill with fewer than 100 installs has had little community validation — flag this clearly to the user.
- **Offer `npx skills init` proactively.** When no skill exists for a user's niche workflow, suggesting skill creation turns a dead end into an opportunity.
- **The `-g -y` flags.** `-g` installs at the user level (not project-local) and `-y` skips interactive prompts — always use both unless the user specifically asks for a project-local install.

## Common Fixes

| Issue | Fix |
|-------|-----|
| `npx skills find` returns no output | Check internet connectivity; try `curl -sf https://skills.sh/` |
| `npx skills` not found | Install Node.js: `brew install node` or `apt-get install nodejs npm` |
| All candidates below install threshold | Lower threshold for niche domains; present with explicit caveat |
| GitHub stars lookup fails | `gh` CLI not authenticated or rate-limited; skip stars check and note in report |
| User intent ambiguous | Ask one clarifying question before running searches |
