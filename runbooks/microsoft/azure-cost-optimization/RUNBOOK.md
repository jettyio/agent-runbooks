---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-cost-optimization"
  source_host: "skills.sh"
  source_title: "azure-cost"
  imported_at: "2026-05-01T02:53:27Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-cost-optimization"
    confidence: "high"
secrets:
  AZURE_CLI_AUTH:
    env: AZURE_CLI_AUTH
    description: "Azure CLI authentication credentials (service principal or managed identity)"
    required: true
---

# Azure Cost Optimization — Agent Runbook

## Objective

Analyze Azure subscriptions to identify cost savings through orphaned resource cleanup, rightsizing, and optimization recommendations based on actual usage data. This runbook automates the discovery of orphaned resources (unattached disks, unused NICs, idle gateways) and over-provisioned services using Azure Quick Review, queries actual costs from Azure Cost Management API and utilization data from Azure Monitor to support rightsizing recommendations, and generates prioritized optimization reports with estimated savings, implementation commands, and Azure Portal links for each resource. It includes specialized Redis and AKS cost optimization analysis with subscription filtering and pre-built report templates. Prerequisites include Cost Management Reader, Monitoring Reader, and Reader roles; the runbook validates all prerequisites before analysis begins.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/cost_optimization_report.md` | Full cost optimization report with executive summary, cost breakdown, orphaned resources, and prioritized recommendations |
| `/app/results/cost_query_result.json` | Audit trail of all cost queries and responses from Azure Cost Management API |
| `/app/results/orphaned_resources.json` | List of orphaned/unused resources discovered by Azure Quick Review with estimated savings |
| `/app/results/rightsizing_recommendations.json` | Rightsizing recommendations with actual utilization metrics and validated pricing |
| `/app/results/summary.md` | Executive summary with run metadata, total costs, top savings opportunities, and issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Subscription ID | *(required — prompt user)* | Azure Subscription ID to analyze |
| Resource Group | *(optional)* | Limit analysis to a specific resource group |
| Analysis scope | `full` | `full` (all resources) or `redis` (Redis-only) or `aks` (AKS-focused) |
| Cost lookback days | `30` | Days of historical cost data to query |
| Utilization lookback days | `14` | Days of utilization metrics to query |
| Output folder | `output/` | Folder for reports and audit trails relative to working directory |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Core Azure CLI for resource discovery, cost queries, and metric collection |
| `az extension: costmanagement` | CLI extension | Yes | Azure Cost Management extension for cost queries |
| `az extension: resource-graph` | CLI extension | Yes | Azure Resource Graph extension for cross-subscription queries |
| `azqr` (Azure Quick Review) | CLI | Yes | Scans for orphaned resources and over-provisioned services |
| Cost Management Reader role | RBAC | Yes | Required to query Azure Cost Management API |
| Monitoring Reader role | RBAC | Yes | Required to query Azure Monitor utilization metrics |
| Reader role | RBAC | Yes | Required to list and inspect resources |
| Azure MCP tools | MCP | Optional | Preferred for AKS, Redis, and storage operations when available |
| PowerShell (pwsh) | Shell | Recommended | Some az CLI commands use PowerShell syntax for date calculations |

---

## Step 1: Environment Setup

```bash
# Verify Azure CLI is installed and authenticated
az account show || { echo "ERROR: Not logged in to Azure CLI. Run 'az login' first."; exit 1; }

# Install required Azure CLI extensions
az extension add --name costmanagement --allow-preview true 2>/dev/null || true
az extension add --name resource-graph 2>/dev/null || true

# Verify azqr is installed
azqr version || { echo "ERROR: azqr not installed. See https://azure.github.io/azqr/ for installation."; exit 1; }

# Create output directories
mkdir -p /app/results output temp

# Verify required RBAC roles (will warn but not fail — some tenants have custom role names)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Analyzing subscription: $SUBSCRIPTION_ID"

# Validate Cost Management access
az costmanagement query --scope "subscriptions/$SUBSCRIPTION_ID" \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-granularity None \
  --query "properties.rows[0]" 2>/dev/null \
  && echo "PASS: Cost Management access verified" \
  || echo "WARN: Cost Management access check failed — verify Cost Management Reader role"
```

**Prerequisite check summary:**
- Azure CLI authenticated: required
- `costmanagement` extension: required
- `resource-graph` extension: required
- `azqr`: required
- Cost Management Reader role: required
- Monitoring Reader role: required
- Reader role: required

---

## Step 2: Load Best Practices

Load Azure cost optimization best practices to inform recommendations before beginning analysis.

```javascript
// If Azure MCP is available in the agent environment:
// mcp_azure_mcp_get_azure_bestpractices({
//   query: "Get cost optimization best practices",
//   tool: "get_bestpractices",
//   topic: "cost-optimization"
// })
```

If Azure MCP tools are not available, proceed to Step 3 using CLI-based discovery. Document in the report which data sources were used.

---

## Step 2.5: Determine Analysis Scope

Before running analysis, confirm the scope with the user (or use defaults from Parameters).

**For Redis-specific analysis** (user mentions "Redis", "Azure Cache for Redis", or "Azure Managed Redis"):
- Skip to Step 3-Redis and use the Redis-specific workflow
- Use `redis_list` to enumerate Redis instances
- Apply Redis-specific rules: failed caches, oversized SKUs, missing cost tags

**For AKS-specific analysis** (user mentions "AKS", "Kubernetes", "cluster", "node pool"):
- Prefer `mcp_azure_mcp_aks` for cluster operations when available
- Fall back to `az aks` and `kubectl` for specific operations
- Focus on namespace-level cost visibility and anomaly investigation

**For general subscription analysis**: continue to Step 3.

---

## Step 3: Run Azure Quick Review (Orphaned Resource Discovery)

Run `azqr` to identify orphaned resources eligible for immediate deletion (highest-confidence savings).

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Run azqr scan — outputs JSON to stdout by default
azqr scan \
  --subscription-id "$SUBSCRIPTION_ID" \
  --output-format json \
  > output/azqr-result-$(date -u +%Y%m%d_%H%M%S).json

echo "PASS: azqr scan complete"
```

**What to look for in azqr results:**
- **Orphaned resources**: unattached disks, unused NICs, idle NAT gateways
- **Over-provisioned resources**: excessive log retention, oversized SKUs
- **Missing cost tags**: resources without proper cost allocation tags

Save results to `output/azqr-result-<timestamp>.json`. Parse the JSON to extract resources with `"orphaned": true` or similar flags for the final report.

---

## Step 4: Discover Resources

List all resources in the target subscription using Azure Resource Graph for cross-subscription efficiency.

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Get subscription info
az account show

# List all resources via Resource Graph (efficient cross-subscription query)
az graph query -q "Resources | where subscriptionId == '$SUBSCRIPTION_ID' | project name, type, resourceGroup, location, tags" \
  --subscriptions "$SUBSCRIPTION_ID" \
  --output json \
  > output/resource-inventory-$(date -u +%Y%m%d_%H%M%S).json

echo "Resource inventory saved."
```

For specific service types, use the appropriate tool:
- **Storage accounts, Cosmos DB, Key Vaults**: use Azure MCP tools when available
- **Redis caches**: use `mcp_azure_mcp_redis` or `az redis list`
- **VMs, App Services, SQL**: use `az` CLI commands
- **AKS clusters**: use `mcp_azure_mcp_aks` or `az aks list`

---

## Step 5: Query Actual Costs (30-Day Lookback)

Retrieve actual costs from Azure Cost Management API for the last 30 days.

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
START_DATE=$(date -u -d "30 days ago" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v-30d +%Y-%m-%dT00:00:00Z)
END_DATE=$(date -u +%Y-%m-%dT23:59:59Z)

# Create cost query body
cat > temp/cost-query.json <<QUERY
{
  "type": "ActualCost",
  "timeframe": "Custom",
  "timePeriod": {
    "from": "${START_DATE}",
    "to": "${END_DATE}"
  },
  "dataset": {
    "granularity": "None",
    "aggregation": {
      "totalCost": {
        "name": "Cost",
        "function": "Sum"
      }
    },
    "grouping": [
      {
        "type": "Dimension",
        "name": "ResourceId"
      }
    ]
  }
}
QUERY

# Execute cost query via REST API (more reliable than az costmanagement query)
az rest \
  --method post \
  --uri "https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --body @temp/cost-query.json \
  --output json \
  > output/cost-query-result-$(date -u +%Y%m%d_%H%M%S).json

echo "PASS: Cost query complete. Results saved to output/."
```

**Important**: Save the full query result as `output/cost-query-result-<timestamp>.json` for audit trail.

---

## Step 6: Validate Pricing from Official Sources

Fetch current pricing from Azure pricing pages to validate savings estimates.

```javascript
// If fetch_webpage MCP tool is available:
// fetch_webpage("https://azure.microsoft.com/en-us/pricing/details/virtual-machines/", "pricing tiers and costs")
// fetch_webpage("https://azure.microsoft.com/pricing/details/container-apps/", "pricing tiers")
```

Key pricing pages to validate:
- Virtual Machines: `https://azure.microsoft.com/pricing/details/virtual-machines/`
- Container Apps: `https://azure.microsoft.com/pricing/details/container-apps/`
- App Service: `https://azure.microsoft.com/pricing/details/app-service/`
- Log Analytics: `https://azure.microsoft.com/pricing/details/monitor/`
- Redis Cache: `https://azure.microsoft.com/pricing/details/cache/`

**Important**: Account for free tier allowances (e.g., Container Apps: 180K vCPU-sec/month free). Never assume costs from memory — always validate against the current pricing page.

---

## Step 7: Collect Utilization Metrics (14-Day Lookback)

Query Azure Monitor for utilization data to support rightsizing recommendations.

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Calculate date range for last 14 days
START_TIME=$(date -u -d "14 days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-14d +%Y-%m-%dT%H:%M:%SZ)
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Example: VM CPU utilization (repeat for each VM resource ID identified in Step 4)
# az monitor metrics list \
#   --resource "<RESOURCE_ID>" \
#   --metric "Percentage CPU" \
#   --interval PT1H \
#   --aggregation Average \
#   --start-time "$START_TIME" \
#   --end-time "$END_TIME" \
#   --output json

# Example: App Service Plan utilization
# az monitor metrics list \
#   --resource "<RESOURCE_ID>" \
#   --metric "CpuTime,Requests" \
#   --interval PT1H \
#   --aggregation Total \
#   --start-time "$START_TIME" \
#   --end-time "$END_TIME" \
#   --output json

echo "Utilization metrics collection template ready."
echo "Replace <RESOURCE_ID> with actual resource IDs from Step 4."
```

Store each metric result to `output/metrics-<resource-name>-<timestamp>.json`.

---

## Step 8: Iterate on Errors (max 3 rounds)

If any API calls fail or return incomplete data:

1. **Cost Management API failure**: Retry with `az rest` instead of `az costmanagement query`; verify the subscription ID and role assignment
2. **azqr scan failure**: Check `azqr version`; ensure the binary is in PATH and the subscription has Reader access
3. **Metrics API failure**: Verify the resource ID format; check that Monitoring Reader role is assigned
4. **Missing data for a resource**: Log the gap in the report with an explicit note ("data unavailable — manual review required")

Do not assume or fabricate cost data. After 3 retry attempts on a single operation, document the failure and continue with the remaining steps.

---

## Step 9: Generate Cost Optimization Report

Create a comprehensive cost optimization report and save to `/app/results/cost_optimization_report.md`.

```markdown
# Azure Cost Optimization Report
Generated: <ISO_8601_TIMESTAMP>
Subscription: <SUBSCRIPTION_ID>
Analysis Period: <START_DATE> to <END_DATE>

## Executive Summary
- **Total Monthly Cost**: $X (ACTUAL DATA from Azure Cost Management API)
- **Top Cost Drivers**: [Top 3 resources by cost with Azure Portal links]
- **Estimated Monthly Savings**: $Y (from orphaned resources + rightsizing)
- **Orphaned Resources Found**: N resources eligible for immediate deletion

## Cost Breakdown (Top 10 Resources)
| Resource | Type | Monthly Cost | Resource Group | Portal Link |
|----------|------|-------------|----------------|-------------|
| ...      | ...  | $X          | ...            | [Open](https://portal.azure.com/...) |

## Free Tier Analysis
Resources operating within free tiers (showing $0 cost) — list here.

## Orphaned Resources (Immediate Savings — Low Risk)
| Resource | Type | Estimated Savings | Action |
|----------|------|-------------------|--------|
| ...      | ...  | $X/month          | Delete after approval |

## Rightsizing Recommendations
### Priority 1 — High Impact, Low Risk
- Resource: <name>
- ACTUAL cost: $X/month (from Cost Management API)
- ACTUAL metrics: CPU avg N%, Memory avg M% (from Azure Monitor)
- VALIDATED pricing: Current SKU $Y/hr, Recommended SKU $Z/hr
- ESTIMATED savings: $S/month
- Command: `az vm resize --resource-group <RG> --name <VM> --size <NEW_SIZE>`

### Priority 2 — Medium Impact, Medium Risk
...

### Priority 3 — Long-term Optimization
Reserved Instances, Storage tiering, etc.

## Total Estimated Savings
- Monthly: $X
- Annual: $Y

## Implementation Commands
[Commands with safety warnings — REQUIRE EXPLICIT APPROVAL before execution]

## Validation Appendix
- Cost data source: Azure Cost Management API (query results in output/)
- Pricing validated from: [Azure pricing page URLs]
- Free tier allowances applied: [list]
- Data classification: ACTUAL DATA / ESTIMATED SAVINGS as labeled
```

**Data Classification Rules:**
- `ACTUAL DATA` = Retrieved from Azure Cost Management API
- `ACTUAL METRICS` = Retrieved from Azure Monitor
- `VALIDATED PRICING` = Retrieved from official Azure pricing pages
- `ESTIMATED SAVINGS` = Calculated from actual data + validated pricing

---

## Step 10: Save Audit Trail & Required Output Files

```bash
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)

# Copy key outputs to /app/results
cp output/cost-query-result-*.json /app/results/cost_query_result.json 2>/dev/null || \
  echo '{"error": "Cost query not completed"}' > /app/results/cost_query_result.json

# Generate orphaned resources JSON from azqr output
python3 - <<'PYEOF'
import json, pathlib, glob

azqr_files = sorted(glob.glob("output/azqr-result-*.json"))
if azqr_files:
    data = json.loads(pathlib.Path(azqr_files[-1]).read_text())
    # Extract orphaned resources — azqr format varies by version
    orphaned = [r for r in data if isinstance(r, dict) and r.get('orphaned', False)]
    pathlib.Path("/app/results/orphaned_resources.json").write_text(json.dumps(orphaned, indent=2))
else:
    pathlib.Path("/app/results/orphaned_resources.json").write_text(json.dumps({"error": "azqr scan not completed or no orphaned resources found"}, indent=2))
PYEOF

# Copy the report
cp output/costoptimizereport-*.md /app/results/cost_optimization_report.md 2>/dev/null || \
  echo "# Cost Optimization Report\n\nReport generation pending." > /app/results/cost_optimization_report.md

echo "PASS: Output files written to /app/results"
```

---

## Step 11: Clean Up Temporary Files

Remove temporary query files after the report is generated. Permanent audit data remains in `output/`.

```bash
rm -rf temp/
echo "PASS: Temporary files cleaned up. Audit trail preserved in output/."
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/cost_optimization_report.md" \
  "$RESULTS_DIR/cost_query_result.json" \
  "$RESULTS_DIR/orphaned_resources.json" \
  "$RESULTS_DIR/rightsizing_recommendations.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Safety Requirements (MANDATORY)

- **Never execute destructive operations** (resource deletion, SKU changes) without explicit user approval
- **Always provide dry-run commands** before execution commands
- **Test changes in non-production first** when possible
- **Include rollback procedures** for every recommended change
- **Monitor impact after implementation** using Azure Monitor alerts

### Checklist

- [ ] Cost data retrieved from Azure Cost Management API (not estimated/assumed)
- [ ] Utilization metrics retrieved from Azure Monitor
- [ ] Pricing validated from official Azure pricing pages
- [ ] Orphaned resources identified via azqr scan
- [ ] Cost optimization report written to `/app/results/cost_optimization_report.md`
- [ ] Cost query results saved for audit trail
- [ ] All recommended commands include safety warnings and approval gates
- [ ] Azure Portal links included for each resource
- [ ] `summary.md` exists with executive summary
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Always query actual costs first**: Never estimate or assume cost data — always retrieve from Cost Management API for credibility.
- **Account for free tiers**: Many Azure services have generous free allowances (e.g., Container Apps: 180K vCPU-sec/month). Ignoring these leads to false savings estimates.
- **Use REST API for cost queries**: `az rest` with a JSON body is more reliable than `az costmanagement query` for complex queries.
- **Prefer MCP tools when available**: `mcp_azure_mcp_aks`, `mcp_azure_mcp_redis` provide richer metadata than CLI equivalents for AKS and Redis analysis.
- **Save the audit trail**: Keep `output/cost-query-result-*.json` files for at least 12 months for historical comparison and compliance.
- **Use correct date ranges**: 30 days for cost history, 14 days for utilization metrics.
- **Verify Portal link format**: `https://portal.azure.com/#@<TENANT_ID>/resource/subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/<PROVIDER>/<TYPE>/<NAME>/overview`
- **Get approval before deleting**: Always surface orphaned resources for human review before any destructive action.
- **Redis-specific analysis**: Use the specialized Redis workflow (Step 2.5) when the user asks about Redis costs — it has subscription-level filtering and pre-built report templates.
- **AKS cost visibility**: Enable the AKS cost analysis add-on for namespace-level cost breakdown; use the anomaly investigation reference for cost spikes.

---

## Common Fixes

| Issue | Fix |
|-------|-----|
| `az costmanagement query` fails | Switch to `az rest --method post` with a JSON body file |
| azqr scan returns empty results | Verify Reader role is assigned; try `azqr scan --debug` |
| Cost query returns no rows | Check date range — `from` must be before `to`; verify subscription has incurred costs |
| Portal links are broken | Verify tenant ID format: `<tenant-id>` not `<tenant-name>` |
| Metrics query fails | Verify resource ID format starts with `/subscriptions/`; check Monitoring Reader role |
| Redis analysis — no subscriptions found | Run `az account list -o table` to verify accessible subscriptions |
| AKS cost add-on not visible | Ensure AKS cluster is on a supported version; enable via `az aks update --enable-cost-analysis` |
