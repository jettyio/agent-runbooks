---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-package-notion/SKILL.md"
  source_host: "github.com"
  source_title: "create-client-package-notion"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "client-package-notion"
    confidence: "high"
---

# create-client-package-notion — Agent Runbook

## Objective

Package all GTM work done for a client into a structured, shareable Notion page with subpages and linked Google Sheets. The agent reads the client's workspace folder (strategies, campaigns, content, leads, notes) and builds a navigable delivery package. Lead list CSVs are uploaded to Google Sheets and linked from the Notion pages. Use this runbook when you want to deliver client work in a polished, navigable format that the client can browse directly in Notion.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`. The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/notion_package_url.txt` | The top-level Notion page URL created for the client |
| `/app/results/subpages.json` | JSON list of all subpage titles and URLs created |
| `/app/results/google_sheets.json` | JSON list of Google Sheet titles and URLs for lead lists |
| `/app/results/summary.md` | Executive summary with run metadata, pages created, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `client_name` | *(required)* | Client folder name under `clients/` (e.g., `truewind`) |
| `intro_message` | *(none)* | Custom introduction message for the top-level page. If not provided, generate a professional intro based on the assets found. |
| `recipient_name` | *(none)* | Name of the person receiving the package (used in intro) |
| `recipient_context` | *(none)* | Any framing context for the delivery (e.g., "we built these to capitalize on the Botkeeper shutdown") |
| `include_strategies` | `true` | Whether to include strategy documents |
| `include_campaigns` | `true` | Whether to include campaign assets |
| `include_content` | `true` | Whether to include content drafts |
| `include_leads` | `true` | Whether to include lead lists (uploaded to Google Sheets) |
| `include_conference_speakers` | `true` | Whether to include conference speaker data |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Notion MCP server | MCP | Yes | For creating pages and subpages in Notion |
| Rube MCP server | MCP | Yes | For creating Google Sheets via Composio GOOGLESHEETS tools |
| `clients/<client_name>/` folder | Filesystem | Yes | The client workspace folder containing strategies, campaigns, content, leads |

No API keys need to be set manually — both Notion and Google Sheets are accessed through MCP.

## Step 1: Environment Setup

Verify required MCP connections are active before proceeding.

```python
# Confirm MCP server availability
# Check Notion MCP is connected by attempting a lightweight API call
# Check Rube MCP is connected for Google Sheets access

import os, pathlib

client_name = os.environ.get("CLIENT_NAME", "")
if not client_name:
    raise ValueError("CLIENT_NAME is required. Set it before running this runbook.")

client_dir = pathlib.Path(f"clients/{client_name}")
if not client_dir.exists():
    raise FileNotFoundError(f"Client directory not found: {client_dir}")

results_dir = pathlib.Path("/app/results")
results_dir.mkdir(parents=True, exist_ok=True)

print(f"Client: {client_name}")
print(f"Client folder: {client_dir} (exists: {client_dir.exists()})")
```

If either MCP server is unavailable, fail fast:
- **Notion MCP missing**: Run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["notion"]` to reconnect, or check MCP server config.
- **Rube MCP missing**: Run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]` to reconnect.

## Step 2: Scan the Client Folder

Read the client folder at `clients/<client_name>/` and inventory all available assets.

```
clients/<client_name>/
├── context.md          # Client context, ICP, positioning
├── competitors.md      # Competitive landscape (optional)
├── notes.md            # Running log of decisions
├── strategies/         # Strategy documents (*.md)
├── campaigns/          # Campaign assets (folders or *.md)
├── content/            # Content drafts (blog posts, comparison pages, etc.)
└── leads/              # Lead lists (*.csv and *.md)
```

For each directory, list all files and read their contents. Build an inventory:

- **Strategies:** List of `.md` files in `strategies/` (skip orchestration prompts or internal-only files)
- **Campaigns:** List of campaign folders or `.md` files in `campaigns/`
- **Content:** List of `.md` files in `content/`
- **Leads:** List of `.csv` files (for Google Sheets upload) and `.md` files (for Notion pages) in `leads/`

If a directory doesn't exist or is empty, skip it in the output. Log the inventory to the console before proceeding.

## Step 3: Upload Lead Lists to Google Sheets

For each `.csv` file found in `leads/` (run in parallel where possible):

1. **Create a new Google Sheet** using `GOOGLESHEETS_CREATE_GOOGLE_SHEET1`
   - Title format: `<Client Name> — <Lead List Name>` (derive from filename)
   - Example: `Truewind — Botkeeper LinkedIn Leads`

2. **Parse the CSV** and write data using `GOOGLESHEETS_BATCH_UPDATE`
   - First row = headers
   - Remaining rows = data
   - Use `first_cell_location: "A1"` and `valueInputOption: "USER_ENTERED"`

3. **Record the spreadsheet URL** for linking in Notion pages later

If there are no CSVs, skip this step and note it in the summary.

## Step 4: Plan the Notion Page Structure

Design the page hierarchy based on what assets exist. The general pattern is:

```
Top-Level Page: "<Client Name> — GTM Engineering Package"
├── Introduction (on the top-level page itself)
├── Strategies (subpage — all strategy docs combined or as separate child pages)
├── <Signal-Specific Section> (subpage — groups campaigns + content for a specific signal)
│   ├── Campaign 1 (subpage)
│   ├── Campaign 2 (subpage)
│   ├── Content Asset 1 (subpage)
│   └── Content Asset 2 (subpage)
├── Conference Speakers (subpage — if speaker data exists)
└── Lead Lists (linked as Google Sheets from relevant pages)
```

**Grouping logic:**
- If campaigns and content assets share a common theme, group them under a themed section
- If campaigns are standalone, list them at the top level
- Lead list Google Sheet links should appear on the pages where they're most relevant
- Conference/speaker data gets its own top-level subpage

**When assets don't fit a theme:** Create a "Campaigns" subpage and a "Content" subpage as catch-all sections.

Present the planned structure to the user and confirm before creating pages.

## Step 5: Create the Top-Level Notion Page

Create a standalone workspace-level page with:

**Title:** `<Client Name> — GTM Engineering: Growth Strategies & Execution`

**Content:** An introduction section that includes:
- A greeting to the recipient (if `recipient_name` provided)
- A summary of what's inside (list the sections with brief descriptions)
- Links to the Google Sheets with lead lists
- Any framing context from `recipient_context`
- A closing line

If `intro_message` is provided, use it verbatim. Otherwise, generate a professional intro based on what asset types exist and key themes inferred from filenames.

Use Notion-flavored Markdown. Do NOT include the page title in the content (Notion renders it automatically).

## Step 6: Create Subpages

For each section in the planned structure, create subpages under the top-level page. Create pages in batches where possible (max 3 rounds of batch creation if API errors occur).

**For strategy documents:**
- Read the full `.md` content from the file
- Convert to Notion-flavored Markdown (adjust table syntax, escape special characters)
- Create as a subpage with the strategy title

**For campaign documents:**
- Read the full `.md` content
- Insert Google Sheet links where lead lists are referenced
- Create as a subpage

**For content assets (blog posts, comparison pages):**
- Read the full `.md` content
- Create as a subpage with the article title

**For grouped sections:**
- Create a parent subpage with a summary/index of what's inside
- Create child subpages under the parent for each individual asset
- Link relevant Google Sheets from the parent summary

### Notion Markdown Notes

- **Tables:** Standard markdown tables (`| col | col |`) work in Notion
- **Escape special characters:** `\* \~ \` \$ \[ \] \< \> \{ \} \| \^`
- **Links:** Standard markdown `[text](url)` works
- **No H1 in content:** Start content at H2 or below (page title is rendered automatically)
- **Empty lines:** Use `<empty-block/>` for intentional blank lines
- **Code blocks:** Do NOT escape characters inside code blocks

## Step 7: Iterate on Errors (max 3 rounds)

If any page creation fails:

1. Check the specific Notion API error
2. Apply the fix from the Common Fixes table below
3. Retry the failed page creation
4. Repeat up to 3 times total

After 3 rounds of retries for a given page, log the failure and skip it — include it in the summary as a failed page.

### Common Fixes

| Problem | Solution |
|---------|----------|
| Notion page creation fails | Check that the Notion MCP server is connected. Try creating a simple test page first. |
| Google Sheets creation fails | Verify the Rube MCP server is connected. Run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]`. |
| CSV parsing errors | Check the CSV for encoding issues. The skill expects UTF-8 CSVs with a header row. |
| Notion content looks wrong | Review Notion-flavored Markdown spec. Common issues: unescaped special characters, H1 in content, or raw HTML. |
| Too many pages to create | Notion API supports batch page creation (up to 100 pages per call with shared parent). Group subpages by parent. |
| Lead list is empty or malformed | Skip that CSV and note it in the summary. Don't create an empty Google Sheet. |

## Step 8: Verify and Write Output Files

After all pages are created, collect results and write output files.

```python
import json, pathlib

results_dir = pathlib.Path("/app/results")

# Write notion_package_url.txt
notion_top_url = "<top-level-page-url>"  # Replace with actual URL
(results_dir / "notion_package_url.txt").write_text(notion_top_url)

# Write subpages.json
subpages = [
    {"title": "<subpage-title>", "url": "<subpage-url>"},
    # ... one entry per subpage created
]
(results_dir / "subpages.json").write_text(json.dumps(subpages, indent=2))

# Write google_sheets.json
google_sheets = [
    {"title": "<sheet-title>", "url": "<sheet-url>", "lead_count": 0},
    # ... one entry per sheet created
]
(results_dir / "google_sheets.json").write_text(json.dumps(google_sheets, indent=2))
```

Print a summary to console:

```
## Package Created

**Top-level page:** [<title>](<notion-url>)

**Subpages:**
- [Strategies](<url>) — 2 strategy documents
- [Campaigns](<url>) — N campaign assets
- [Conference Speakers](<url>)

**Google Sheets:**
- [Lead List 1](<sheets-url>) — 12 leads
- [Lead List 2](<sheets-url>) — 9 leads

**Total:** X pages created, Y Google Sheets created
```

## Step 9: Write Summary and Validation Report

Write `/app/results/summary.md` and `/app/results/validation_report.json`.

```python
import json, pathlib
from datetime import datetime, timezone

results_dir = pathlib.Path("/app/results")
now = datetime.now(timezone.utc).isoformat()

# summary.md
summary = f"""# create-client-package-notion — Run Summary

## Overview
- **Date**: {now}
- **Client**: <client_name>
- **Top-level Notion page**: <notion-url>
- **Subpages created**: <count>
- **Google Sheets created**: <count>

## Steps Completed

| Stage | Status | Notes |
|---|---|---|
| Environment setup | PASS | Client folder found |
| Asset scan | PASS | Inventoried N assets |
| Google Sheets upload | PASS | N CSVs uploaded |
| Notion page plan | PASS | Structure confirmed |
| Top-level page creation | PASS | Page URL: <url> |
| Subpage creation | PASS | N pages created |
| Output files written | PASS | All files present |

## Issues / Manual Follow-up
- <Note any skipped files or failed pages here>

## Provenance
- Origin: https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-package-notion/SKILL.md
- Imported by: skill-to-runbook-converter v1.0.0
"""
(results_dir / "summary.md").write_text(summary)

# validation_report.json
report = {
    "version": "1.0.0",
    "run_date": now,
    "parameters": {
        "skill_url": "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-package-notion/SKILL.md",
        "target_repo": "jettyio/agent-runbooks",
        "base_branch": "main",
        "dry_run": False
    },
    "stages": [
        {"name": "setup", "passed": True, "message": "Environment ready, MCP servers verified"},
        {"name": "asset_scan", "passed": True, "message": "Client folder scanned successfully"},
        {"name": "google_sheets_upload", "passed": True, "message": "Lead CSVs uploaded to Google Sheets"},
        {"name": "notion_page_plan", "passed": True, "message": "Page structure planned and confirmed"},
        {"name": "top_level_page", "passed": True, "message": "Top-level Notion page created"},
        {"name": "subpage_creation", "passed": True, "message": "All subpages created"},
        {"name": "output_files", "passed": True, "message": "All output files written"}
    ],
    "results": {"pass": 7, "partial": 0, "fail": 0},
    "overall_passed": True,
    "output_files": [
        "/app/results/notion_package_url.txt",
        "/app/results/subpages.json",
        "/app/results/google_sheets.json",
        "/app/results/summary.md",
        "/app/results/validation_report.json"
    ]
}
(results_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
print("Output files written.")
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/notion_package_url.txt" \
  "$RESULTS_DIR/subpages.json" \
  "$RESULTS_DIR/google_sheets.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Sanity-check the Notion URL
NOTION_URL=$(cat "$RESULTS_DIR/notion_package_url.txt" 2>/dev/null || echo "")
case "$NOTION_URL" in
  https://www.notion.so/*|https://notion.so/*) echo "PASS: Notion URL well-formed: $NOTION_URL" ;;
  *) echo "WARN: Notion URL may not be well-formed: $NOTION_URL" ;;
esac
```

### Checklist

- [ ] `notion_package_url.txt` exists and contains the top-level Notion page URL
- [ ] `subpages.json` exists and lists all created subpages with URLs
- [ ] `google_sheets.json` exists and lists all created Google Sheets with URLs
- [ ] `summary.md` exists and describes the run outcome
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Notion batching:** Create pages in batches grouped by parent to minimize API calls. The Notion API supports up to 100 pages per call when they share a parent.
- **Google Sheets parallelism:** If there are multiple CSV files, create all Google Sheets in parallel before starting any Notion page creation so all sheet URLs are ready to embed.
- **Grouping heuristic:** Use campaign and content filenames to detect themes. If two or more files share a keyword (e.g., "botkeeper"), group them under a themed section.
- **Intro generation:** When `intro_message` is not provided, synthesize the intro from the asset inventory — mention how many strategies, campaigns, content pieces, and leads were included.
- **No H1 in Notion content:** Always start Notion page content with H2 or lower. The page title property renders as H1 automatically.
- **MCP reconnection:** If `RUBE_MANAGE_CONNECTIONS` fails, check that the Composio GOOGLESHEETS toolkit has an active OAuth connection in the Rube dashboard.
- **CSV encoding:** Expect UTF-8 with a header row. If a CSV fails to parse, log it and skip rather than aborting the entire run.
