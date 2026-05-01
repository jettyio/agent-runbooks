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
    source_collection: "playbooks"
    skill_name: "client-package-notion"
    confidence: "high"
secrets:
  NOTION_MCP_TOKEN:
    env: NOTION_MCP_TOKEN
    description: "Notion MCP server authentication token"
    required: true
  RUBE_MCP_TOKEN:
    env: RUBE_MCP_TOKEN
    description: "Rube MCP server authentication token (for Google Sheets via Composio)"
    required: true
---

# create-client-package-notion — Agent Runbook

## Objective

Package all GTM (Go-To-Market) work done for a client into a structured, shareable Notion workspace with subpages and Google Sheets. The agent reads the client's workspace folder — including strategies, campaigns, content drafts, lead lists, and notes — and builds a navigable Notion delivery package the client can browse directly. Lead list CSVs are uploaded to Google Sheets and linked from the relevant Notion pages. Use this runbook when you want to deliver completed work to a client in a polished, professionally organized format.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/notion_package_url.txt` | Top-level Notion page URL shared with the client |
| `/app/results/subpage_urls.json` | JSON array of all created subpage URLs with titles |
| `/app/results/google_sheet_urls.json` | JSON array of Google Sheet URLs with lead list names and row counts |
| `/app/results/package_summary.md` | Human-readable summary of the created package (pages, sheets, totals) |
| `/app/results/summary.md` | Executive summary with run metadata and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `/app/results` | `/app/results` | Output directory for all results |
| client_name | `client_name` | *(required)* | Client folder name under `clients/` (e.g., `truewind`) |
| intro_message | `intro_message` | *(optional)* | Custom introduction message for the top-level page |
| recipient_name | `recipient_name` | *(optional)* | Name of the person receiving the package (used in intro) |
| recipient_context | `recipient_context` | *(optional)* | Any framing context for the delivery |
| include_strategies | `include_strategies` | `true` | Whether to include strategy documents |
| include_campaigns | `include_campaigns` | `true` | Whether to include campaign assets |
| include_content | `include_content` | `true` | Whether to include content drafts |
| include_leads | `include_leads` | `true` | Whether to include lead lists (uploaded to Google Sheets) |
| include_conference_speakers | `include_conference_speakers` | `true` | Whether to include conference speaker data |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Notion MCP server | MCP | Yes | For creating pages and subpages in Notion |
| Rube MCP server | MCP | Yes | For creating Google Sheets via Composio GOOGLESHEETS tools |
| `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | Tool | Yes | Composio tool to create a new Google Sheet |
| `GOOGLESHEETS_BATCH_UPDATE` | Tool | Yes | Composio tool to write data to a Google Sheet |
| `clients/<client_name>/` directory | Local filesystem | Yes | Client workspace folder with all assets |

No API keys need to be set manually — both MCP servers are accessed through the MCP protocol. Verify connections before starting.

## Step 1: Environment Setup

Verify all required services are accessible before processing.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify client folder exists
CLIENT_NAME="${client_name}"
CLIENT_DIR="clients/${CLIENT_NAME}"

if [ ! -d "$CLIENT_DIR" ]; then
  echo "ERROR: Client folder not found at $CLIENT_DIR"
  exit 1
fi

echo "Client folder found: $CLIENT_DIR"

# Create results directory
mkdir -p /app/results

# List available assets
echo "--- Assets in $CLIENT_DIR ---"
ls -la "$CLIENT_DIR"
```

Verify Notion and Rube MCP servers are connected:
- Test Notion by listing available pages or creating a simple test page
- Test Rube by calling `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]`

If either MCP server is unavailable, fail fast and write `validation_report.json` with `stages[0].passed=false`.

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

If a directory doesn't exist or is empty, skip it in the output.

Record the full inventory in memory for use in Steps 3–6.

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

If there are no CSVs, skip this step and continue.

Write results to `/app/results/google_sheet_urls.json`:
```json
[
  { "name": "Truewind — Botkeeper LinkedIn Leads", "url": "https://docs.google.com/...", "row_count": 42 }
]
```

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
- If campaigns and content assets share a common theme (e.g., "botkeeper"), group them under a themed section
- If campaigns are standalone, list them at the top level
- Lead list Google Sheet links should appear on the pages where they're most relevant
- Conference/speaker data gets its own top-level subpage

**When assets don't fit a theme:** Create a "Campaigns" subpage and a "Content" subpage as catch-all sections.

Present the planned structure to the user and confirm before creating pages.

## Step 5: Create the Top-Level Notion Page

Create a standalone workspace-level page with:

**Title:** `<Client Name> — GTM Engineering: Growth Strategies & Execution` (or similar)

**Content:** An introduction section that includes:
- A greeting to the recipient (if `recipient_name` provided)
- A summary of what's inside (list the sections with brief descriptions)
- Links to the Google Sheets with lead lists
- Any framing context from `recipient_context`
- A closing line

If `intro_message` is provided, use it as-is. Otherwise, generate a professional intro based on:
- What asset types exist (strategies, campaigns, content, leads)
- How many leads were found
- What the key themes are (inferred from strategy/campaign filenames)

Use Notion-flavored Markdown. Do NOT include the page title in the content (Notion renders it automatically).

Record the top-level page URL and write to `/app/results/notion_package_url.txt`.

## Step 6: Create Subpages

For each section in the planned structure, create subpages under the top-level page.

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

**For lead/conference data in `.md` format:**
- Read the full `.md` content
- Create as a subpage

**For grouped sections (e.g., "Botkeeper Strategies"):**
- Create a parent subpage with a summary/index of what's inside
- Create child subpages under the parent for each individual asset
- Link relevant Google Sheets from the parent summary

Create pages in batches where possible (the Notion API supports creating multiple pages in one call when they share a parent).

Iterate up to max 3 rounds if any page creation fails before reporting failure.

Write all created subpage URLs to `/app/results/subpage_urls.json`:
```json
[
  { "title": "Strategies", "url": "https://notion.so/...", "parent": "top-level" },
  { "title": "LinkedIn Engagement", "url": "https://notion.so/...", "parent": "Botkeeper Strategies" }
]
```

## Step 7: Iterate on Errors (max 3 rounds)

If any Notion page or Google Sheet creation fails:

1. Read the specific error from the API response
2. Apply the targeted fix from the Common Fixes table below
3. Retry the failed operation
4. Repeat up to 3 times total

After 3 rounds, if operations are still failing, record the failures in `summary.md` and continue with successful pages — do not abort the entire run.

### Common Fixes

| Problem | Solution |
|---------|----------|
| Notion page creation fails | Check that the Notion MCP server is connected. Try creating a simple test page first. |
| Google Sheets creation fails | Verify the Rube MCP server is connected. Run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]`. |
| CSV parsing errors | Check the CSV for encoding issues. The skill expects UTF-8 CSVs with a header row. |
| Notion content looks wrong | Review Notion-flavored Markdown spec. Common issues: unescaped special characters, H1 in content (conflicts with page title). |
| Too many pages to create | Notion API supports batch page creation (up to 100 pages per call with shared parent). Group subpages by parent and batch create. |
| Lead list is empty or malformed | Skip that CSV and note it in the summary. Don't create an empty Google Sheet. |

## Step 8: Verify and Report

After all pages are created, output a summary and write the package summary file.

Write `/app/results/package_summary.md`:

```markdown
## Package Created

**Top-level page:** [<title>](<notion-url>)

**Subpages:**
- [Strategies](<url>) — N strategy documents
- [<Signal Section>](<url>) — N assets
  - [Campaign 1](<url>)
  - [Content Asset 1](<url>)
- [Conference Speakers](<url>)

**Google Sheets:**
- [Lead List 1](<sheets-url>) — N leads
- [Lead List 2](<sheets-url>) — N leads

**Total:** X pages created, Y Google Sheets created
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/notion_package_url.txt" \
  "$RESULTS_DIR/subpage_urls.json" \
  "$RESULTS_DIR/google_sheet_urls.json" \
  "$RESULTS_DIR/package_summary.md" \
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
  https://notion.so/*|https://www.notion.so/*) echo "PASS: Notion URL well-formed: $NOTION_URL" ;;
  *) echo "WARN: notion_package_url.txt missing or not a valid notion.so URL" ;;
esac
```

### Checklist

- [ ] `notion_package_url.txt` exists and contains a valid `notion.so` URL
- [ ] `subpage_urls.json` exists and lists all created subpages
- [ ] `google_sheet_urls.json` exists (can be empty array `[]` if no lead CSVs found)
- [ ] `package_summary.md` exists with the full package breakdown
- [ ] `summary.md` exists and includes run metadata and any issues
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every line (or WARN for empty google sheets if no CSVs)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer batch page creation.** When multiple subpages share the same parent, create them in a single API call — this is significantly faster than sequential creation.
- **Notion-flavored Markdown quirks.** Do NOT include H1 (`#`) in page content bodies — Notion uses the page title property for the heading. Start content at H2 (`##`) or below.
- **Escape special characters.** When converting client `.md` files to Notion content, escape: `\* \~ \` \$ \[ \] \< \> \{ \} \| \^`
- **Group by theme, not by asset type.** Clients find themed groupings (e.g., "Botkeeper Acquisition") more useful than flat lists of "Campaigns" and "Content."
- **Google Sheets links belong near the data.** Link lead list sheets from the campaign or content pages that reference them, not just from a top-level "Leads" page.
- **Always confirm the page structure before building.** Present the planned hierarchy to the user in Step 4 and wait for approval — rebuilding Notion hierarchies after the fact is tedious.
- **Skip empty directories silently.** If a client folder has no `content/` or no `campaigns/`, skip those sections without error — not every client has every asset type.
