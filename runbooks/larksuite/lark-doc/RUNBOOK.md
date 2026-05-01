---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/larksuite/cli/lark-doc"
  source_host: "skills.sh"
  source_title: "lark-doc"
  imported_at: "2026-05-01T03:50:37Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "larksuite"
    skill_name: "lark-doc"
    confidence: "high"
secrets: {}
---

# lark-doc — Agent Runbook

## Objective

This runbook enables an AI agent to interact with Feishu (Lark) cloud documents using the `lark-cli` command-line tool and the Lark Docs v2 API. The agent can create new documents, fetch document content in multiple detail levels and scopes, update documents using eight distinct operation modes (str_replace, block_insert_after, block_copy_insert_after, block_replace, block_delete, block_move_after, overwrite, append), upload and download document media (images and files), and search cloud-drive documents. All `docs +create`, `docs +fetch`, and `docs +update` operations **must** include `--api-version v2`. The default content format is DocxXML; Markdown is supported as an alternative.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the operation performed, including command used, document URL/token, and outcome |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/output.md` | The document content fetched or confirmation of create/update/media operation |
| `/app/results/command_log.txt` | Full command(s) executed with all flags, redacted of secrets |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `--doc` | *(required for fetch/update)* | Document URL or token |
| `--api-version` | `v2` | **Always use `v2`**; never omit |
| `--command` | `append` | Update mode: `str_replace`, `block_insert_after`, `block_copy_insert_after`, `block_replace`, `block_delete`, `block_move_after`, `overwrite`, or `append` |
| `--content` | *(required for create/update)* | XML or Markdown content to write |
| `--doc-format` | `xml` | Content format: `xml` (default) or `markdown` |
| `--detail` | `simple` | Fetch detail level: `simple`, `with-ids`, or `full` |
| `--scope` | `full` | Fetch scope: `full`, `outline`, `range`, `keyword`, or `section` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `lark-cli` | CLI binary | Yes | Main CLI for all Lark document operations |
| Lark authentication | Credential | Yes | Read `../lark-shared/SKILL.md` for auth setup — user_access_token or app credentials |
| Lark Docs v2 API | External API | Yes | All operations must use `--api-version v2` |

---

## Step 1: Environment Setup

Before executing any document operation, **you MUST read the shared Lark skill documentation**:

```bash
# Verify lark-cli is installed
lark-cli --version

# Read shared authentication and global parameters guide
# This is MANDATORY — do not skip
cat "$(lark-cli skill-path lark-shared)/SKILL.md" 2>/dev/null ||   echo "Read lark-shared/SKILL.md from the skills repository"

# Create output directories
mkdir -p /app/results
```

**CRITICAL prerequisite reading before any operation:**
1. `lark-shared/SKILL.md` — authentication, permissions, global parameters (required for ALL operations)
2. For **fetch** → `lark-doc-fetch.md` (scope/detail selection, partial read strategies, `<fragment>`/`<excerpt>` output structure)
3. For **create or edit** → `lark-doc-xml.md` (XML syntax rules); use `lark-doc-md.md` only when user explicitly requests Markdown
4. For **creating from scratch** → also read `lark-doc-create-workflow.md`
5. For **editing existing documents** → also read `lark-doc-update-workflow.md`

**Skipping these reference files causes parameter errors, format errors, or style failures.**

---

## Step 2: Determine Operation

Identify which operation the user wants based on their request:

| User intent | Operation | Shortcut |
|-------------|-----------|----------|
| Read/view document content | Fetch | `lark-cli docs +fetch --api-version v2` |
| Create a new document | Create | `lark-cli docs +create --api-version v2` |
| Edit/modify existing document | Update | `lark-cli docs +update --api-version v2` |
| Insert image or file | Media insert | `lark-cli docs +media-insert` |
| Download image/file/whiteboard | Media download | `lark-cli docs +media-download` |
| Preview media in document | Media preview | `lark-cli docs +media-preview` |
| Find document by name/keyword | Search | `lark-cli drive +search` (**not** `docs +search`, which is deprecated) |

**Format selection rules:**
- **Create / bulk write** (`+create`, or `+update --command append/overwrite`): XML or Markdown both allowed. Use Markdown only when user provides a `.md` file or explicitly requests it; otherwise default to XML (supports callout, grid, checkbox, and other rich blocks).
- **Precise editing** (`+update` with `str_replace` / `block_insert_after` / `block_replace` / `block_delete` / `block_move_after`): Always use XML (`--doc-format xml`, the default). XML ensures stable block structure and style for precise edits.

---

## Step 3: Execute the Operation

### Fetch Document Content

```bash
# Basic fetch (simple detail, full scope)
lark-cli docs +fetch --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN"

# With detail level
lark-cli docs +fetch --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --detail with-ids

# Partial read by keyword
lark-cli docs +fetch --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --scope keyword --keyword "TARGET_TERM"

# Partial read by section heading
lark-cli docs +fetch --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --scope section --section "HEADING_TEXT"
```

### Create Document

```bash
# Create with XML content
lark-cli docs +create --api-version v2 --content '<title>Document Title</title><p>Body paragraph.</p>'

# Create from Markdown file
lark-cli docs +create --api-version v2 --content "$(cat document.md)" --doc-format markdown
```

### Update Document

```bash
# Append content
lark-cli docs +update --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --command append --content '<p>New content</p>'

# String replace
lark-cli docs +update --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --command str_replace --old-str "old text" --new-str "new text"

# Insert block after a specific block
lark-cli docs +update --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --command block_insert_after --block-id "BLOCK_ID" --content '<p>New block</p>'

# Overwrite entire document
lark-cli docs +update --api-version v2 --doc "DOCUMENT_URL_OR_TOKEN" --command overwrite --content '<title>New Title</title><p>New content</p>'
```

### Media Operations

```bash
# Insert image (from clipboard — preferred for screenshots)
lark-cli docs +media-insert --doc "DOCUMENT_URL_OR_TOKEN" --from-clipboard

# Insert image from file
lark-cli docs +media-insert --doc "DOCUMENT_URL_OR_TOKEN" --file "/path/to/image.png"

# Download media
lark-cli docs +media-download --doc "DOCUMENT_URL_OR_TOKEN" --media-token "MEDIA_TOKEN"

# Download whiteboard thumbnail
lark-cli docs +media-download --doc "DOCUMENT_URL_OR_TOKEN" --type whiteboard
```

### Search (use drive +search, not docs +search)

```bash
# Search cloud drive for documents
lark-cli drive +search --query "search terms"
```

---

## Step 4: Handle Embedded Resources

When document content contains embedded resource tags, extract tokens and switch to the appropriate skill:

| Tag / Attribute | Extract field | Switch to skill |
|-----------------|---------------|-----------------|
| `<sheet token="..." sheet-id="...">` | `token` → spreadsheet_token, `sheet-id` | `lark-sheets` |
| `<bitable token="..." table-id="...">` | `token` → app_token, `table-id` | `lark-base` |
| `<cite type="doc" file-type="sheets" token="..." sheet-id="...">` | Same as `<sheet>` | `lark-sheets` |
| `<cite type="doc" file-type="bitable" token="..." table-id="...">` | Same as `<bitable>` | `lark-base` |
| `<synced_reference src-token="..." src-block-id="...">` | `src-token` → doc_token, `src-block-id` → block_id | Use `docs +fetch` on src-token document |

**Always extract tokens and fetch nested data; never present raw tags as final output.**

---

## Step 5: Iterate on Errors (max 3 rounds)

If an operation fails:

1. Read the error message from command output
2. Apply the targeted fix from the Common Fixes table below
3. Retry the command with corrected parameters
4. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| Missing `--api-version v2` | Add `--api-version v2` to the command |
| Authentication error | Re-read `lark-shared/SKILL.md` for token refresh procedure |
| Block ID not found | Use `+fetch --detail with-ids` to get current block IDs |
| XML format error | Re-read `lark-doc-xml.md` and validate XML structure |
| Media upload fails | Check file size limits; use `--from-clipboard` for screenshots |
| `docs +search` not found | Use `drive +search` instead (docs +search is deprecated) |

---

## Step 6: Write Results

```bash
# Save operation output
RESULTS_DIR="/app/results"

# Write command log (redact any tokens from display)
echo "Command: lark-cli docs +<operation> --api-version v2 [flags]" > "$RESULTS_DIR/command_log.txt"
echo "Executed at: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RESULTS_DIR/command_log.txt"

# Write document output to output.md
# (paste actual command output here)

# Write summary
cat > "$RESULTS_DIR/summary.md" << 'SUMMARY'
# lark-doc Operation Summary

## Operation
- Command: <describe what was run>
- Document: <URL or token, if applicable>
- API version: v2
- Format: xml / markdown

## Result
- Status: success / failure
- Output: <brief description>

## Issues
- <Any errors encountered and how they were resolved>
SUMMARY
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/output.md" \
  "$RESULTS_DIR/command_log.txt"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `lark-shared/SKILL.md` was read before any operation
- [ ] All `docs +create`/`+fetch`/`+update` commands included `--api-version v2`
- [ ] Appropriate format reference was read (`lark-doc-xml.md` or `lark-doc-md.md`)
- [ ] For create: `lark-doc-create-workflow.md` was read
- [ ] For edit: `lark-doc-update-workflow.md` was read
- [ ] Embedded resource tags were extracted and sub-skills were invoked as needed
- [ ] `docs +search` was NOT used; `drive +search` was used instead
- [ ] `/app/results/output.md` contains the operation result
- [ ] `/app/results/command_log.txt` contains the command(s) run
- [ ] `/app/results/summary.md` describes the operation and outcome
- [ ] `/app/results/validation_report.json` is written with `overall_passed`
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Always use `--api-version v2`.** Omitting this flag causes the CLI to fall back to the deprecated v1 API, which returns different response structures and may silently produce incorrect results.
- **Prefer XML for precise edits.** Even though Markdown is simpler to write, XML gives stable block-level control for `str_replace` and `block_*` operations.
- **Use `--scope` to limit context window usage.** For large documents, use `--scope keyword`, `--scope section`, or `--scope range` instead of fetching the full document — this reduces token consumption and speeds up operations.
- **`drive +search` is the unified resource discovery entry point.** Use it first when the user asks to find a spreadsheet, report, or recently edited file by name.
- **`+media-insert --from-clipboard` is preferred for screenshots.** For images already on the clipboard (e.g., screenshots, copied from Feishu/browser), this is faster and avoids saving a temp file.
- **Never present embedded `<sheet>` or `<bitable>` tags as final output.** Always extract tokens and fetch nested data from `lark-sheets` or `lark-base`.
