---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/client-package-local/SKILL.md"
  source_host: "github.com"
  source_title: "create-client-package"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "client-package-local"
    confidence: "high"
secrets: {}
---

# create-client-package — Agent Runbook

## Objective

Package all GTM work done for a client into a structured local delivery package with dated `.md` files and Google Sheets. The agent reads a client's workspace folder (strategies, campaigns, content, leads, notes) and builds a navigable directory of deliverables. Lead lists are uploaded to Google Sheets via the Rube MCP server and linked from the generated markdown files. Use this runbook to deliver polished, navigable client work packages without requiring Notion or any external CMS.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files. The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `clients/<client_name>/client-package/<date>/Overview - <date>.md` | Overview document with summary, TOC, and recipient greeting |
| `clients/<client_name>/client-package/<date>/Lead Lists - <date>.md` | Summary of all lead lists with Google Sheet links |
| `clients/<client_name>/client-package/<date>/Strategies - <date>/<Strategy>/overview.md` | Per-strategy overview (one per strategy found) |
| `clients/<client_name>/client-package/<date>/Strategies - <date>/<Strategy>/<asset> - <date>.md` | Campaign and content assets per strategy |
| `clients/<client_name>/client-package/<date>/Strategies - <date>/<Strategy>/<leads>.csv` | Lead CSV exports per strategy |
| `/app/results/summary.md` | Executive summary of the run |
| `/app/results/validation_report.json` | Structured validation results |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `client_name` | Yes | — | Client folder name under `clients/` (e.g., `truewind`) |
| `date` | No | today's date | Date string in `YYYY-MM-DD` format for folder and file naming |
| `intro_message` | No | — | Custom introduction message for the overview file; auto-generated if not provided |
| `recipient_name` | No | — | Name of the person receiving the package (used in intro) |
| `recipient_context` | No | — | Framing context for the delivery (e.g., "we built these to capitalize on the Botkeeper shutdown") |
| `include_strategies` | No | `true` | Whether to include strategy documents |
| `include_campaigns` | No | `true` | Whether to include campaign assets |
| `include_content` | No | `true` | Whether to include content drafts |
| `include_leads` | No | `true` | Whether to include lead lists (uploaded to Google Sheets) |
| Results directory | No | `/app/results` | Output directory for run-level results |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Rube MCP server | MCP | Yes | Required for Google Sheets creation and data writing via Composio GOOGLESHEETS tools |
| `company-contact-finder` | Skill | No | Lead enrichment when lead lists reference companies needing contact data |
| `setup-outreach-campaign` | Skill | No | Launch campaigns in Smartlead once client approves |
| Google Sheets write access | Credential | Yes | Provided via Rube MCP server (Composio GOOGLESHEETS); no manual API key setup needed |
| Client workspace folder | Filesystem | Yes | `clients/<client_name>/` must exist with at least one of: strategies/, campaigns/, content/, leads/ |

## Step 1: Environment Setup

Verify all required inputs and connectivity before proceeding.

```bash
# Confirm client workspace exists
CLIENT_DIR="clients/${client_name}"
if [ ! -d "$CLIENT_DIR" ]; then
  echo "ERROR: Client directory not found at $CLIENT_DIR"
  exit 1
fi

# Set date if not provided
DATE="${date:-$(date +%Y-%m-%d)}"
echo "Using date: $DATE"

# Verify Rube MCP server is reachable (use RUBE_MANAGE_CONNECTIONS to check)
# If the MCP server is unavailable, proceed without Google Sheets and note in summary

mkdir -p "/app/results"
echo "=== Environment ready ==="
echo "Client: ${client_name}"
echo "Date: ${DATE}"
echo "Results: /app/results"
```

If the Rube MCP server is unavailable, proceed through Step 2–4 to generate the directory structure, skip Step 3 (lead upload), and record a warning in `/app/results/summary.md`.

## Step 2: Scan the Client Folder

Read `clients/<client_name>/` and build a complete asset inventory.

```
clients/<client_name>/
├── context.md          # Client context, ICP, positioning
├── competitors.md      # Competitive landscape (optional)
├── notes.md            # Running log of decisions
├── strategies/         # Strategy documents (*.md)
├── campaigns/          # Campaign assets (folders or *.md)
├── content/            # Content drafts (blog posts, comparison pages, etc.)
└── leads/              # Lead lists (*.csv, *.json, *.md)
```

For each directory, list all files and read their contents. Build an inventory:

- **Strategies:** `.md` files in `strategies/` (skip `ORCHESTRATION-PROMPT.md` and other internal-only files)
- **Campaigns:** Campaign folders or `.md` files in `campaigns/`
- **Content:** `.md` files in `content/`
- **Leads:** `.csv` and `.json` files in `leads/` (for Google Sheets upload) and `.md` files (for reference)

If a directory does not exist or is empty, skip it and note it in the summary. Do not fail the run — continue with available assets.

## Step 3: Identify Strategies and Map Assets

Each strategy in `strategies/` is a top-level theme. For each strategy:

1. **Read the strategy `.md` file** to understand the strategy name, summary, and execution plan
2. **Map campaigns** — match campaigns in `campaigns/` to strategies by name/theme (e.g., `hiring-hurting-outreach` → `hiring-hurting` strategy)
3. **Map content** — match content in `content/` to strategies by name/theme
4. **Map leads** — match lead files in `leads/` to strategies by name/theme

Assets that don't clearly map to a strategy go under a `General` or `Ungrouped` section.

> **Iterate on errors (max 3 rounds):** If strategy mapping is ambiguous (e.g., a campaign could belong to multiple strategies), place it under the most specific match. If truly ambiguous after 3 attempts, ask the user which strategy to use.

## Step 4: Upload Lead Lists to Google Sheets

For each lead list file (`.csv` or `.json`) found in `leads/` (when `include_leads=true`):

1. **Parse the file**:
   - `.csv`: parse directly (UTF-8 with header row)
   - `.json`: flatten to tabular format

2. **Ensure required columns exist** (add if missing, use `N/A` if data unavailable):
   - `Name` — lead's full name
   - `Company` — company name
   - `Title` — job title
   - `LinkedIn URL` — LinkedIn profile URL
   - `Source` — how the lead was found
   - `Qualification Status` — e.g., "Qualified", "Not Qualified", "Needs Review"
   - `Qualification Reasoning` — why they qualified or didn't

   Preserve additional columns from the source data after the required columns.

3. **Create a new Google Sheet** using `RUBE_SEARCH_TOOLS` to find `GOOGLESHEETS_CREATE_GOOGLE_SHEET1`:
   - Title format: `<Client Name> — <Lead List Name> (<date>)`
   - Example: `Truewind — Botkeeper LinkedIn Leads (2026-02-24)`

4. **Write data** using `GOOGLESHEETS_BATCH_UPDATE`:
   - First row = headers (required columns first, then additional)
   - Remaining rows = data
   - Use `first_cell_location: "A1"` and `valueInputOption: "USER_ENTERED"`

5. **Record the spreadsheet URL** for use in Lead Lists file

Create sheets in parallel where possible. If a lead file is empty or malformed, skip it and note in summary.

**Troubleshooting:**
| Problem | Solution |
|---------|----------|
| Google Sheets creation fails | Verify Rube MCP server is connected. Run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]` |
| CSV parsing errors | Check for encoding issues — expects UTF-8 CSVs with a header row |
| JSON lead files have nested structure | Flatten the JSON to tabular format; extract key fields into required columns |
| Lead list is empty or malformed | Skip that file and note it in summary; do not create an empty Google Sheet |

## Step 5: Create the Package Directory

Create the full output directory structure:

```bash
mkdir -p "clients/${client_name}/client-package/${DATE}"
mkdir -p "clients/${client_name}/client-package/${DATE}/Strategies - ${DATE}"
```

## Step 6: Generate the Overview File

Create `clients/<client_name>/client-package/<date>/Overview - <date>.md`:

```markdown
# GTM Engineering Package — <Client Name>

**Prepared:** <date>
**For:** <recipient_name> (if provided)

## Summary

<Brief overview — strategies developed, leads found, campaigns built. Use intro_message if provided; otherwise generate from assets found.>

## What's Inside

### Strategies
- **<Strategy 1>** — <one-line summary>
- **<Strategy 2>** — <one-line summary>

### Lead Lists
See [Lead Lists - <date>](./Lead Lists - <date>.md) for all lead lists with Google Sheet links.

**Total leads found:** <count across all lists>

### Campaigns
<List of campaigns built, with which strategy they belong to>

### Content
<List of content pieces created>

---

<closing line — e.g., "Let me know if you'd like to discuss any of these assets.">
```

If `intro_message` is provided, use it verbatim as the Summary section. If `recipient_context` is provided, include it as a framing note before the Summary.

## Step 7: Generate the Lead Lists File

Create `clients/<client_name>/client-package/<date>/Lead Lists - <date>.md`:

```markdown
# Lead Lists — <Client Name>

**Date:** <date>

## Sheets

- **[<Client Name> — <Lead List 1>](<google-sheet-url>)** — <N> leads from <source description>
- **[<Client Name> — <Lead List 2>](<google-sheet-url>)** — <N> leads from <source description>

**Total:** <X> leads across <Y> sheets
```

If `include_leads=false` or no lead files were found, create the file with a note that no lead lists were included.

## Step 8: Generate Strategy Subfolders

For each strategy identified in Step 3, create a subfolder under `Strategies - <date>/`:

```
Strategies - <date>/
└── <Strategy Name>/
    ├── overview.md
    ├── <Substrategy/Campaign 1> - <date>.md
    ├── <Substrategy/Campaign 2> - <date>.md
    ├── <substrategy-1-leads>.csv
    └── <substrategy-2-leads>.csv
```

### overview.md

```markdown
# <Strategy Name>

<One-paragraph summary of the strategy>

**Signal:** <what signal is being tracked>
**Target ICP:** <filters and ideal customer profile>

## Assets

### Substrategies / Campaigns
- **<Substrategy 1>** — <brief description>
- **<Substrategy 2>** — <brief description>

### Content
- **<Content 1>** — <brief description>

### Lead Lists
- **[<Lead List>](<google-sheet-url>)** — <N> leads
```

### Substrategy / Campaign `.md` Files

For each campaign or content asset mapped to this strategy:
- Copy meaningful content from the original file
- Remove internal-only notes or orchestration details
- Include links to relevant Google Sheets
- Name: `<Descriptive Name> - <date>.md`

### Lead `.csv` Files

For each lead list mapped to this strategy:
- Export a copy of the lead data with standardized columns first
- Name: `<strategy-name>-leads.csv` or `<specific-source>-leads.csv`

## Step 9: Iterate on Errors (max 3 rounds)

If any file creation fails or an asset cannot be mapped:

1. Read the specific error or ambiguity
2. Apply the fix from the Troubleshooting table in Step 4
3. Retry the affected step
4. Repeat up to 3 times

After 3 rounds, if the error persists: skip the affected asset, note it in `/app/results/summary.md`, and continue with remaining assets.

## Step 10: Verify and Report

After all files are created, output a summary and write `/app/results/summary.md`:

```
## Package Created

**Location:** clients/<client_name>/client-package/<date>/

**Files:**
- Overview - <date>.md
- Lead Lists - <date>.md
- Strategies - <date>/
  - <Strategy 1>/
    - overview.md
    - <Substrategy 1> - <date>.md
    - <substrategy-1>-leads.csv
  - <Strategy 2>/
    - ...

**Google Sheets:**
- [Lead List 1](<sheets-url>) — 12 leads
- [Lead List 2](<sheets-url>) — 9 leads

**Total:** X files created, Y Google Sheets created, Z total leads
```

Then write `/app/results/validation_report.json` with stages for: setup, scan, strategy-mapping, lead-upload, directory-creation, file-generation, and final-report.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
CLIENT_PKG="clients/${client_name}/client-package/${date}"
for f in \
  "$CLIENT_PKG/Overview - ${date}.md" \
  "$CLIENT_PKG/Lead Lists - ${date}.md" \
  "/app/results/summary.md" \
  "/app/results/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] `Overview - <date>.md` exists with summary, TOC, and any recipient greeting
- [ ] `Lead Lists - <date>.md` exists with Google Sheet links (or note if none)
- [ ] Each strategy subfolder has `overview.md` and at least one asset file
- [ ] All lead CSVs use standardized columns
- [ ] `/app/results/summary.md` exists with package location and asset counts
- [ ] `/app/results/validation_report.json` exists with `stages` and `overall_passed`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Parallel Sheet creation.** Use parallel tool calls when creating multiple Google Sheets — this significantly reduces runtime for clients with many lead lists.
- **Strategy mapping is fuzzy.** Prefer over-inclusion (one asset in multiple strategies) over exclusion when mapping is ambiguous; the client can reorganize later.
- **Preserve original content.** When copying campaign or content files, keep the full text — do not summarize or truncate. Only remove internal orchestration notes.
- **Empty directories are skipped.** If `strategies/`, `campaigns/`, `content/`, or `leads/` is missing or empty, note it in the summary and continue — do not fail the run.
- **Rube MCP connection.** If Google Sheets tools are not found via `RUBE_SEARCH_TOOLS`, run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]` to activate the connection before retrying.
- **Date consistency.** Use the same `date` value for all folder and file names throughout the run — do not call `date` multiple times.
