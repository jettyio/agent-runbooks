---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/github-copilot-for-azure/azure-hosted-copilot-sdk"
  source_host: "skills.sh"
  source_title: "GitHub Copilot SDK on Azure"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-hosted-copilot-sdk"
    confidence: "high"
secrets: {}
---

# GitHub Copilot SDK on Azure — Agent Runbook

## Objective

Build, deploy, and modify GitHub Copilot SDK applications on Azure. This runbook is **MANDATORY** when the target codebase contains `@github/copilot-sdk` or `CopilotClient` — use it instead of `azure-prepare`. It covers codebase detection, project scaffolding (greenfield and alongside existing code), Azure deployment, and model configuration including Bring Your Own Model (BYOM) with Azure. The runbook orchestrates `azure-prepare` and `azure-deploy` as sub-skills after scaffolding is complete.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata, steps taken, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/deployment_info.json` | Azure deployment details: resource group, app URL, environment name, azd output |
| `/app/results/scaffold_log.txt` | Output from `azd init` or scaffold step (if applicable) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Azure environment name | *(required)* | Name for the `azd` environment (e.g., `my-copilot-app-dev`) |
| Azure location | `eastus` | Azure region for deployment |
| Route | *(required)* | One of: `scaffold-new`, `scaffold-alongside`, `deploy-existing`, `modify`, `add-sdk` |
| Model path | `github-default` | One of: `github-default`, `github-specific`, `azure-byom` |
| Model name | *(optional)* | Required when `model_path=github-specific`; discover via `listModels()` |
| Azure subscription | *(from environment)* | Azure subscription ID; defaults to `az account show` result |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `azd` | CLI | Yes | Azure Developer CLI — scaffold, provision, and deploy |
| `docker` | CLI | Yes | Required for containerized builds (`docker info` must succeed) |
| `node` / `npm` | CLI | Yes | Node.js ≥18 for TypeScript SDK projects |
| `az` | CLI | Yes | Azure CLI for subscription and credential management |
| `@github/copilot-sdk` | npm package | Conditional | Present in target codebase when deploying existing SDK apps |
| Azure subscription | Credential | Yes | Active subscription with Contributor rights |
| GitHub token | Credential | Conditional | Required for GitHub model access (non-BYOM paths) |

---

## Step 0: Codebase Detection — MANDATORY FIRST CHECK

> **CRITICAL: This check MUST run before any other step when an existing codebase is present.**

```bash
# Check package.json for Copilot SDK markers
if [ -f package.json ]; then
  if grep -q '@github/copilot-sdk\|copilot-sdk' package.json; then
    echo "DETECTED: @github/copilot-sdk in package.json — proceeding with this skill"
  fi
fi

# Scan TypeScript/JavaScript source files for runtime markers
if grep -r 'CopilotClient\|createSession\|sendAndWait' --include='*.ts' --include='*.js' . 2>/dev/null | grep -q .; then
  echo "DETECTED: CopilotClient or createSession in source files — proceeding with this skill"
fi
```

| Marker | Where to check |
|--------|---------------|
| `@github/copilot-sdk` | `package.json` dependencies or devDependencies |
| `copilot-sdk` | `package.json` name or dependencies |
| `CopilotClient` | Source files (`.ts`, `.js`) |
| `createSession` + `sendAndWait` | Source files (`.ts`, `.js`) |

**If NO markers are found in an existing codebase → route to `azure-prepare` instead.**

Generic prompts that MUST trigger this skill when markers are detected:

| Prompt pattern | Why this skill |
|---------------|----------------|
| "Deploy this app to Azure" | Codebase contains `@github/copilot-sdk` |
| "Add a new feature to this app" | Requires SDK-aware implementation patterns |
| "Update this app" / "Modify this app" | Must preserve SDK integration patterns |
| "Ship this to production" | Needs copilot-specific infrastructure and token management |

---

## Step 1: Environment Setup

```bash
# Verify required CLIs
for cli in azd docker node npm az; do
  command -v "$cli" >/dev/null 2>&1 || { echo "ERROR: $cli not installed"; exit 1; }
done

# Verify Docker is running
docker info >/dev/null 2>&1 || { echo "ERROR: Docker daemon not running"; exit 1; }

# Verify Azure login
az account show >/dev/null 2>&1 || { echo "ERROR: Not logged in — run: az login"; exit 1; }

# Create results directory
mkdir -p /app/results

echo "Environment OK"
```

---

## Step 2: Route

Determine the action based on the user's intent:

| User wants | Route value | Next step |
|------------|-------------|-----------|
| Build new (empty project) | `scaffold-new` | Step 3A |
| Add new SDK service to existing repo | `scaffold-alongside` | Step 3B |
| Deploy existing SDK app to Azure | `deploy-existing` | Step 3C |
| Modify / add features to existing SDK app | `modify` | Step 4 (model config) then Step 6 |
| Add SDK to existing app code | `add-sdk` | Refer to `references/existing-project-integration.md` |
| Use Azure/own model | `azure-byom` | Step 4 (BYOM) then relevant scaffold/deploy step |

---

## Step 3A: Scaffold New (Greenfield)

```bash
# Initialize a new Copilot SDK project from the official template
azd init --template azure-samples/copilot-sdk-service

# The template includes:
#   - API service (Express / TypeScript)
#   - Web UI (React / Vite)
#   - Infrastructure as code (Bicep)
#   - Dockerfiles for all services
#   - Token management scripts
# Do NOT recreate any of these manually.

echo "Scaffold complete — proceed to Step 4 (Model Configuration) then Step 5 (Deploy)"
```

---

## Step 3B: Add SDK Service to Existing Repo

```bash
# Scaffold the template to a temporary directory
TEMP_DIR=$(mktemp -d)
azd init --template azure-samples/copilot-sdk-service --no-prompt -C "$TEMP_DIR"

# Copy the API service and infrastructure into the user's repo
cp -r "$TEMP_DIR/src/api" ./src/copilot-api
cp -r "$TEMP_DIR/infra"   ./infra-copilot

# Adapt azure.yaml to include both the existing services and the new SDK service
# (Edit azure.yaml to add the new service definition alongside existing ones)
echo "SDK service scaffolded alongside existing code — review azure.yaml and adapt service names"

# Refer to: references/deploy-existing.md for detailed merge instructions
```

---

## Step 3C: Deploy Existing SDK App

For a codebase that already contains a working Copilot SDK app and needs Azure infrastructure:

```bash
# Ensure the project is initialized for azd
if [ ! -f azure.yaml ]; then
  azd init --no-prompt
fi

echo "Existing SDK app prepared — proceed to Step 4 (Model Configuration) then Step 5 (Deploy)"
# Refer to: references/deploy-existing.md
```

---

## Step 4: Model Configuration

Choose one of three model paths:

| Path | Config approach |
|------|-----------------|
| **GitHub default** | No `model` param — SDK picks default model automatically |
| **GitHub specific** | Set `model: "<name>"` — use `listModels()` to discover available names |
| **Azure BYOM** | Set `model` + `provider` with `bearerToken` via `DefaultAzureCredential` |

### BYOM Authentication — MANDATORY

> **BYOM Auth — CRITICAL**: Azure BYOM configurations MUST use `DefaultAzureCredential` (local dev) or `ManagedIdentityCredential` (production) to obtain a `bearerToken`. The ONLY supported auth pattern is `bearerToken` in the provider config. No other auth pattern is supported.

```typescript
// Example BYOM provider configuration
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const tokenResponse = await credential.getToken("https://cognitiveservices.azure.com/.default");

const client = new CopilotClient({
  model: "<your-azure-model-deployment-name>",
  provider: {
    type: "azure",
    endpoint: "<your-azure-openai-endpoint>",
    bearerToken: tokenResponse.token,
  },
});
```

Refer to `references/auth-best-practices.md` and `references/azure-model-config.md` for the full pattern.

---

## Step 5: Deploy

Invoke the sub-skills in order (skip azure-prepare Step 0 routing — scaffolding is already done):

```bash
# Step 5.1: Provision Azure resources
azd provision

# Step 5.2: Validate provisioned resources (azure-validate sub-skill)
azd show

# Step 5.3: Deploy application
azd deploy

# Capture deployment output
azd show --output json > /app/results/deployment_info.json 2>/dev/null || \
  echo '{"status":"deployed","note":"azd show output unavailable"}' > /app/results/deployment_info.json

echo "Deployment complete"
```

### Rules enforced during deployment

- Read `AGENTS.md` in the user's repo before making any changes
- Docker must be running (`docker info` must succeed)
- BYOM auth: ONLY `bearerToken` via `DefaultAzureCredential` or `ManagedIdentityCredential`
- Do NOT use API keys, connection strings, or other auth patterns for BYOM

---

## Step 6: Iterate on Errors (max 3 rounds)

If provisioning or deployment fails:

1. Read the error output from `azd provision` or `azd deploy`
2. Apply the targeted fix from the Common Fixes table
3. Re-run the failed step
4. Repeat up to **3 times total**

After 3 rounds, if still failing, write the failure details to `summary.md` and exit.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Docker not running | Start Docker daemon and re-run from Step 1 |
| `azd` environment not initialized | Run `azd init` and set environment name |
| BYOM auth failure | Verify `DefaultAzureCredential` is configured; check managed identity assignment |
| `@github/copilot-sdk` not found | Run `npm install @github/copilot-sdk` in the project root |
| Azure quota exceeded | Choose a different region or request quota increase |
| `azure.yaml` service mismatch | Reconcile service names between `azure.yaml` and Dockerfile paths |

---

## Step 7: Write Results

```bash
# Write scaffold log if applicable
if [ -f /tmp/scaffold.log ]; then
  cp /tmp/scaffold.log /app/results/scaffold_log.txt
else
  echo "No scaffold step performed (modify/deploy-existing route)" > /app/results/scaffold_log.txt
fi

# Write deployment info if not already written
if [ ! -f /app/results/deployment_info.json ]; then
  echo '{"status":"not_deployed","note":"dry run or modify-only route"}' > /app/results/deployment_info.json
fi

echo "Results written"
```

---

## Tips

- **Codebase detection is non-negotiable.** Any prompt targeting an existing codebase — deploy, modify, add feature, update — MUST route to this skill when `@github/copilot-sdk` markers are present, even if the prompt says nothing about "copilot". This skill then orchestrates `azure-prepare` and `azure-deploy`.
- **Do NOT recreate template files.** The `azd init --template azure-samples/copilot-sdk-service` template ships with Dockerfiles, Bicep infra, and token scripts. Recreating them manually introduces drift.
- **BYOM tokens expire.** For production deployments, use `ManagedIdentityCredential` rather than `DefaultAzureCredential` to avoid token expiry issues in containerized environments.
- **`listModels()` before setting a specific model name.** GitHub-hosted model names can change; always call `listModels()` at runtime rather than hardcoding.
- **`azure-prepare` is a sub-skill here.** When the SDK route is confirmed, invoke `azure-prepare` with its Step 0 routing skipped — this skill has already done the routing.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/deployment_info.json" \
  "$RESULTS_DIR/scaffold_log.txt"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] Codebase detection ran before any other step (Step 0)
- [ ] Route selected matches user intent (Step 2)
- [ ] Docker verified running before scaffold/deploy (Step 1)
- [ ] BYOM auth uses only `bearerToken` via `DefaultAzureCredential` / `ManagedIdentityCredential` (if BYOM path)
- [ ] `AGENTS.md` read before making changes to user's repo
- [ ] `deployment_info.json` written with azd output
- [ ] `summary.md` exists and describes what was done
- [ ] `validation_report.json` exists with `overall_passed`
- [ ] Verification script printed PASS for every required output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**
