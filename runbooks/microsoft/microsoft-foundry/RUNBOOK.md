---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/microsoft-foundry"
  source_host: "skills.sh"
  source_title: "microsoft-foundry"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "microsoft-foundry"
    confidence: "high"
secrets:
  AZURE_SUBSCRIPTION_ID:
    description: "Azure subscription ID for Foundry resource operations"
    required: false
  AZURE_AI_PROJECT_ENDPOINT:
    description: "Azure AI Foundry project endpoint URL"
    required: false
---

# Microsoft Foundry — Agent Runbook

## Objective

This runbook automates end-to-end workflows for Microsoft Foundry agents: Docker build, ACR push, hosted and prompt agent creation, container start, batch evaluation, continuous evaluation, prompt optimizer workflows, agent.yaml management, and dataset curation from traces. It covers the complete AI agent development lifecycle — from provisioning Azure AI Foundry resources and projects, through agent deployment and invocation, to observation, trace analysis, RBAC, quota management, and troubleshooting. Use this runbook when deploying agents to Foundry, managing model deployments, running evaluations, optimizing prompts, or onboarding new Foundry infrastructure.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata, workflow executed, and outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/agent_metadata.yaml` | Written or updated `.foundry/agent-metadata.yaml` for the target agent (if applicable) |
| `/app/results/workflow_log.md` | Step-by-step log of actions taken, MCP tool calls, and results |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Agent root | *(required)* | Path to the agent source folder containing `.foundry/agent-metadata.yaml` |
| Environment | `dev` | Target environment key from agent metadata (`dev`, `prod`, etc.) |
| Workflow | *(required)* | Workflow to execute: `deploy`, `invoke`, `observe`, `trace`, `troubleshoot`, `create`, `eval-datasets`, `project/create`, `resource/create`, `models/deploy-model`, `quota`, `rbac` |
| Project endpoint | *(from metadata or required)* | Azure AI Foundry project endpoint URL |
| Agent name | *(from metadata or required)* | Name of the target Foundry agent |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` | CLI | Yes | Azure CLI for resource provisioning and RBAC |
| `azd` | CLI | Recommended | Azure Developer CLI for environment variable seeding |
| `docker` | CLI | For deploy workflow | Build and push container images |
| Azure MCP `foundry` tool | MCP | Yes | Primary Foundry entry point — must be called before any workflow |
| `ask_user` / `askQuestions` | MCP tool | Yes | Collecting missing configuration values from the user |
| `task` / `runSubagent` | MCP tool | Optional | Delegating long-running or independent sub-tasks |

## Step 1: Environment Setup

### 1.1 Verify Azure MCP Foundry Tool

> **MANDATORY:** Before executing ANY workflow, call the Azure MCP `foundry` tool as a discovery/help step to inspect available Foundry MCP tools and their parameters.

```bash
# Verify az CLI is available
command -v az >/dev/null || { echo "ERROR: Azure CLI not installed"; exit 1; }

# Check Azure login status
az account show || az login

# Optionally verify azd is available for environment seeding
command -v azd >/dev/null && azd env get-values 2>/dev/null || echo "azd not available or not configured"
```

### 1.2 Initialize Results Directory

```bash
mkdir -p /app/results
```

Write the initial workflow log header to `/app/results/workflow_log.md`.

## Step 2: Resolve Agent Context

> Run this step **only when configuration values are not already known** from the user's message or prior session context.

### 2.1 Discover Agent Roots

Search the workspace for `.foundry/` folders containing `agent-metadata.yaml` or `agent-metadata.<env>.yaml`:

- **One match** → use that agent root.
- **Multiple matches** → use `ask_user` to prompt the user to choose.
- **No matches** → for `create`/`deploy` workflows, seed a new `.foundry/` folder; for all other workflows, stop and ask the user which folder to initialize.

### 2.2 Select Metadata File and Resolve Environment

Inside the selected agent root, choose the metadata file in this order:
1. Filename or path explicitly provided by the user
2. `.foundry/agent-metadata.<env>.yaml` if an explicit environment is known and the file exists
3. `.foundry/agent-metadata.yaml`
4. Prompt the user if multiple files remain ambiguous

Resolve environment in this order:
1. Explicitly named by the user
2. The only environment defined in the metadata file
3. Already selected earlier in the session
4. `defaultEnvironment` from metadata
5. Prompt the user

### 2.3 Resolve Common Configuration

| Metadata Field | Resolves To |
|----------------|-------------|
| `environments.<env>.projectEndpoint` | Project endpoint URL |
| `environments.<env>.agentName` | Agent name |
| `environments.<env>.azureContainerRegistry` | ACR registry for deploy workflow |
| `environments.<env>.evaluationSuites[]` | Dataset + evaluator bundles for observe/eval-datasets |

### 2.4 Bootstrap Missing Metadata (Create/Deploy Only)

If initializing a new `.foundry` workspace, check for `azure.yaml` in the project root. If found, run `azd env get-values` and seed `agent-metadata.yaml`:

| azd Variable | Seeds |
|-------------|-------|
| `AZURE_AI_PROJECT_ENDPOINT` or `AZURE_AIPROJECT_ENDPOINT` | `environments.<env>.projectEndpoint` |
| `AZURE_CONTAINER_REGISTRY_NAME` or `AZURE_CONTAINER_REGISTRY_ENDPOINT` | `environments.<env>.azureContainerRegistry` |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription for trace/troubleshoot |

### 2.5 Collect Missing Values (max 3 rounds)

Use `ask_user` or `askQuestions` **only for values not already resolved**:
- Agent root path
- Metadata file
- Environment name
- Project endpoint
- Agent name

## Step 3: Execute Selected Workflow

Read the corresponding sub-skill document **before** calling any workflow-specific MCP tools:

| Workflow | Sub-Skill Document | When to Use |
|----------|--------------------|-------------|
| `deploy` | `foundry-agent/deploy/deploy.md` | Containerize, build, push to ACR, create/update/clone agent deployments |
| `invoke` | `foundry-agent/invoke/invoke.md` | Send messages to an agent, single or multi-turn conversations |
| `observe` | `foundry-agent/observe/observe.md` | Batch evals, failure analysis, prompt optimization, CI/CD monitoring |
| `trace` | `foundry-agent/trace/trace.md` | Query traces, latency/failure analysis via App Insights |
| `troubleshoot` | `foundry-agent/troubleshoot/troubleshoot.md` | View hosted agent logs, diagnose failures |
| `create` | `foundry-agent/create/create.md` | Create new hosted agent applications |
| `eval-datasets` | `foundry-agent/eval-datasets/eval-datasets.md` | Harvest traces into evaluation datasets, version management |
| `project/create` | `project/create/create-foundry-project.md` | Create new Azure AI Foundry project |
| `resource/create` | `resource/create/create-foundry-resource.md` | Provision Azure AI Services multi-service resource |
| `models/deploy-model` | `models/deploy-model/SKILL.md` | Model deployment with intelligent routing |
| `quota` | `quota/quota.md` | Quota usage, increase requests, capacity planning |
| `rbac` | `rbac/rbac.md` | Role assignments, managed identities, service principals |

### Agent Development Lifecycle

Match user intent to the correct workflow sequence:

| User Intent | Workflow Sequence |
|-------------|------------------|
| Create a new agent from scratch | `create` → `deploy` → `invoke` |
| Deploy agent (code already exists) | `deploy` → `invoke` |
| Update/redeploy after code changes | `deploy` → `invoke` |
| Invoke/test/chat with an agent | `invoke` |
| Optimize agent prompt/instructions | `observe` (Step 4: Optimize) |
| Evaluate and optimize (full loop) | `observe` |
| Enable continuous evaluation monitoring | `observe` (Step 6: CI/CD & Monitoring) |
| Troubleshoot an agent issue | `invoke` → `troubleshoot` |
| Fix a broken agent | `invoke` → `troubleshoot` → fixes → `deploy` → `invoke` |

### Agent Workspace Standard

Every agent source folder keeps Foundry-specific state under `.foundry/`:

```text
<agent-root>/
  .foundry/
    agent-metadata.yaml
    agent-metadata.prod.yaml   # optional environment sidecar
    datasets/
    evaluators/
    results/
```

## Step 4: Validate Workflow Execution

After executing the selected workflow, verify:

1. **Deploy**: Agent deployment is listed and in a healthy state via `foundry` MCP tool.
2. **Invoke**: Agent responded to at least one test message without error.
3. **Observe**: Evaluation results are persisted; any regressions flagged.
4. **Create**: `.foundry/agent-metadata.yaml` written with required fields.
5. **Model deploy**: Model deployment visible in the project with correct SKU/capacity.
6. **RBAC**: Role assignment confirmed via `az role assignment list`.
7. **Quota**: Quota report written to results.

Record each check in `/app/results/workflow_log.md`.

## Step 5: Iterate on Errors (max 3 rounds)

If any validation check from Step 4 fails:

1. Identify the specific error (MCP tool response, CLI output, or exception).
2. Apply the targeted fix:

| Issue | Fix |
|-------|-----|
| Missing metadata field | Prompt user via `ask_user`; update `agent-metadata.yaml` |
| ACR login failure | Run `az acr login --name <registry>` and retry |
| Model deployment quota exceeded | Run `quota` workflow to find available capacity/region |
| Agent invocation 4xx error | Check RBAC permissions; run `rbac` workflow |
| Evaluation dataset not found | Run `eval-datasets` workflow to create/refresh |
| Project endpoint URL invalid | Re-resolve from `azd env get-values` or ask user |

3. Retry the failed workflow step.
4. Re-validate with Step 4 criteria.
5. Repeat up to 3 times total.

After 3 rounds, if validation still fails, record the failure in `summary.md` and exit with `overall_passed=false`.

## Step 6: Write Results

### 6.1 Write Workflow Log

Finalize `/app/results/workflow_log.md` with all actions taken, MCP calls, and outcomes.

### 6.2 Write Agent Metadata (if modified)

If `agent-metadata.yaml` was created or updated, copy the final version to `/app/results/agent_metadata.yaml`.

### 6.3 Write Summary

Write `/app/results/summary.md`:

```markdown
# Microsoft Foundry Workflow — Results

## Overview
- **Date**: <run date>
- **Workflow**: <workflow executed>
- **Agent root**: <path>
- **Environment**: <env>
- **Agent name**: <name>
- **Project endpoint**: <endpoint>

## Validation Results
| Check | Status | Notes |
|-------|--------|-------|
| ... | PASS/FAIL | ... |

## Issues / Follow-up
- <any errors encountered>
- <any manual steps required>

## Provenance
- Origin skill: https://skills.sh/microsoft/azure-skills/microsoft-foundry
- Runbook: skill-to-runbook-converter v1.0.0
```

### 6.4 Write Validation Report

Write `/app/results/validation_report.json` with all stage results and `overall_passed`.

## Final Checklist (MANDATORY)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/workflow_log.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

- [ ] `summary.md` exists and documents the workflow outcome
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `workflow_log.md` contains a step-by-step execution record
- [ ] `agent_metadata.yaml` written if agent metadata was created or modified
- [ ] All required validation checks from Step 4 passed (or failures documented)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Always call the `foundry` MCP tool first.** It's the required discovery step — it reveals available operations and their current parameters before any workflow begins.
- **Prefer metadata over prompting.** The `.foundry/agent-metadata.yaml` contract contains most configuration; only use `ask_user` for values genuinely absent from context.
- **Use `task`/`runSubagent` for parallelizable work.** Environment variable scanning, Dockerfile generation, and status polling are all good candidates.
- **Keep `.foundry/` scoped to the selected agent root.** Never scan sibling agent folders unless the user explicitly switches roots.
- **Model deployment is a separate workflow.** For all deployment scenarios (quick preset, fully customized, capacity discovery), use the `models/deploy-model` sub-skill — it routes intelligently among `preset`, `customize`, and `capacity` sub-skills.
- **Prompt optimization lives in `observe`.** For requests like "optimize my prompt" or "improve my agent instructions," load the `observe` sub-skill and use the `prompt_optimize` MCP tool through the eval-driven workflow.
- **Onboarding tip:** For a complete onboarding flow: `project/create` → `resource/create` → `deploy` → `invoke`.
