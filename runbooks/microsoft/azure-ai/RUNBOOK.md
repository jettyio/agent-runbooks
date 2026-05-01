---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/github-copilot-for-azure/azure-ai"
  source_host: "skills.sh"
  source_title: "Azure AI Services"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-ai"
    confidence: "high"
secrets: {}
---

# Azure AI Services — Agent Runbook

## Objective

This runbook guides an agent through using Azure AI services — including AI Search,
Speech, OpenAI (GPT/embeddings/DALL-E), and Document Intelligence — via the Azure MCP
server or CLI. It covers configuring MCP tools (`azure__search`, `azure__speech`),
executing full-text, vector, and hybrid search queries, performing speech-to-text and
text-to-speech operations, and verifying output correctness. Use this runbook when a
task requires Azure AI capabilities such as semantic search, transcription, OCR, or
form extraction.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary: what was done, services used, outputs produced |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/search_results.json` | Results from any AI Search query operations (empty array `[]` if no search was performed) |
| `/app/results/speech_output.txt` | Output from speech transcription or synthesis (empty string if not performed) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Azure subscription | *(from environment)* | Azure subscription ID or name |
| Search index name | *(required)* | Name of the AI Search index to query |
| Search query | *(required)* | Query string for AI Search |
| Search mode | `hybrid` | One of: `full-text`, `vector`, `hybrid` |
| Speech input file | *(optional)* | Path to audio file for transcription |
| Speech output file | `/app/results/speech_output.txt` | Path for synthesis output |
| MCP enabled | `true` | Whether the Azure MCP server is active |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `azure__search` MCP tool | MCP server | Preferred | Azure AI Search via MCP: list indexes, query, get index details |
| `azure__speech` MCP tool | MCP server | Preferred | Azure Speech via MCP: transcribe audio, synthesize text |
| `az` CLI | CLI | Fallback | Azure CLI for search and cognitive services management |
| `az search` | CLI subcommand | Fallback | Manage AI Search resources |
| `az cognitiveservices` | CLI subcommand | Fallback | Manage OpenAI and other cognitive services |
| Azure subscription access | Credential | Yes | Valid Azure credentials in environment |

---

## Step 1: Environment Setup

Verify that required dependencies and credentials are available.

```bash
# Verify Azure CLI is installed
command -v az >/dev/null || { echo "ERROR: az CLI not installed"; exit 1; }

# Verify Azure credentials
az account show >/dev/null 2>&1 || { echo "ERROR: Not logged in to Azure. Run: az login"; exit 1; }
az account show --query name -o tsv

# Create output directory
mkdir -p /app/results
```

**MCP check:** If the Azure MCP server (`azure__search`, `azure__speech`) is active, prefer
those tools over the CLI. If not enabled, run `/azure:setup` or enable via `/mcp`.

---

## Step 2: Discover AI Search Indexes

List available AI Search indexes to identify the target index.

**Via MCP (preferred):**
```
azure__search command=search_index_list
```

**Via CLI (fallback):**
```bash
az search index list --service-name <SEARCH_SERVICE_NAME> --resource-group <RESOURCE_GROUP> -o table
```

Confirm the target index exists before proceeding. If the index is not found, stop and
report the error.

---

## Step 3: Inspect the Target Index

Retrieve index schema to understand available fields and search capabilities.

**Via MCP:**
```
azure__search command=search_index_get index=<INDEX_NAME>
```

**Via CLI:**
```bash
az search index show --name <INDEX_NAME> --service-name <SEARCH_SERVICE_NAME> --resource-group <RESOURCE_GROUP>
```

Note which fields support:
- Full-text search (string fields with analyzer)
- Vector search (fields with vector profile)
- Semantic configuration names (if hybrid/semantic mode requested)

---

## Step 4: Execute the Search Query

Run the search query using the selected mode. Capture results to `/app/results/search_results.json`.

**Via MCP:**
```
azure__search command=search_query index=<INDEX_NAME> query=<QUERY> mode=<MODE>
```

**Via CLI:**
```bash
# Full-text search
az rest --method POST \
  --url "https://<SEARCH_SERVICE>.search.windows.net/indexes/<INDEX_NAME>/docs/search?api-version=2023-11-01" \
  --headers "Content-Type=application/json" \
  --body '{"search": "<QUERY>", "queryType": "simple"}' \
  | tee /app/results/search_results.json

# Vector/hybrid search — include vectorQueries in the body
```

Write results to `/app/results/search_results.json`.

---

## Step 5: Speech Operations (Optional)

Perform speech-to-text or text-to-speech if required by the task.

### Speech-to-Text (Transcription)
**Via MCP:**
```
azure__speech command=speech_transcribe audio_file=<PATH_TO_AUDIO>
```

### Text-to-Speech (Synthesis)
**Via MCP:**
```
azure__speech command=speech_synthesize text="<TEXT>" voice="en-US-AriaNeural"
```

Save transcription or synthesis output to `/app/results/speech_output.txt`.

If speech operations are not required, write an empty file:
```bash
echo "" > /app/results/speech_output.txt
```

---

## Step 6: Iterate on Errors (max 3 rounds)

If any step above fails, apply targeted fixes:

| Error | Fix |
|-------|-----|
| MCP tool not found / not enabled | Fall back to `az` CLI equivalents; ensure `/azure:setup` was run |
| Index not found | Re-run Step 2 to list available indexes; check spelling and region |
| Auth error (401/403) | Re-run `az login` or verify service principal credentials |
| No results returned | Broaden the query; check index has documents with `az search index show` |
| Speech audio format unsupported | Convert to WAV/PCM 16kHz 16-bit mono before transcribing |
| Rate limit (429) | Wait and retry; note Azure AI Search free-tier limits |

Retry each failed step up to 3 times before reporting failure in `summary.md`.

---

## Final Checklist

Run the verification script and write the output files.

### Write Summary

Write `/app/results/summary.md` describing:
- Which Azure AI services were used
- Queries executed and result counts
- Any speech operations performed
- Errors encountered and how they were resolved

### Write Validation Report

Write `/app/results/validation_report.json` with the following shape:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601>",
  "stages": [
    { "name": "setup",    "passed": true, "message": "Azure CLI authenticated" },
    { "name": "search",   "passed": true, "message": "Query returned N results" },
    { "name": "speech",   "passed": true, "message": "Speech operation completed / skipped" },
    { "name": "outputs",  "passed": true, "message": "All output files written" }
  ],
  "results": { "pass": 0, "partial": 0, "fail": 0 },
  "overall_passed": true,
  "output_files": [
    "/app/results/summary.md",
    "/app/results/validation_report.json",
    "/app/results/search_results.json",
    "/app/results/speech_output.txt"
  ]
}
```

### FINAL OUTPUT VERIFICATION

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/search_results.json" \
  "$RESULTS_DIR/speech_output.txt"; do
  if [ ! -e "$f" ]; then
    echo "FAIL: $f is missing"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

---

## Tips

- **MCP is preferred over CLI.** When `azure__search` and `azure__speech` are available,
  use them — they handle authentication automatically and return structured results.
- **Hybrid search outperforms pure keyword or pure vector search** for most natural-language
  queries against enterprise content. Default to `mode=hybrid` when in doubt.
- **SSML for synthesis.** When using `speech_synthesize`, wrap text in SSML to control
  prosody, voice, and language. Example: `<speak><voice name="en-US-AriaNeural">Hello</voice></speak>`.
- **Index fields matter.** Always inspect the index schema (Step 3) before querying — using
  a non-searchable field in a filter causes a 400 error.
- **Document Intelligence is CLI-only in MCP v0.** Use
  `az cognitiveservices account` and the REST API for form extraction / OCR until an
  MCP command is added.
