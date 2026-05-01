---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/microsoft-foundry"
  source_host: "skills.sh"
  source_title: "Microsoft Foundry Skill"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "microsoft-foundry"
    confidence: "high"
secrets: {}
---

# Microsoft Foundry Skill — Agent Runbook

## Objective

This runbook operationalizes the Microsoft Foundry Skill for Jetty-deployed agents. It covers the full developer lifecycle for Azure AI Foundry resources: model discovery and deployment, complete end-to-end lifecycle of AI agents (Docker build, ACR push, hosted and prompt agent creation, container management), batch and continuous evaluation workflows, prompt optimizer pipelines, RBAC and quota management, and troubleshooting. Agents following this runbook must consult the Azure MCP `foundry` tool as their entry point for all Foundry-related operations before executing any workflow step. Use this runbook for: deploying agents to Foundry, creating hosted agents, invoking agents, running evaluations, optimizing prompts, managing models, projects, RBAC, and capacity. Do NOT use for: Azure Functions, App Service, or general Azure deployment tasks (use `azure-deploy` or `azure-prepare` skills instead).

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the run: agent context, steps executed, sub-skill used, outcome |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/agent_context.json` | Resolved agent context: agent root, metadata file, environment, project endpoint, agent name |
| `/app/results/workflow_output.md` | Output of the specific workflow executed (deploy, invoke, observe, etc.) |
| `/app/results/sub_skill_used.txt` | Name of the sub-skill loaded and executed (e.g. `deploy`, `observe`, `create`) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Agent root | *(required)* | Path to the agent source folder containing `.foundry/agent-metadata*.yaml` |
| Metadata file | `agent-metadata.yaml` | Metadata filename (or sidecar, e.g. `agent-metadata.prod.yaml`) |
| Environment | *(required)* | Target environment key (e.g. `dev`, `prod`) |
| Project endpoint | *(required)* | Azure AI Foundry project endpoint URL |
| Agent name | *(required)* | Name of the target agent |
| Sub-skill | *(required)* | Workflow to execute: `deploy`, `invoke`, `observe`, `trace`, `troubleshoot`, `create`, `eval-datasets`, `project/create`, `resource/create`, `models/deploy-model`, `quota`, `rbac` |
| Dry run | `false` | If `true`, validate configuration without executing live Azure operations |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` CLI | CLI | Yes | Azure CLI for resource provisioning, RBAC, and quota management |
| `azd` CLI | CLI | Recommended | Azure Developer CLI for environment bootstrapping (`azd env get-values`) |
| `docker` | CLI | For deploy | Docker for containerizing hosted agent images |
| Azure MCP `foundry` tool | MCP | Yes | Primary entry point for all Foundry MCP operations |
| `ask_user` / `askQuestions` tool | MCP | Yes | Collect missing configuration values from the user |
| `task` / `runSubagent` tool | MCP | Recommended | Delegate long-running or independent sub-tasks |
| `.foundry/agent-metadata.yaml` | File | Yes | Agent metadata file with environment configurations |
| Azure AI Foundry project | Cloud | Yes | Active Foundry project with appropriate RBAC permissions |

---

## Step 1: Environment Setup

Verify the required tools are available and the Azure session is authenticated.

```bash
echo "=== Foundry Skill — Environment Check ==="
command -v az   >/dev/null 2>&1 && echo "PASS: az CLI found"   || echo "WARN: az CLI not found — install Azure CLI"
command -v azd  >/dev/null 2>&1 && echo "PASS: azd found"      || echo "INFO: azd not found — optional for bootstrapping"
command -v docker >/dev/null 2>&1 && echo "PASS: docker found" || echo "INFO: docker not found — required for hosted agent deploy"

# Verify Azure login
az account show >/dev/null 2>&1 && echo "PASS: Azure session active" || { echo "FAIL: Not logged in to Azure"; exit 1; }
az account show --query "{subscription:id, name:name}" -o json

mkdir -p /app/results
echo "Results dir ready: /app/results"
```

---

## Step 2: Discover Foundry MCP Entry Point

**MANDATORY**: Before executing any workflow-specific steps, call the Azure MCP `foundry` tool to discover available Foundry MCP tools and their parameters. Treat this as a discovery/help step.

```
# Pseudo-code — use the MCP tool interface
foundry_tools = mcp_call("foundry", action="list_tools")
print(foundry_tools)
```

Record the list of available tools to inform which MCP calls are valid for subsequent steps.

---

## Step 3: Load Sub-Skill Document

**MANDATORY**: Before executing workflow-specific steps, read the corresponding sub-skill document. Do not call workflow-specific MCP tools without first reading its skill document.

Match user intent to the correct sub-skill:

| User Intent | Sub-Skill to Load |
|-------------|------------------|
| Create a new agent from scratch | `create` → `deploy` → `invoke` |
| Deploy an agent (code exists) | `deploy` → `invoke` |
| Update/redeploy after code changes | `deploy` → `invoke` |
| Invoke/test/chat with an agent | `invoke` |
| Optimize / improve prompt or instructions | `observe` (Step 4: Optimize) |
| Evaluate and optimize (full loop) | `observe` |
| Enable continuous evaluation monitoring | `observe` (Step 6: CI/CD & Monitoring) |
| Troubleshoot agent issue | `invoke` → `troubleshoot` |
| Fix broken agent | `invoke` → `troubleshoot` → apply fixes → `deploy` → `invoke` |
| Deploy a model | `models/deploy-model` |
| Create Foundry project | `project/create` |
| Create AI Services resource | `resource/create` |
| Manage RBAC/permissions | `rbac` |
| Manage quota/capacity | `quota` |
| Dataset operations from traces | `eval-datasets` |

Write the chosen sub-skill name to `/app/results/sub_skill_used.txt`.

---

## Step 4: Resolve Agent Context

Run context resolution only for values not already provided by the user.

### Step 4a: Discover Agent Roots

Search the workspace for `.foundry/` folders containing `agent-metadata.yaml` or `agent-metadata.<env>.yaml`:

```bash
find . -type f -name "agent-metadata*.yaml" -path "*/.foundry/*" 2>/dev/null
```

- **One match** → use that agent root automatically.
- **Multiple matches** → ask the user to select the target agent folder.
- **No matches** → for `create`/`deploy`: seed a new `.foundry/` folder; for all other workflows: stop and ask which agent folder to initialize.

### Step 4b: Select Metadata File and Environment

Priority order for metadata file selection:
1. File explicitly named by the user or workflow
2. `agent-metadata.<env>.yaml` if an environment is already known
3. `agent-metadata.yaml` (default)
4. Prompt user if multiple candidates remain

Priority order for environment selection:
1. Explicitly named by the user
2. Single environment defined in metadata file
3. Environment already selected earlier in the session
4. `defaultEnvironment` from metadata
5. Prompt user if multiple environments and no rule applies

### Step 4c: Resolve Configuration Values

| Metadata Field | Resolves To | Used By |
|----------------|-------------|---------|
| `environments.<env>.projectEndpoint` | Project endpoint URL | deploy, invoke, observe, trace, troubleshoot |
| `environments.<env>.agentName` | Agent name | invoke, observe, trace, troubleshoot |
| `environments.<env>.azureContainerRegistry` | ACR registry name / image URL prefix | deploy |
| `environments.<env>.evaluationSuites[]` | Dataset + evaluator + tag bundles | observe, eval-datasets |

### Step 4d: Bootstrap from azd (Create/Deploy only)

If metadata fields are still missing and `azure.yaml` exists in the project root, run:

```bash
azd env get-values
```

Seed `agent-metadata.yaml` with:
- `AZURE_AI_PROJECT_ENDPOINT` / `AZURE_AIPROJECT_ENDPOINT` → `environments.<env>.projectEndpoint`
- `AZURE_CONTAINER_REGISTRY_NAME` / `AZURE_CONTAINER_REGISTRY_ENDPOINT` → `environments.<env>.azureContainerRegistry`
- `AZURE_SUBSCRIPTION_ID` → subscription for trace/troubleshoot

Write the resolved context to `/app/results/agent_context.json`:

```json
{
  "agent_root": "<resolved>",
  "metadata_file": "<resolved>",
  "environment": "<resolved>",
  "project_endpoint": "<resolved>",
  "agent_name": "<resolved>",
  "acr_registry": "<resolved or null>",
  "sub_skill": "<chosen sub-skill>"
}
```

---

## Step 5: Execute Sub-Skill Workflow

Execute the workflow defined by the sub-skill loaded in Step 3. Follow the sub-skill document exactly — do not skip pre-checks or validation logic.

### Workspace Standard

Maintain the `.foundry/` workspace structure:

```text
<agent-root>/
  .foundry/
    agent-metadata.yaml
    agent-metadata.prod.yaml   (optional sidecar)
    datasets/                  (local cache — reuse when current)
    evaluators/                (local cache — reuse when current)
    results/
```

### Agent Types

| Type | Kind | Notes |
|------|------|-------|
| **Prompt** | `"prompt"` | LLM-based agent backed by a model deployment |
| **Hosted** | `"hosted"` | Container-based agent running custom code |

Use the `agent_get` MCP tool to determine an agent's type when needed.

### Metadata Write Rules

On any metadata write (deploy, auto-setup, dataset refresh, trace-to-dataset update):
- Persist only `evaluationSuites[]` in the selected metadata file
- If single-environment file: rewrite only that environment block
- If multi-environment file: rewrite only the selected environment block
- Never copy or merge environments across sibling files automatically
- Migrate legacy `testSuites[]` / `testCases[]` → `evaluationSuites[]` format
- Map legacy `priority` to `tags.tier` only when `tags.tier` is missing: `P0` → `smoke`, `P1` → `regression`, `P2` → `coverage`

Write workflow output to `/app/results/workflow_output.md`.

---

## Step 6: Iterate on Errors (max 3 rounds)

If any workflow step fails:

1. Read the error message from the MCP tool or CLI output.
2. Apply the targeted fix from the table below.
3. Re-run the failed step.
4. Repeat up to 3 times.

After 3 rounds, if still failing: write the failure into `summary.md` and `validation_report.json`, then exit with `overall_passed=false`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `foundry` MCP tool not found | Verify Azure MCP server is running; check MCP server connection |
| Agent metadata not found | Run discovery in Step 4a; create `.foundry/` workspace if needed |
| Project endpoint invalid | Re-resolve from `azd env get-values` or ask user for correct URL |
| ACR auth failure | Run `az acr login --name <registry>` before docker push |
| Agent not found by name | Use `agent_get` to list agents; verify `agentName` in metadata |
| Quota insufficient | Load `quota` sub-skill; check capacity in target region |
| RBAC permission denied | Load `rbac` sub-skill; assign correct role to identity |
| Evaluation suite not found | Refresh datasets cache; re-run `eval-datasets` sub-skill |

---

## Step 7: Write Executive Summary

Write `/app/results/summary.md` with the run outcome, sub-skill used, agent context, and any issues.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/agent_context.json" \
  "$RESULTS_DIR/workflow_output.md" \
  "$RESULTS_DIR/sub_skill_used.txt"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] Azure session is active and authenticated
- [ ] `foundry` MCP entry point called and tools listed (Step 2)
- [ ] Sub-skill document loaded before any workflow-specific MCP calls (Step 3)
- [ ] Agent root, metadata file, environment, and project endpoint all resolved (Step 4)
- [ ] Workflow executed per sub-skill document (Step 5)
- [ ] Metadata written in `evaluationSuites[]` format if updated (Step 5)
- [ ] Errors retried up to 3 times with targeted fixes applied (Step 6)
- [ ] `agent_context.json` written with all resolved values
- [ ] `workflow_output.md` written with step-by-step outcome
- [ ] `sub_skill_used.txt` written with the sub-skill name
- [ ] `summary.md` written with run overview and any issues
- [ ] `validation_report.json` written with `overall_passed` field
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Always call `foundry` first.** Treat the initial `foundry` MCP call as a discovery step on every run — tool parameters change across versions.
- **Read sub-skills before acting.** Even if you know the MCP tool parameters, the sub-skill document contains required pre-checks and validation logic that must be followed.
- **Reuse `.foundry/` cache.** `datasets/` and `evaluators/` are local cache folders — reuse when current and ask before refreshing or overwriting.
- **Agent context is session-scoped.** Once agent root, metadata file, and environment are selected, keep them visible in every workflow summary. Do not re-ask for values already resolved.
- **Never scan sibling agent folders.** After selecting an agent root, keep all context inside that folder only unless the user explicitly switches roots.
- **Prompt optimization lives in `observe`.** For "optimize my prompt" or "improve agent instructions" requests, load the `observe` sub-skill and use the `prompt_optimize` MCP tool.
- **Full onboarding flow**: `project/create` → `resource/create` → `create` → `deploy` → `invoke` → `observe`.
- **Model deployment routing**: `models/deploy-model` intelligently routes between quick preset, customized, and capacity-discovery sub-flows.

## Additional Resources

- [Foundry Hosted Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry)
- [Foundry Agent Runtime Components](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/runtime-components?view=foundry)
- [Python SDK Reference](https://github.com/microsoft/azure-skills/blob/HEAD/.github/plugins/azure-skills/skills/microsoft-foundry/references/sdk/foundry-sdk-py.md)
- [Agent Metadata Contract](https://github.com/microsoft/azure-skills/blob/HEAD/.github/plugins/azure-skills/skills/microsoft-foundry/references/agent-metadata-contract.md)
- [Standard Agent Setup](https://github.com/microsoft/azure-skills/blob/HEAD/.github/plugins/azure-skills/skills/microsoft-foundry/references/standard-agent-setup.md)
- [Private Network Setup](https://github.com/microsoft/azure-skills/blob/HEAD/.github/plugins/azure-skills/skills/microsoft-foundry/references/private-network-standard-agent-setup.md)
