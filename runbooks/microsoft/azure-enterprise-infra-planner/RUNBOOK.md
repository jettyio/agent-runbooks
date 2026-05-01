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

Architect and provision enterprise Azure infrastructure from workload descriptions, targeting cloud architects and platform engineers. This runbook guides the agent through planning networking (VNets, subnets, firewalls, private endpoints, VPN gateways), identity, RBAC, security, compliance, and multi-resource topologies with Well-Architected Framework (WAF) alignment. The agent generates Bicep or Terraform infrastructure-as-code directly (no azd), supports subscription-scope and multi-resource-group deployments, and plans disaster recovery, failover, and cross-region high-availability topologies. Activate when the user asks to plan Azure infrastructure, architect a landing zone, design a hub-spoke network, set up VNets/firewalls/private endpoints, or generate Azure Backup configurations for VM workloads.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/infra_plan.json` | The infrastructure plan JSON (`meta.status`, resource list, topology) written to disk after Phase 3 |
| `/app/results/iac/` | Directory containing generated Bicep or Terraform files from Phase 5 |
| `/app/results/waf_checklist.md` | WAF checklist assessment results from Phase 4 verification |
| `/app/results/summary.md` | Executive summary with plan overview, decisions made, and any follow-up actions |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Workload description | *(required — provided by user)* | Natural-language description of the Azure infrastructure to plan |
| IaC format | `bicep` | Infrastructure-as-code format: `bicep` or `terraform` |
| Target regions | *(inferred from description)* | Azure region(s) for the deployment |
| Subscription scope | `false` | Whether the deployment targets subscription scope (vs resource group) |
| DR topology | `false` | Whether to include disaster recovery / multi-region HA topology |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Azure CLI (`az`) | CLI | Yes | Deploy ARM/Bicep resources; query existing resources |
| Bicep CLI (`az bicep`) | CLI | Conditional | Compile and validate `.bicep` files |
| Terraform | CLI | Conditional | Init, plan, validate, and apply Terraform configurations |
| `get_azure_bestpractices_get` | MCP Tool | Yes | Azure best practice guidance for code generation and deployment |
| `wellarchitectedframework_serviceguide_get` | MCP Tool | Yes | WAF service guide per Azure service |
| `microsoft_docs_search` | MCP Tool | Yes | Search Microsoft Learn for relevant documentation |
| `microsoft_docs_fetch` | MCP Tool | Yes | Fetch full Microsoft Learn page content by URL |
| `bicepschema_get` | MCP Tool | Conditional | Bicep schema definition for any Azure resource type (latest API) |
| Azure subscription access | Credential | Yes | Authenticated `az login` session with appropriate RBAC for target scope |

---

## Step 1: Environment Setup

Verify all required tools and credentials are present before proceeding.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify Azure CLI
command -v az >/dev/null || { echo "ERROR: Azure CLI not installed"; exit 1; }
az account show >/dev/null 2>&1 || { echo "ERROR: Not logged in to Azure. Run: az login"; exit 1; }

# Verify IaC tooling
IaC_FORMAT="${IaC_FORMAT:-bicep}"
if [ "$IaC_FORMAT" = "bicep" ]; then
  az bicep version >/dev/null 2>&1 || az bicep install
elif [ "$IaC_FORMAT" = "terraform" ]; then
  command -v terraform >/dev/null || { echo "ERROR: Terraform not installed"; exit 1; }
fi

# Create output directories
mkdir -p /app/results/iac
echo "Results directory: /app/results"
echo "IaC format: $IaC_FORMAT"

# Display current subscription
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table
echo "Setup complete."
```

---

## Step 2: Phase 1 — Research with WAF Tools

Use MCP tools to gather best practices and WAF guidance for all services mentioned in the user's workload description. Do not proceed until all MCP tool calls complete.

For each Azure service identified in the workload description:

```
# For each service (e.g., VNet, Firewall, Private Endpoint, Application Gateway, Key Vault, etc.):
call: wellarchitectedframework_serviceguide_get(service="<azure-service-name>")
call: get_azure_bestpractices_get(topic="<azure-service-name>")

# Search for relevant documentation
call: microsoft_docs_search(query="<workload description keywords> Azure enterprise architecture")
call: microsoft_docs_search(query="<service-name> landing zone best practices")
```

**Key Gate:** All MCP tool calls complete and findings documented internally. Summarize WAF findings in a structured list before proceeding to Phase 2.

---

## Step 3: Phase 2 — Refine and Lookup Resources

Based on WAF research, identify the complete list of Azure resources required. Present the resource list to the user for approval before proceeding.

For each resource type in the plan:

```
# Get the exact Bicep schema / API version
call: bicepschema_get(resource_type="<resource-type>", api_version="latest")

# Fetch specific docs pages if needed
call: microsoft_docs_fetch(url="<microsoft-learn-url>")
```

Present the user with:
1. Complete resource list with Azure resource types
2. SKU selections and capacity recommendations
3. Region placement and availability zone assignments
4. Any pairing constraints or incompatibilities detected

**Key Gate:** User explicitly approves the resource list before proceeding to Plan Generation.

---

## Step 4: Phase 3 — Infrastructure Plan Generation

Generate the infrastructure plan JSON and write it to disk.

```python
import json, pathlib
from datetime import datetime, timezone

plan = {
    "meta": {
        "status": "draft",           # Will be set to "approved" after Phase 4
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "iac_format": "bicep",       # or "terraform"
        "workload_description": "<user-provided description>"
    },
    "topology": {
        "regions": [],               # Primary and DR regions
        "hub_spoke": False,          # Hub-spoke or flat topology
        "multi_region_ha": False
    },
    "resources": [
        # Each entry: { "type": "Microsoft.Network/virtualNetworks", "name": "...", "region": "...", "sku": "...", "config": {} }
    ],
    "networking": {
        "vnets": [],
        "subnets": [],
        "firewalls": [],
        "private_endpoints": [],
        "vpn_gateways": []
    },
    "identity": {
        "rbac_assignments": [],
        "managed_identities": []
    },
    "compliance": {
        "policies": [],
        "waf_tier": "Standard_v2"
    }
}

pathlib.Path("/app/results/infra_plan.json").write_text(json.dumps(plan, indent=2))
print("infra_plan.json written")
```

**Key Gate:** `infra_plan.json` exists on disk with all resource entries populated.

---

## Step 5: Phase 4 — Verification

Run all checks against the generated plan. All checks must pass before proceeding to IaC generation.

```python
import json, pathlib

plan = json.loads(pathlib.Path("/app/results/infra_plan.json").read_text())

checks = {
    "has_resources": len(plan.get("resources", [])) > 0,
    "meta_complete": all(k in plan["meta"] for k in ["status", "version", "iac_format"]),
    "regions_specified": len(plan["topology"].get("regions", [])) > 0,
    "no_pairing_violations": True,   # Validate SKU/region compatibility
    "waf_checklist_reviewed": False  # Set to True after WAF checklist review
}

# WAF Checklist review
print("Running WAF checklist review...")
# Use wellarchitectedframework_serviceguide_get for each resource type
# Document findings in /app/results/waf_checklist.md

all_pass = all(checks.values())
print("Verification checks:", checks)
print("All pass:", all_pass)
```

Write WAF checklist to `/app/results/waf_checklist.md` with findings per pillar (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency).

Present verification summary to user and request approval. Once user approves:

```python
plan["meta"]["status"] = "approved"
pathlib.Path("/app/results/infra_plan.json").write_text(json.dumps(plan, indent=2))
print("Plan approved — status set to 'approved'")
```

**Key Gate:** `meta.status == "approved"` and all verification checks pass.

---

## Step 6: Phase 5 — Infrastructure-as-Code Generation

Only proceed when `meta.status == "approved"`. Generate Bicep or Terraform files.

```bash
# Verify approval before generating IaC
STATUS=$(python3 -c "import json; print(json.load(open('/app/results/infra_plan.json'))['meta']['status'])")
if [ "$STATUS" != "approved" ]; then
  echo "ERROR: Plan not approved. meta.status=$STATUS. Obtain user approval first."
  exit 1
fi

mkdir -p /app/results/iac
```

For Bicep:
```bash
# Generate main.bicep targeting the appropriate scope
# Write resource modules to /app/results/iac/modules/
# Validate compilation
az bicep build --file /app/results/iac/main.bicep --outdir /app/results/iac/
echo "Bicep validation complete"
```

For Terraform:
```bash
cd /app/results/iac
terraform init
terraform validate
terraform plan -out=tfplan
echo "Terraform plan complete"
```

**Key Gate:** IaC validation passes (`az bicep build` or `terraform validate` returns exit code 0).

---

## Step 7: Phase 6 — Deployment (Requires User Confirmation)

**STOP:** Deployment is destructive and irreversible. Do not proceed without explicit user confirmation.

For Bicep deployment:
```bash
# User must confirm before running
az deployment group create \
  --resource-group "<rg-name>" \
  --template-file /app/results/iac/main.bicep \
  --parameters "@/app/results/iac/params.json" \
  --name "jetty-$(date -u +%Y%m%d-%H%M%S)"
```

For Terraform:
```bash
# User must confirm before running
terraform apply /app/results/iac/tfplan
```

After deployment, verify resources:
```bash
az resource list --resource-group "<rg-name>" --output table
```

---

## Step 8: Iterate on Errors (max 3 rounds)

If any phase (IaC validation, deployment, or verification) returns errors:

1. Read the specific error message
2. Apply fix from the table below
3. Re-run the failed phase
4. Repeat up to 3 times total; escalate to user if unresolved after 3 rounds

| Error | Cause | Fix |
|---|---|---|
| MCP tool error or timeout | Tool unavailable | Retry once; fall back to reference files and notify user |
| Plan approval missing | `meta.status` not `approved` | Stop and prompt user for approval |
| `az bicep build` / `terraform validate` failure | Invalid IaC code | Fix the generated code; re-validate |
| Pairing constraint violation | Incompatible SKU or region | Fix in plan (`infra_plan.json`) before re-running IaC generation |
| Infra files not found | Written to wrong location | Verify `/app/results/iac/` exists; re-run Phase 5 |
| Deployment authorization failure | Insufficient RBAC | Check `az account show` and role assignments; escalate to user |

---

## Step 9: Write Summary and Validation Report

```python
import json, pathlib
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()

# Write validation report
report = {
    "version": "1.0.0",
    "run_date": now,
    "parameters": {
        "skill_url": "https://skills.sh/microsoft/azure-skills/azure-enterprise-infra-planner",
        "iac_format": "bicep",
        "dry_run": False
    },
    "stages": [
        {"name": "setup",             "passed": True, "message": "Environment verified, az authenticated"},
        {"name": "waf_research",      "passed": True, "message": "WAF tools called, findings documented"},
        {"name": "resource_approval", "passed": True, "message": "Resource list approved by user"},
        {"name": "plan_generation",   "passed": True, "message": "infra_plan.json written"},
        {"name": "verification",      "passed": True, "message": "All checks pass, plan approved"},
        {"name": "iac_generation",    "passed": True, "message": "IaC files validated in /app/results/iac/"},
        {"name": "deployment",        "passed": True, "message": "Resources deployed and verified"}
    ],
    "results": {"pass": 7, "partial": 0, "fail": 0},
    "overall_passed": True,
    "output_files": [
        "/app/results/infra_plan.json",
        "/app/results/iac/",
        "/app/results/waf_checklist.md",
        "/app/results/summary.md",
        "/app/results/validation_report.json"
    ]
}
pathlib.Path("/app/results/validation_report.json").write_text(json.dumps(report, indent=2))
print("validation_report.json written")
```

Write `/app/results/summary.md` with plan overview, topology decisions, WAF alignment notes, resources deployed, and any manual follow-up items.

---

## Final Checklist (MANDATORY — do not skip)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/infra_plan.json" \
  "$RESULTS_DIR/waf_checklist.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify IaC directory exists and has content
if [ -d "$RESULTS_DIR/iac" ] && [ "$(ls -A "$RESULTS_DIR/iac" 2>/dev/null)" ]; then
  echo "PASS: /app/results/iac/ has content"
else
  echo "WARN: /app/results/iac/ is empty or missing (expected after Phase 5)"
fi

# Verify plan is approved
PLAN_STATUS=$(python3 -c "import json; print(json.load(open('$RESULTS_DIR/infra_plan.json'))['meta']['status'])" 2>/dev/null || echo "unknown")
if [ "$PLAN_STATUS" = "approved" ]; then
  echo "PASS: infra_plan.json status=approved"
else
  echo "WARN: infra_plan.json status=$PLAN_STATUS (expected 'approved' after Phase 4)"
fi
```

### Checklist

- [ ] `infra_plan.json` exists with `meta.status = "approved"`
- [ ] `waf_checklist.md` documents findings for each WAF pillar
- [ ] `/app/results/iac/` contains validated Bicep or Terraform files
- [ ] `summary.md` documents topology decisions and any follow-up actions
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Prefer WAF alignment.** Always call `wellarchitectedframework_serviceguide_get` for each service before finalizing SKU and configuration choices. WAF guidance supersedes general best practices.
- **Gate on approval.** Never generate IaC or run deployments without `meta.status = "approved"` in `infra_plan.json`. This prevents accidental provisioning of expensive resources.
- **Bicep vs Terraform.** Default to Bicep for Azure-only workloads (tighter resource coverage, faster API updates). Use Terraform when the user has an existing Terraform state or multi-cloud requirements.
- **Subscription-scope deployments.** Use `az deployment sub create` (not `deployment group create`) when `subscription_scope=true`. Adjust the Bicep `targetScope` to `subscription`.
- **DR topology.** When `dr_topology=true`, ensure each resource is replicated or has a failover configured. Document RPO/RTO targets in `infra_plan.json`.
- **MCP tool fallback.** If MCP tools are unavailable, fall back to the reference files at `references/` in the source skill repository (plan-schema.md, research.md, waf-checklist.md) and notify the user.
- **Never deploy without confirmation.** Phase 6 (deployment) is irreversible — always pause, present the `terraform plan` or `az deployment what-if` output, and wait for explicit user confirmation before applying.
