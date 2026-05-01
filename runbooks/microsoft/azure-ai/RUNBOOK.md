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

This runbook guides an agent through working with Azure AI Services, including Azure AI Search, Azure Speech, Azure OpenAI, and Azure Document Intelligence. Use this runbook when you need to perform full-text search, vector search, hybrid search, speech-to-text, text-to-speech, transcription, OCR, or interact with GPT models and embeddings on Azure. The runbook covers both MCP-based access (preferred) and direct SDK/CLI approaches across Python, TypeScript, and .NET. It validates that required outputs are produced and the correct Azure services have been queried.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the run: services used, operations performed, outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/operation_results.json` | Results of each Azure AI operation performed (search queries, speech, etc.) |

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Azure subscription | *(required)* | Azure subscription ID or name |
| Azure resource group | *(required)* | Resource group containing Azure AI resources |
| Search service name | *(optional)* | Azure AI Search service name |
| Speech resource name | *(optional)* | Azure AI Speech resource name |
| OpenAI resource name | *(optional)* | Azure OpenAI resource name |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `azure-cli` (`az`) | CLI | Yes | Azure CLI for resource management and authentication |
| `azure__search` MCP tool | MCP | Optional | Azure MCP server tool for AI Search (preferred when available) |
| `azure__speech` MCP tool | MCP | Optional | Azure MCP server tool for Speech (preferred when available) |
| `azure-search-documents` | Python package | Optional | Python SDK for Azure AI Search |
| `azure-cognitiveservices-speech` | Python package | Optional | Python SDK for Azure Speech |
| `openai` | Python package | Optional | Python SDK for Azure OpenAI |
| `azure-ai-formrecognizer` | Python package | Optional | Python SDK for Document Intelligence |

---

## Step 1: Environment Setup

Verify prerequisites and authenticate with Azure.

```bash
# Verify Azure CLI is available
command -v az >/dev/null || { echo "ERROR: az CLI not installed"; exit 1; }

# Check Azure authentication
az account show >/dev/null 2>&1 || { echo "ERROR: Not logged in to Azure. Run: az login"; exit 1; }

# Show active subscription
az account show --query "{name:name, id:id, state:state}" -o table

# Create results directory
mkdir -p /app/results

# Check for MCP tools availability
if command -v azure >/dev/null 2>&1; then
  echo "Azure MCP tools available"
else
  echo "Azure MCP not detected — will use SDK/CLI directly"
fi
```

Install Python SDK packages as needed:

```bash
pip install azure-search-documents azure-cognitiveservices-speech openai azure-ai-formrecognizer azure-identity -q
```

---

## Step 2: Determine Available Azure AI Services

Enumerate the Azure AI resources available in the target subscription and resource group.

### Using Azure MCP (Preferred)

If `azure__search` MCP is enabled:
- Use `azure__search` with command `search_index_list` to list available search indexes
- Use `azure__search` with command `search_index_get` to inspect index schema

If `azure__speech` MCP is enabled:
- Use `azure__speech` with command `speech_transcribe` for speech-to-text
- Use `azure__speech` with command `speech_synthesize` for text-to-speech

**If Azure MCP is not enabled:** Run `/azure:setup` or enable via `/mcp`, then re-run.

### Using Azure CLI (Fallback)

```bash
# List Cognitive Services / AI resources
az cognitiveservices account list --query "[].{name:name, kind:kind, location:location}" -o table

# List AI Search services
az search service list --resource-group "$RESOURCE_GROUP" --query "[].{name:name, sku:sku.name, status:provisioningState}" -o table 2>/dev/null || echo "No search services found or az search extension not installed"
```

---

## Step 3: AI Search Operations

Use Azure AI Search for full-text, vector, or hybrid search scenarios.

### Service Capabilities

| Feature | Description |
|---------|-------------|
| Full-text search | Linguistic analysis, stemming |
| Vector search | Semantic similarity with embeddings |
| Hybrid search | Combined keyword + vector |
| AI enrichment | Entity extraction, OCR, sentiment |

### Via MCP (Preferred)

```
azure__search search_index_list    → list available indexes
azure__search search_index_get     → get index schema and field definitions
azure__search search_query         → execute a search query against an index
```

### Via Python SDK

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

service_endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
credential = AzureKeyCredential(SEARCH_API_KEY)

search_client = SearchClient(
    endpoint=service_endpoint,
    index_name=INDEX_NAME,
    credential=credential
)

# Full-text search
results = search_client.search(search_text="your query here", top=5)
for result in results:
    print(result)

# Vector search
from azure.search.documents.models import VectorizedQuery
vector_query = VectorizedQuery(vector=YOUR_EMBEDDING, k_nearest_neighbors=5, fields="content_vector")
results = search_client.search(search_text=None, vector_queries=[vector_query])
```

### Via Azure CLI

```bash
az search query-key list --resource-group "$RESOURCE_GROUP" --service-name "$SEARCH_SERVICE_NAME" -o table
```

---

## Step 4: Speech Operations

Use Azure AI Speech for speech-to-text and text-to-speech scenarios.

### Service Capabilities

| Feature | Description |
|---------|-------------|
| Speech-to-text | Real-time and batch transcription |
| Text-to-speech | Neural voices, SSML support |
| Speaker diarization | Identify who spoke when |
| Custom models | Domain-specific vocabulary |

### Via MCP (Preferred)

```
azure__speech speech_transcribe    → transcribe audio file or stream to text
azure__speech speech_synthesize    → synthesize text to speech audio
```

### Via Python SDK

```python
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

# Speech to text
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
result = speech_recognizer.recognize_once_async().get()
print(f"Recognized: {result.text}")

# Text to speech
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
result = synthesizer.speak_text_async("Hello from Azure Speech.").get()
```

---

## Step 5: Azure OpenAI Operations

Use Azure OpenAI for GPT models, embeddings, and DALL-E image generation.

### Via Python SDK

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01"
)

# Chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)

# Embeddings
embedding = client.embeddings.create(
    model="text-embedding-ada-002",
    input="Your text here"
)
print(embedding.data[0].embedding[:5])
```

### Via Azure CLI

```bash
az cognitiveservices account show --name "$OPENAI_RESOURCE" --resource-group "$RESOURCE_GROUP"
```

---

## Step 6: Document Intelligence (OCR) Operations

Use Azure Document Intelligence for form extraction and OCR.

### Via Python SDK

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

client = DocumentAnalysisClient(
    endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
    credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
)

with open("document.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-read", f)
result = poller.result()

for page in result.pages:
    for line in page.lines:
        print(line.content)
```

---

## Step 7: Iterate on Errors (max 3 rounds)

If any operation in Steps 2–6 fails or produces unexpected results:

1. Read the error message and identify the failing component
2. Apply the targeted fix from the Common Fixes table below
3. Re-run the failed step
4. Validate the output
5. Repeat up to 3 times total

After 3 rounds, if the operation still fails, log the failure in `operation_results.json` and continue to the next step.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `AuthenticationError` | Re-run `az login` or verify API keys in environment variables |
| `ResourceNotFound` | Verify resource name and resource group; use `az cognitiveservices account list` to enumerate |
| MCP tools not available | Run `/azure:setup` to configure Azure MCP server |
| Search index not found | List indexes with `azure__search search_index_list` or `az search index list` |
| Speech region mismatch | Check region in Azure portal; update `SPEECH_REGION` variable |
| Rate limit / quota exceeded | Add retry logic with exponential backoff; check quotas in Azure portal |

---

## Step 8: Collect and Write Operation Results

Aggregate results from all operations performed and write to the output files.

```python
import json, pathlib
from datetime import datetime, timezone

operation_results = {
    "run_date": datetime.now(timezone.utc).isoformat(),
    "operations": [
        # Each entry: {"service": "...", "operation": "...", "status": "pass|fail", "result_summary": "..."}
    ],
    "overall_status": "pass"
}

pathlib.Path('/app/results/operation_results.json').write_text(
    json.dumps(operation_results, indent=2), encoding='utf-8'
)
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
  "$RESULTS_DIR/operation_results.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] Azure authentication confirmed (Step 1)
- [ ] Available Azure AI services enumerated (Step 2)
- [ ] AI Search operations completed or skipped with reason (Step 3)
- [ ] Speech operations completed or skipped with reason (Step 4)
- [ ] Azure OpenAI operations completed or skipped with reason (Step 5)
- [ ] Document Intelligence operations completed or skipped with reason (Step 6)
- [ ] `operation_results.json` written with per-service outcomes
- [ ] `summary.md` written with run overview
- [ ] `validation_report.json` written with `overall_passed` field
- [ ] Verification script printed PASS for every required output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Prefer MCP tools when available.** The `azure__search` and `azure__speech` MCP tools provide a higher-level interface and handle authentication automatically. Only fall back to SDK/CLI if MCP is unavailable.
- **Use `az login --use-device-code` in non-interactive environments** to authenticate without a browser.
- **Check SKU and region limits.** Azure AI services have per-region quotas; if you hit rate limits, switch to a different region or request quota increases.
- **Vector search requires embeddings.** To perform vector or hybrid search on Azure AI Search, you must first generate embeddings using Azure OpenAI (`text-embedding-ada-002`) or another embedding model.
- **Document Intelligence supports pre-built and custom models.** Use `prebuilt-read` for general OCR, `prebuilt-invoice` for invoices, or train a custom model for domain-specific forms.
- **Speaker diarization is a Speech service add-on.** Enable it in the `SpeechConfig` before starting a recognition session.
