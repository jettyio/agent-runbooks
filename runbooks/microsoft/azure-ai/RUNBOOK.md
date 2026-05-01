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

This runbook guides an agent through working with Azure AI services including AI Search, Speech, OpenAI, and Document Intelligence. Use this runbook when a task involves search (full-text, vector, hybrid, or semantic), speech-to-text, text-to-speech, transcription, OCR, or form extraction. When Azure MCP is enabled, prefer the `azure__search` and `azure__speech` MCP tools; otherwise fall back to the Azure CLI (`az`) or SDK calls. The runbook covers service discovery, tool invocation patterns, SDK usage, and verification of outputs.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata, service used, and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/service_output.md` | Raw or summarized output from the Azure AI service call(s) performed |
| `/app/results/commands_run.md` | List of all MCP tool calls or CLI commands executed during the run |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all result files |
| Azure service | *(required)* | Target service: `ai-search`, `speech`, `openai`, `document-intelligence` |
| Azure subscription | *(required)* | Azure subscription ID or name |
| Resource group | *(required)* | Azure resource group containing the target resource |
| Search index name | *(optional)* | Required when `azure_service=ai-search` |
| Search query | *(optional)* | Query string for AI Search operations |
| Speech input | *(optional)* | File path or text for speech operations |
| Use MCP | `auto` | `auto` (prefer MCP if available), `force`, or `cli` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Azure MCP server | MCP | Preferred | Provides `azure__search` and `azure__speech` tools |
| `az` CLI | CLI | Fallback | Azure CLI for service management when MCP unavailable |
| `python3` | Runtime | Optional | For SDK-based access to Azure AI services |
| `azure-search-documents` | Python package | Optional | Azure AI Search Python SDK |
| `azure-cognitiveservices-speech` | Python package | Optional | Azure Speech SDK |
| `openai` | Python package | Optional | Azure OpenAI Python SDK |
| Azure credentials | Credential | Yes | Service principal or managed identity with appropriate role |

---

## Step 1: Environment Setup

Verify the Azure environment and determine which invocation method to use (MCP vs. CLI).

```bash
echo "=== AZURE AI SERVICES SETUP ==="

# Check if Azure MCP is available
if command -v mcp >/dev/null 2>&1; then
  echo "MCP available — will prefer azure__search / azure__speech tools"
  USE_MCP=true
else
  echo "MCP not available — will use Azure CLI fallback"
  USE_MCP=false
fi

# Verify az CLI is installed (needed as fallback or for management tasks)
command -v az >/dev/null 2>&1 || { echo "WARNING: az CLI not found. Install via: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"; }

# Verify login state
az account show --query "{subscription:id, name:name}" -o json 2>/dev/null || {
  echo "Not logged in to Azure. Run: az login"
  exit 1
}

# Create output directory
mkdir -p /app/results

echo "Setup complete."
```

If the environment is not authenticated, abort and instruct the user to run `az login` or configure a service principal.

---

## Step 2: Select Service and Verify Resource Exists

Based on the `azure_service` parameter, confirm the target resource exists and is accessible.

### AI Search

```bash
# List search services in the resource group
az search service list --resource-group "$RESOURCE_GROUP" -o table

# Verify index exists
az search index list \
  --service-name "$SEARCH_SERVICE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  -o table
```

Or via MCP (preferred when available):

```
azure__search(command="search_index_list")
```

### Speech

```bash
# List cognitive services (Speech is a Cognitive Service)
az cognitiveservices account list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?kind=='SpeechServices']" \
  -o table
```

Or via MCP:

```
azure__speech(command="speech_transcribe", ...)
azure__speech(command="speech_synthesize", ...)
```

### OpenAI

```bash
az cognitiveservices account list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?kind=='OpenAI']" \
  -o table
```

### Document Intelligence

```bash
az cognitiveservices account list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?kind=='FormRecognizer']" \
  -o table
```

Record the endpoint URL and resource name; you will need them in subsequent steps.

---

## Step 3: Invoke the Azure AI Service

Choose the appropriate invocation path based on the selected service and available tools.

### Path A — AI Search (MCP preferred)

```python
# Via MCP tool (when Azure MCP server is running)
# azure__search(command="search_query", index="<index>", query="<query>")

# Via Python SDK fallback
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

client = SearchClient(
    endpoint="https://<service>.search.windows.net",
    index_name="<index>",
    credential=DefaultAzureCredential()
)
results = client.search(search_text="<query>", top=10)
for r in results:
    print(r)
```

### Path B — Speech (MCP preferred)

```python
# Via MCP tool
# azure__speech(command="speech_transcribe", audio_file="<path>")
# azure__speech(command="speech_synthesize", text="<text>", voice="en-US-JennyNeural")

# Via SDK fallback
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    endpoint="https://<region>.api.cognitive.microsoft.com",
    subscription="<key>"
)
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
result = recognizer.recognize_once()
print(result.text)
```

### Path C — OpenAI

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://<resource>.openai.azure.com",
    api_version="2024-02-01"
)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "<prompt>"}]
)
print(response.choices[0].message.content)
```

### Path D — Document Intelligence

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.identity import DefaultAzureCredential

client = DocumentAnalysisClient(
    endpoint="https://<resource>.cognitiveservices.azure.com",
    credential=DefaultAzureCredential()
)
poller = client.begin_analyze_document_from_url("prebuilt-document", "<doc_url>")
result = poller.result()
for page in result.pages:
    for line in page.lines:
        print(line.content)
```

Save the raw output to `/app/results/service_output.md`.

---

## Step 4: Iterate on Errors (max 3 rounds)

If Step 3 fails or returns unexpected results:

1. Check the error message — common causes are:
   - Authentication: re-run `az login` or verify the managed identity has the correct role
   - Missing MCP: if `azure__search` returns "tool not found", fall back to the SDK path
   - Index not found: verify the index name with `az search index list` or `azure__search(command="search_index_list")`
   - Quota/capacity: check the Azure portal for quota limits

2. Apply the appropriate fix from the table below:

| Error | Fix |
|-------|-----|
| `AuthenticationError` | Run `az login` or ensure managed identity is configured |
| `ResourceNotFoundError` | Verify resource group, service name, and index name |
| MCP tool not found | Switch to CLI / SDK path; confirm MCP server is running |
| Rate limit / quota | Reduce request frequency; check Azure portal quota |
| Empty search results | Broaden query; check index has documents; verify field names |

3. Re-run Step 3 with the corrected inputs.
4. Repeat up to 3 times total.

After 3 rounds without resolution, abort and document the failure in `/app/results/summary.md`.

---

## Step 5: Validate Output

Confirm the service returned meaningful results before writing the summary.

```bash
# Check service_output.md is non-empty
if [ ! -s /app/results/service_output.md ]; then
  echo "FAIL: service_output.md is missing or empty — Azure AI call may have failed"
  exit 1
fi

echo "PASS: service_output.md present ($(wc -c < /app/results/service_output.md) bytes)"

# For AI Search: confirm at least one result returned
if grep -q '"@search.score"' /app/results/service_output.md 2>/dev/null; then
  echo "PASS: Search results contain scored documents"
fi

# For Speech: confirm transcription text is present
if grep -qi 'transcription\|recognized\|text:' /app/results/service_output.md 2>/dev/null; then
  echo "PASS: Speech output contains transcription"
fi
```

---

## Step 6: Write Commands Log

Document all MCP tool calls and CLI commands executed during this run.

```bash
cat > /app/results/commands_run.md << 'EOF'
# Commands Run

## Service Selection
- Service: <azure_service>
- Invocation method: <MCP|CLI|SDK>

## Commands Executed
1. `az account show` — verified Azure login
2. <tool or command> — <purpose>
3. ...
EOF
```

---

## Step 7: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/service_output.md" \
  "$RESULTS_DIR/commands_run.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `summary.md` exists and describes the service used, inputs, and results
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `service_output.md` exists and contains actual output from the Azure AI call
- [ ] `commands_run.md` exists and lists all MCP tool calls and CLI commands used
- [ ] No Azure credentials or secrets were written to any output file
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Prefer MCP over CLI.** When `azure__search` or `azure__speech` are available via an active MCP server, use them — they are faster and require fewer credentials to configure explicitly. If MCP is absent, the CLI and SDK paths both work.
- **Enable Azure MCP if needed.** Run `/azure:setup` or enable via `/mcp` in Copilot for Azure to activate MCP tooling.
- **Use `DefaultAzureCredential` in SDK calls.** It automatically picks up managed identity, `az login` sessions, and environment variables — no hardcoded keys.
- **AI Search hybrid queries perform best.** Combine keyword + vector search for highest recall and relevance; use `queryType="semantic"` for re-ranking on supported indexes.
- **Batch speech transcription** is preferred for files > 60 seconds; real-time recognition works best for short utterances.
- **SDK Quick Reference guides** are available in the source repository for AI Search (Python/TS/.NET), OpenAI (.NET), Vision, Transcription, Translation, Document Intelligence, and Content Safety — consult them for idiomatic SDK patterns.
