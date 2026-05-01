---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-enterprise-infra-planner"
  source_host: "skills.sh"
  source_title: "Azure Enterprise Infra Planner"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-enterprise-infra-planner"
    confidence: "high"
secrets: {}
---

# Azure Enterprise Infra Planner — Agent Runbook

## Objective

Plan, architect, and provision enterprise-scale Azure infrastructure from workload descriptions. This runbook guides a cloud architect or platform engineer through WAF-aligned design of landing zones, hub-spoke networks, multi-region topologies, networking components (VNets, subnets, firewalls, private endpoints, VPN gateways), identity and RBAC setups, and compliance-driven infrastructure. The agent generates deployment-ready Bicep or Terraform code directly (without azd) and executes an approval-gated six-phase workflow from research through deployment. Use `azure-prepare` instead for app-centric workflows.

## REQUIRED OUTPUT FILES (MANDATORY)

**All files below must exist and be non-empty in `/app/results` before the task is complete.**

| File | Description |
|------|-------------|
| `/app/results/infra-plan.json` | Infrastructure plan JSON as specified by `plan-schema.md` |
| `/app/results/iac/` | Directory containing generated Bicep or Terraform files |
| `/app/results/waf-checklist-results.md` | Completed WAF checklist with pass/fail per item |
| `/app/results/deployment-log.txt` | CLI output from `az deployment` or `terraform apply` |
| `/app/results/summary.md` | Executive summary of the planning run, decisions made, and any open issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all artifacts |
| Workload description | *(required)* | Natural-language description of the workload to architect |
| IaC format | `bicep` | `bicep` or `terraform` |
| Target subscription | *(required)* | Azure subscription ID for deployment |
| Target resource group | *(required)* | Resource group name (will be created if absent) |
| Target region | `eastus2` | Primary Azure region |
| DR region | *(optional)* | Secondary region for disaster-recovery topology |
| Approval required | `true` | If `true`, pause for user sign-off before IaC generation and deployment |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Deployment, validation, resource listing |
| `bicep` (via `az bicep`) | CLI | Conditional | Required when IaC format is `bicep` |
| `terraform` | CLI | Conditional | Required when IaC format is `terraform` |
| `get_azure_bestpractices_get` | MCP Tool | Yes | Azure best-practice guidance for code generation and operations |
| `wellarchitectedframework_serviceguide_get` | MCP Tool | Yes | WAF service guides for each Azure service used |
| `microsoft_docs_search` | MCP Tool | Yes | Search Microsoft Learn documentation |
| `microsoft_docs_fetch` | MCP Tool | Yes | Fetch full Microsoft Learn pages by URL |
| `bicepschema_get` | MCP Tool | Conditional | Bicep resource schema (latest API version); required for Bicep mode |
| Azure subscription access | Credential | Yes | Active `az login` session or service principal with Contributor on the target subscription |

## Step 1: Environment Setup

Verify all required tools and credentials are available before planning begins.

```bash
echo "=== Environment Verification ==="
command -v az      >/dev/null && echo "PASS: az found"      || { echo "FAIL: az not installed"; exit 1; }
az bicep install 2>/dev/null || true
command -v terraform >/dev/null && echo "PASS: terraform found" || echo "WARN: terraform not found (required only for terraform mode)"

az account show --output table 2>/dev/null || { echo "FAIL: not logged in to Azure"; exit 1; }
echo "PASS: Azure login active"

mkdir -p /app/results/iac
echo "PASS: output directories ready"
```

If the Azure CLI is not authenticated, run `az login` (interactive) or configure a service principal via environment variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`) before proceeding.

## Step 2: Phase 1 — Research with WAF Tools

Use MCP tools to gather best-practice guidance for every Azure service in scope. Call all applicable tools before moving to Phase 2.

**Required MCP tool calls (adjust service list to match the workload):**

```
get_azure_bestpractices_get        — general Azure infra best practices
wellarchitectedframework_serviceguide_get(service="Virtual Network")
wellarchitectedframework_serviceguide_get(service="Azure Firewall")
wellarchitectedframework_serviceguide_get(service="Azure Bastion")
wellarchitectedframework_serviceguide_get(service="<any other service in scope>")
microsoft_docs_search(query="Azure landing zone design")
microsoft_docs_fetch(url="<relevant Microsoft Learn URL>")
```

**Key gate:** All MCP tool calls must complete (or fail gracefully with a documented fallback) before proceeding. Append findings to `/app/results/work/research-notes.md`.

## Step 3: Phase 2 — Refine & Resource Lookup

Using research findings, enumerate the concrete Azure resources required and present them to the user for approval.

1. List every resource type, SKU, and estimated count.
2. Cross-reference against `references/constraints/` for known pairing constraints and quota limits.
3. Run `microsoft_docs_search` for any resource types with open questions.
4. Use `bicepschema_get` (Bicep mode) to confirm the latest API version for each resource type.

**Present resource list to user and pause.** Do not proceed to plan generation until the user explicitly approves the resource list.

**Key gate:** Resource list approved by user.

## Step 4: Phase 3 — Infrastructure Plan Generation

Generate the infrastructure plan JSON at `/app/results/infra-plan.json` following the schema in `references/plan-schema.md`.

```json
{
  "meta": {
    "status": "draft",
    "created_at": "<ISO-8601>",
    "workload": "<workload description>",
    "regions": ["<primary>"],
    "iac_format": "bicep"
  },
  "resources": [
    {
      "name": "<resource-name>",
      "type": "<Azure resource type>",
      "sku": "<SKU>",
      "region": "<region>",
      "resource_group": "<rg>",
      "dependencies": []
    }
  ],
  "networking": {
    "vnets": [],
    "subnets": [],
    "peerings": [],
    "firewalls": [],
    "private_endpoints": []
  },
  "identity": {
    "rbac_assignments": [],
    "managed_identities": []
  }
}
```

Write the file, then set `meta.status = "draft"`.

**Key gate:** Plan JSON written to disk at `/app/results/infra-plan.json`.

## Step 5: Phase 4 — Verification & Approval

Run all validation checks against the plan before generating IaC:

```bash
# Validate plan JSON is well-formed
python3 -c "import json, sys; json.load(open('/app/results/infra-plan.json')); print('PASS: plan JSON valid')"

# Check for pairing constraint violations (reference constraints/ directory)
# Check that all regions are valid Azure regions
az account list-locations --query "[].name" -o tsv | grep -Fxq "<primary-region>" && echo "PASS: primary region valid" || echo "FAIL: invalid primary region"

# WAF checklist
echo "Complete waf-checklist.md and save results to /app/results/waf-checklist-results.md"
```

**Present verification results to user and pause for sign-off.** Update `meta.status = "approved"` only after user confirms.

**Key gate:** All checks pass AND `meta.status = "approved"`.

## Step 6: Phase 5 — Infrastructure-as-Code Generation

Generate Bicep or Terraform files only after `meta.status = "approved"`.

### Bicep

```bash
# One main.bicep at subscription scope, modules per resource group
mkdir -p /app/results/iac
# Write main.bicep (use bicepschema_get for each resource type's latest API version)
# Validate
az bicep build --file /app/results/iac/main.bicep && echo "PASS: Bicep compiles"
```

### Terraform

```bash
mkdir -p /app/results/iac
# Write main.tf, variables.tf, outputs.tf
terraform -chdir=/app/results/iac init
terraform -chdir=/app/results/iac validate && echo "PASS: Terraform config valid"
terraform -chdir=/app/results/iac plan -out=/app/results/iac/tfplan
```

Fix any validation errors and re-validate before proceeding. Notify user if errors cannot be resolved.

**Key gate:** IaC files at `/app/results/iac/` pass validation with no errors.

## Step 7: Phase 6 — Deployment

Confirm with user before executing any destructive action.

### Bicep deployment

```bash
az deployment sub create \
  --name "jetty-infra-$(date -u +%Y%m%dT%H%M%S)" \
  --location "<primary-region>" \
  --template-file /app/results/iac/main.bicep \
  --parameters @/app/results/iac/main.bicepparam \
  2>&1 | tee /app/results/deployment-log.txt
```

### Terraform deployment

```bash
terraform -chdir=/app/results/iac apply /app/results/iac/tfplan \
  2>&1 | tee /app/results/deployment-log.txt
```

Check exit code. If non-zero, diagnose from the log and surface errors to the user; do not retry blindly.

**Key gate:** User confirms destructive actions; deployment exits 0.

## Step 8: Iterate on Errors (max 3 rounds)

If any phase gate fails (IaC validation, deployment error, WAF checklist failures):

1. Identify the specific failed check from logs or validation output.
2. Apply a targeted fix (see Common Fixes table below).
3. Re-run the affected phase only (not the entire workflow).
4. Repeat up to **max 3 rounds** per phase.
5. If still failing after 3 rounds, surface to user with a clear summary and stop.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `az bicep build` fails | Check for unsupported API version — call `bicepschema_get` to confirm latest stable version and update the template |
| `terraform validate` fails | Fix HCL syntax; check that provider version constraints match the installed provider |
| MCP tool unavailable | Retry once; fall back to `references/` files and note the fallback in the run summary |
| Plan approval missing | `meta.status` is not `approved` — stop and prompt user before proceeding to IaC |
| Pairing constraint violation | Cross-check `references/constraints/`; fix the offending resource combination in the plan |
| Infra files not found | Verify paths under `<project-root>/.azure/` and `/app/results/iac/`; if missing, re-run generation phase |

## Step 9: Write Summary and Validation Report

### Summary

Write `/app/results/summary.md`:

```markdown
# Azure Enterprise Infra Planner — Run Summary

## Overview
- **Date**: <run date>
- **Workload**: <workload description>
- **IaC format**: <bicep|terraform>
- **Primary region**: <region>
- **Status**: <complete|partial|failed>

## Phase Results
| Phase | Status | Notes |
|-------|--------|-------|
| 1 Research WAF Tools | ... | ... |
| 2 Refine & Lookup | ... | ... |
| 3 Plan Generation | ... | ... |
| 4 Verification | ... | ... |
| 5 IaC Generation | ... | ... |
| 6 Deployment | ... | ... |

## Issues / Follow-up
- <Any open issues>
- <Any manual steps required>
```

### Validation Report

Write `/app/results/validation_report.json` with stage-level pass/fail for all phases.

## Final Checklist (MANDATORY — do not skip)

### FINAL OUTPUT VERIFICATION

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/infra-plan.json" \
  "$RESULTS_DIR/iac" \
  "$RESULTS_DIR/waf-checklist-results.md" \
  "$RESULTS_DIR/deployment-log.txt" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -e "$f" ]; then
    echo "FAIL: $f is missing"
  else
    echo "PASS: $f exists"
  fi
done

# Verify plan is approved
STATUS=$(python3 -c "import json; d=json.load(open('$RESULTS_DIR/infra-plan.json')); print(d['meta']['status'])" 2>/dev/null)
[ "$STATUS" = "approved" ] && echo "PASS: plan status=approved" || echo "WARN: plan status=$STATUS (expected approved)"

# Verify IaC validates
if [ -f "$RESULTS_DIR/iac/main.bicep" ]; then
  az bicep build --file "$RESULTS_DIR/iac/main.bicep" 2>/dev/null && echo "PASS: Bicep validates" || echo "FAIL: Bicep validation failed"
elif [ -f "$RESULTS_DIR/iac/main.tf" ]; then
  terraform -chdir="$RESULTS_DIR/iac" validate 2>/dev/null && echo "PASS: Terraform validates" || echo "FAIL: Terraform validation failed"
fi
```

### Checklist

- [ ] `infra-plan.json` exists, is valid JSON, and `meta.status = "approved"`
- [ ] `/app/results/iac/` contains at least one Bicep or Terraform file
- [ ] IaC files pass `az bicep build` or `terraform validate`
- [ ] `waf-checklist-results.md` is complete with all items evaluated
- [ ] `deployment-log.txt` records the deployment output
- [ ] `summary.md` exists with phase results and any open issues
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer subscription-scope Bicep deployments** (`az deployment sub create`) for multi-resource-group topologies — this gives you a single idempotent entry point.
- **Gate on approval strictly.** Never generate IaC or deploy without `meta.status = "approved"` — this prevents accidental provisioning of expensive or destructive resources.
- **Use `bicepschema_get` for every resource type.** API versions drift quickly; always confirm the latest stable version before writing templates.
- **Validate before you apply.** Run `az bicep build` or `terraform validate` immediately after generation — catching errors early avoids failed deployments.
- **DR topology requires separate plan review.** If a secondary region is specified, treat the DR resources as a separate section in `infra-plan.json` and require a second user approval gate.
- **MCP tool fallbacks.** If MCP tools are unavailable, fall back to the reference files shipped with the skill (`references/research.md`, `references/waf-checklist.md`, `references/constraints/`) and document the fallback in `summary.md`.
- **Do not use `azd`.** This skill generates Bicep or Terraform directly; `azure-prepare` should be used for app-centric workflows that rely on `azd`.
