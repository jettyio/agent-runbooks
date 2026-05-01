---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-ai"
  source_host: "skills.sh"
  source_title: "Azure AI Services"
  imported_at: "2026-05-01T02:57:56Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-ai"
    confidence: "high"
secrets:
  AZURE_SUBSCRIPTION_ID:
    env: AZURE_SUBSCRIPTION_ID
    description: "Azure subscription ID for CLI operations (optional if using MCP server)"
    required: false
  AZURE_OPENAI_API_KEY:
    env: AZURE_OPENAI_API_KEY
    description: "API key for Azure OpenAI service (optional if using managed identity)"
    required: false
---

# Azure AI Services — Agent Runbook

## Objective

This runbook guides an AI agent through working with Azure AI services including Azure AI Search, Azure Speech, Azure OpenAI, and Azure Document Intelligence. The agent will configure and use the appropriate tools (Azure MCP server or Azure CLI) to perform AI-powered operations such as full-text search, vector/hybrid search, speech-to-text transcription, text-to-speech synthesis, and OCR-based document extraction. Use this runbook when the task involves any of: AI Search queries, vector or semantic search, speech transcription, text-to-speech conversion, or document form extraction with Azure services.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of operations performed, services used, and outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |
| `/app/results/azure_ai_output.md` | Results of the Azure AI operations requested (search results, transcription output, etc.) |

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| Results directory | Output directory for all results | `/app/results` |
| Azure service | Target Azure AI service (`search`, `speech`, `openai`, `document-intelligence`) | *(required)* |
| Operation | Operation to perform (e.g. `query`, `transcribe`, `synthesize`, `extract`) | *(required)* |
| Input data | Path to input file or query string | *(required)* |
| Azure region | Azure region for the service endpoint | `eastus` |
| Search index name | Name of the Azure AI Search index (search operations only) | *(optional)* |
| Vector search | Enable vector/hybrid search mode | `false` |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `azure-cli` | CLI | Recommended | `az` CLI for Azure resource management and service operations |
| Azure MCP server | MCP | Preferred | `azure__search`, `azure__speech` tools when MCP is enabled |
| `azure-search-documents` | Python package | Optional | Python SDK for Azure AI Search |
| `azure-cognitiveservices-speech` | Python package | Optional | Python SDK for Azure Speech |
| `openai` | Python package | Optional | Python SDK for Azure OpenAI |
| `azure-ai-documentintelligence` | Python package | Optional | Python SDK for Document Intelligence |
| Azure subscription | Credential | Yes | Active Azure subscription with AI services provisioned |

## Step 1: Environment Setup

Verify the Azure environment is ready and the appropriate tooling is available.

```bash
echo "=== Azure AI Services — Environment Setup ==="

# Check for Azure MCP tools (preferred path)
if command -v az >/dev/null 2>&1; then
  echo "PASS: Azure CLI available"
  az version --query '"azure-cli"' -o tsv 2>/dev/null || echo "  (version check skipped)"
else
  echo "WARN: Azure CLI not found — MCP server must be available"
fi

# Verify output directory
mkdir -p /app/results
echo "PASS: Output directory ready at /app/results"

# Check authentication (if using CLI)
if command -v az >/dev/null 2>&1; then
  az account show --query "{subscription:id, name:name}" -o table 2>/dev/null \
    && echo "PASS: Azure CLI authenticated" \
    || echo "WARN: Not logged in — run 'az login' or set AZURE_* env vars"
fi
```

If Azure MCP is not enabled, run `/azure:setup` or enable via `/mcp` before proceeding. If Azure CLI is unavailable and MCP is unavailable, the task cannot continue — write a `validation_report.json` with `overall_passed: false`.

## Step 2: Identify Target Service and Operation

Based on the task description, select the correct Azure AI service:

| If the task mentions… | Use this service | Primary tool |
|----------------------|-----------------|--------------|
| Search, query, find, vector, semantic, hybrid | **AI Search** | `azure__search` / `az search` |
| Speech, transcribe, audio, voice, text-to-speech | **Speech** | `azure__speech` / Azure Speech SDK |
| GPT, completion, embedding, DALL-E, chat | **OpenAI** | Azure OpenAI SDK / `az cognitiveservices` |
| Form, OCR, document, extract, receipt, invoice | **Document Intelligence** | Azure Document Intelligence SDK |

Record your selection before proceeding to the relevant step.

## Step 3: Azure AI Search Operations

*Skip this step if not using AI Search.*

### Option A — MCP Server (Preferred when enabled)

```
# List available search indexes
azure__search command=search_index_list

# Inspect a specific index
azure__search command=search_index_get index_name=<INDEX_NAME>

# Run a full-text or keyword query
azure__search command=search_query index_name=<INDEX_NAME> query="<SEARCH_TERMS>"

# Run a vector / hybrid query
azure__search command=search_query index_name=<INDEX_NAME> query="<SEARCH_TERMS>" search_mode=hybrid
```

### Option B — Azure CLI

```bash
# List search services in subscription
az search service list --output table

# Query an index via REST (requires endpoint and API key)
ENDPOINT="https://<service-name>.search.windows.net"
API_KEY="<your-admin-or-query-key>"
INDEX="<index-name>"

curl -s -X POST \
  "${ENDPOINT}/indexes/${INDEX}/docs/search?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: ${API_KEY}" \
  -d '{"search": "<QUERY>", "queryType": "semantic", "semanticConfiguration": "default", "top": 5}' \
  | python3 -m json.tool
```

### AI Search Capabilities Reference

| Feature | Description |
|---------|-------------|
| Full-text search | Linguistic analysis, stemming, BM25 scoring |
| Vector search | Semantic similarity with embeddings |
| Hybrid search | Combined keyword + vector for best relevance |
| AI enrichment | Entity extraction, OCR, sentiment during indexing |

## Step 4: Azure Speech Operations

*Skip this step if not using Azure Speech.*

### Option A — MCP Server (Preferred when enabled)

```
# Transcribe audio to text
azure__speech command=speech_transcribe audio_file=<PATH_TO_AUDIO>

# Synthesize text to speech
azure__speech command=speech_synthesize text="<TEXT_TO_SPEAK>" output_file=/app/results/output.wav
```

### Option B — Python SDK

```python
import azure.cognitiveservices.speech as speechsdk

# Speech-to-text
speech_config = speechsdk.SpeechConfig(
    subscription="<AZURE_SPEECH_KEY>",
    region="<AZURE_REGION>"
)
audio_config = speechsdk.audio.AudioConfig(filename="<AUDIO_FILE>")
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
result = recognizer.recognize_once()
print("Transcription:", result.text)
```

### Speech Capabilities Reference

| Feature | Description |
|---------|-------------|
| Speech-to-text | Real-time and batch transcription |
| Text-to-speech | Neural voices, SSML support |
| Speaker diarization | Identify who spoke when |
| Custom models | Domain-specific vocabulary |

## Step 5: Azure OpenAI Operations

*Skip this step if not using Azure OpenAI.*

```bash
# List available cognitive services accounts
az cognitiveservices account list --output table

# Deploy a model (if needed)
az cognitiveservices account deployment create \
  --name <ACCOUNT_NAME> \
  --resource-group <RG> \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://<account>.openai.azure.com/",
    api_key="<AZURE_OPENAI_KEY>",
    api_version="2024-02-01"
)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "<PROMPT>"}]
)
print(response.choices[0].message.content)
```

## Step 6: Azure Document Intelligence Operations

*Skip this step if not using Document Intelligence.*

```python
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<resource>.cognitiveservices.azure.com/"
key = "<DOCUMENT_INTELLIGENCE_KEY>"
client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

with open("<DOCUMENT_PATH>", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-layout", f)
result = poller.result()

for page in result.pages:
    for line in page.lines:
        print(line.content)
```

## Step 7: Iterate on Errors (max 3 rounds)

If any Azure AI operation fails or returns unexpected results:

1. Read the error message carefully — note the HTTP status code and error type.
2. Apply the targeted fix from the table below.
3. Retry the operation.
4. Repeat up to 3 times total; after 3 failed attempts, record the failure in `summary.md`.

### Common Fixes

| Error | Fix |
|-------|-----|
| `AuthenticationFailed` | Verify `AZURE_OPENAI_API_KEY` / Speech key is set and correct |
| `ResourceNotFound` (404) | Check the index name, endpoint URL, and resource group |
| `QuotaExceeded` (429) | Wait and retry, or switch to a different region/tier |
| `InvalidRequest` on vector search | Ensure the index has a vector field and vectorizer configured |
| MCP tool unavailable | Fall back to Azure CLI or Python SDK (see Option B in each step) |
| `az login` required | Run `az login --use-device-code` or set `AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_TENANT_ID` |

## Step 8: Write Output Results

After completing the requested Azure AI operations, write findings to the results directory:

```bash
mkdir -p /app/results

# Write azure_ai_output.md with operation results
cat > /app/results/azure_ai_output.md << 'EOF'
# Azure AI Operation Results

## Service Used
<!-- e.g., AI Search, Speech, OpenAI, Document Intelligence -->

## Operation Performed
<!-- e.g., semantic search query, speech transcription -->

## Results
<!-- Paste or describe output here -->

## Metadata
- Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Region: <AZURE_REGION>
EOF
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/azure_ai_output.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Correct Azure AI service identified and used
- [ ] Operations completed successfully (no unresolved errors)
- [ ] `azure_ai_output.md` contains the operation results
- [ ] `summary.md` describes what was done and any issues
- [ ] `validation_report.json` has `overall_passed: true` (or `false` with reasons)

**If ANY item fails, go back to the relevant step and fix it.**

## Tips

- **Prefer MCP over CLI.** When `azure__search` or `azure__speech` MCP tools are available, use them — they handle authentication and endpoint resolution automatically.
- **Check index configuration first.** For AI Search, always call `search_index_list` then `search_index_get` before querying to understand the schema and which fields support vector search.
- **Neural voices for TTS.** Azure Speech neural voices produce significantly more natural output; specify `voice_name="en-US-AriaNeural"` (or similar) when calling `speech_synthesize`.
- **Hybrid search outperforms either alone.** For most search tasks, `search_mode=hybrid` gives the best relevance by combining BM25 keyword scoring with vector similarity.
- **SDK Quick References.** For language-specific SDK patterns, the source skill at `https://skills.sh/microsoft/azure-skills/azure-ai` links to condensed guides for Python, TypeScript, .NET, and Java.
- **Region matters.** Some models and features (e.g., `gpt-4o`) may only be available in specific Azure regions. Default to `eastus` or `swedencentral` for broadest model availability.
