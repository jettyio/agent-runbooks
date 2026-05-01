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
    source_collection: "playbooks"
    skill_name: "client-package-local"
    confidence: "high"
secrets: {}
---

# create-client-package — Agent Runbook

## Objective

Package all GTM work for a client into a structured local delivery package with dated `.md` files and Google Sheets. The agent reads the client's workspace folder (strategies, campaigns, content, leads, notes) and builds a navigable directory of dated deliverables. Lead lists are uploaded to Google Sheets and linked from the markdown files. Use this runbook when you want to deliver work to a client in a polished, navigable format without requiring Notion or any external platform beyond Google Sheets.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files before the task is considered complete.**

| File | Description |
|------|-------------|
| `clients/<client_name>/client-package/<date>/Overview - <date>.md` | High-level summary of all deliverables with table of contents |
| `clients/<client_name>/client-package/<date>/Lead Lists - <date>.md` | All Google Sheet links with lead counts and descriptions |
| `clients/<client_name>/client-package/<date>/Strategies - <date>/<strategy>/overview.md` | Per-strategy summary (one per strategy found) |
| `clients/<client_name>/client-package/<date>/Strategies - <date>/<strategy>/<asset> - <date>.md` | Individual campaign and content assets (one per asset) |
| `/app/results/summary.md` | Executive summary of the run with file counts and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `/app/results` | `/app/results` | Output directory for summary and validation report |
| `client_name` | *(required)* | Client folder name under `clients/` (e.g., `truewind`) |
| `date` | today's date | Date string in `YYYY-MM-DD` format, used for folder and file naming |
| `intro_message` | *(auto-generated)* | Custom introduction message for the overview file. If not provided, generate one based on assets found. |
| `recipient_name` | *(none)* | Name of the person receiving the package (used in intro) |
| `recipient_context` | *(none)* | Any framing context for the delivery (e.g., "we built these to capitalize on the Botkeeper shutdown") |
| `include_strategies` | `true` | Whether to include strategy documents |
| `include_campaigns` | `true` | Whether to include campaign assets |
| `include_content` | `true` | Whether to include content drafts |
| `include_leads` | `true` | Whether to include lead lists (uploaded to Google Sheets) |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Rube MCP server | MCP | Yes | Required for creating Google Sheets via Composio GOOGLESHEETS tools |
| `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | Composio tool | Yes | Creates a new Google Sheet via Rube MCP |
| `GOOGLESHEETS_BATCH_UPDATE` | Composio tool | Yes | Writes data rows to a Google Sheet |
| `RUBE_MANAGE_CONNECTIONS` | Composio tool | Conditional | Use to reconnect Google Sheets if `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` fails |
| `clients/<client_name>/` directory | Filesystem | Yes | The client's workspace directory must exist with at least one non-empty subfolder |

No API keys need to be configured manually — Google Sheets access is provided through the Rube MCP server.

---

## Step 1: Environment Setup

Verify all required prerequisites before touching the filesystem.

```bash
# Confirm client folder exists
CLIENT_DIR="clients/${client_name}"
if [ ! -d "$CLIENT_DIR" ]; then
  echo "ERROR: Client directory '$CLIENT_DIR' not found."
  exit 1
fi

# Confirm Rube MCP is available (if include_leads=true)
# The agent will detect missing MCP connectivity in Step 3 and surface the error there.

# Set date if not provided
DATE="${date:-$(date +%Y-%m-%d)}"
PACKAGE_DIR="${CLIENT_DIR}/client-package/${DATE}"
mkdir -p "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/Strategies - ${DATE}"

echo "Package directory created: ${PACKAGE_DIR}"
```

---

## Step 2: Scan the Client Folder

Read `clients/<client_name>/` and inventory all available assets:

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

- **Strategies:** `.md` files in `strategies/` — skip `ORCHESTRATION-PROMPT.md` and other internal-only files
- **Campaigns:** Campaign folders or `.md` files in `campaigns/`
- **Content:** `.md` files in `content/`
- **Leads:** `.csv` and `.json` files in `leads/` (for Google Sheets upload) and `.md` files (for reference)

If a directory doesn't exist or is empty, skip it and note it in the run summary.

---

## Step 3: Identify Strategies and Map Assets

Each strategy in `strategies/` is a top-level theme. For each strategy:

1. **Read the strategy `.md` file** to understand the strategy name, summary, and execution plan
2. **Map campaigns to strategies** — match campaigns in `campaigns/` to strategies by name/theme
3. **Map content to strategies** — match content in `content/` to strategies by name/theme
4. **Map leads to strategies** — match lead files in `leads/` to strategies by name/theme

Assets that don't clearly map to a strategy go under a `General` or `Ungrouped` section.

---

## Step 4: Upload Lead Lists to Google Sheets (max 3 rounds)

For each lead list file (`.csv` or `.json`) found in `leads/` (skip if `include_leads=false`):

1. **Parse the file** — `.csv` directly; `.json` flatten to tabular format
2. **Ensure required columns exist** (add with `N/A` if missing):
   - `Name`, `Company`, `Title`, `LinkedIn URL`, `Source`, `Qualification Status`, `Qualification Reasoning`
   - Preserve additional columns after the required ones
3. **Create a new Google Sheet** using `RUBE_SEARCH_TOOLS` to find `GOOGLESHEETS_CREATE_GOOGLE_SHEET1`:
   - Title format: `<Client Name> — <Lead List Name> (<date>)`
   - Example: `Truewind — Botkeeper LinkedIn Leads (2026-02-24)`
4. **Write data** using `GOOGLESHEETS_BATCH_UPDATE`:
   - First row = headers; remaining rows = data
   - Use `first_cell_location: "A1"` and `valueInputOption: "USER_ENTERED"`
5. **Record the spreadsheet URL** for linking in the Lead Lists file

If there are multiple lead files, create sheets in parallel where possible.

On failure: run `RUBE_MANAGE_CONNECTIONS` with `toolkits: ["googlesheets"]` and retry once. After 3 rounds of failures for a given file, skip it, note it in the summary, and continue with remaining files.

---

## Step 5: Create the Package Directory

```bash
mkdir -p "clients/${client_name}/client-package/${date}"
mkdir -p "clients/${client_name}/client-package/${date}/Strategies - ${date}"
```

---

## Step 6: Create the Overview File

Create `clients/<client_name>/client-package/<date>/Overview - <date>.md`:

```markdown
# GTM Engineering Package — <Client Name>

**Prepared:** <date>
**For:** <recipient_name> (if provided)

<intro_message or auto-generated summary>

## Summary

<Brief overview of what was done — strategies developed, leads found, campaigns built>

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

<closing line>
```

If `recipient_context` was provided, include it as a framing paragraph before the Summary section.

---

## Step 7: Create the Lead Lists File

Create `clients/<client_name>/client-package/<date>/Lead Lists - <date>.md`:

```markdown
# Lead Lists — <Client Name>

**Date:** <date>

## Sheets

- **[<Client> — <Lead List Name>](<google-sheet-url>)** — <N> leads from <source description>

**Total:** X leads across Y sheets
```

---

## Step 8: Create Strategy Subfolders

For each strategy identified in Step 3, create `Strategies - <date>/<Strategy Name>/`:

```
Strategies - <date>/
└── <Strategy Name>/
    ├── overview.md
    ├── <Substrategy/Campaign 1> - <date>.md
    ├── <Substrategy/Campaign 2> - <date>.md
    ├── <substrategy-1-leads>.csv
    └── <substrategy-2-leads>.csv
```

#### `overview.md`

- Strategy name and one-paragraph summary
- The signal being tracked
- Target ICP / filters
- List of substrategies, campaigns, and content pieces with brief descriptions
- Links to the Google Sheets for any related lead lists

#### Substrategy / Campaign `.md` files

- Copy the meaningful content from the original file
- Clean up internal-only notes or orchestration details
- Include links to relevant Google Sheets
- Name: `<Descriptive Name> - <date>.md`

#### Lead `.csv` files

- Export a copy of the lead data with standardized columns (Name, Company, Title, LinkedIn URL, Source, Qualification Status, Qualification Reasoning) plus any additional relevant columns
- Name descriptively: `<strategy-name>-leads.csv` or `<specific-source>-leads.csv`

---

## Step 9: Verify and Report

After all files are created, verify the output and produce the run summary.

```bash
PACKAGE_DIR="clients/${client_name}/client-package/${date}"

# Count created files
FILE_COUNT=$(find "$PACKAGE_DIR" -type f | wc -l)
echo "Files created: $FILE_COUNT"

# List all created files
find "$PACKAGE_DIR" -type f | sort

# Check required files exist
for required in \
  "${PACKAGE_DIR}/Overview - ${date}.md" \
  "${PACKAGE_DIR}/Lead Lists - ${date}.md"; do
  if [ ! -s "$required" ]; then
    echo "MISSING: $required"
  else
    echo "PRESENT: $required"
  fi
done
```

Output a summary in the terminal:

```
## Package Created

**Location:** clients/<client_name>/client-package/<date>/

**Files:**
- Overview - <date>.md
- Lead Lists - <date>.md
- Strategies - <date>/
  - <Strategy 1>/
    - overview.md
    - ...

**Google Sheets:**
- [Lead List 1](<sheets-url>) — N leads

**Total:** X files created, Y Google Sheets created, Z total leads
```

---

## Step 10: Write Summary and Validation Report

Write `/app/results/summary.md` with the run overview, file counts, and any issues encountered.

Write `/app/results/validation_report.json` with structured validation results per stage.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
PACKAGE_DIR="clients/${client_name}/client-package/${date}"

for required in \
  "${PACKAGE_DIR}/Overview - ${date}.md" \
  "${PACKAGE_DIR}/Lead Lists - ${date}.md" \
  "/app/results/summary.md" \
  "/app/results/validation_report.json"; do
  if [ ! -s "$required" ]; then
    echo "FAIL: $required is missing or empty"
  else
    echo "PASS: $required ($(wc -c < "$required") bytes)"
  fi
done
echo "=== END FINAL OUTPUT VERIFICATION ==="
```

### Checklist

- [ ] `Overview - <date>.md` created with correct client name, date, and TOC
- [ ] `Lead Lists - <date>.md` created with all Google Sheet links
- [ ] Strategy subfolders created for each strategy found
- [ ] Each strategy subfolder contains `overview.md`, campaign `.md` files, and lead `.csv` files
- [ ] All Google Sheets have required columns and correct title format
- [ ] `/app/results/summary.md` exists with file count and any issues noted
- [ ] `/app/results/validation_report.json` exists with `overall_passed` field

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Use the date parameter consistently.** All file and folder names use the same date string — set it once at the start and re-use it everywhere to avoid mismatches.
- **Parallel Sheet creation speeds up delivery.** When there are multiple lead lists, fire `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` calls in parallel rather than serially.
- **Verify Rube MCP before starting.** Run a quick `RUBE_SEARCH_TOOLS` call at the start to confirm the MCP server is connected. Catching this early avoids partial runs where the package directory is created but no Sheets are populated.
- **Skip, don't abort on missing directories.** If `campaigns/` or `content/` doesn't exist, continue with what's available. Note the missing folders in the summary.
- **Strategy mapping is fuzzy by design.** When a campaign or lead file could belong to multiple strategies, pick the most specific match. If truly ambiguous, ask the user rather than guessing.
- **Slugify asset filenames for the `.csv` copies.** Use the strategy name in the filename (e.g., `botkeeper-shutdown-leads.csv`) so the files are human-readable and sortable.
- **Keep internal notes out of deliverables.** Strip `ORCHESTRATION-PROMPT.md` and any section marked as "internal only" from all output files.
