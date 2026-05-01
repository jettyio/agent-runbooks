---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-cost-optimization"
  source_host: "skills.sh"
  source_title: "Azure Cost Optimization Skill"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-cost-optimization"
    confidence: "high"
secrets: {}
---

# Azure Cost Optimization Skill — Agent Runbook

## Objective

Analyze Azure subscriptions to identify cost savings through orphaned resource cleanup, rightsizing,
and optimization recommendations based on actual usage data. This runbook guides an agent through
discovering resources, querying actual cost data from the Azure Cost Management API, validating
current pricing, collecting utilization metrics, and producing a prioritized cost optimization
report with concrete savings estimates and implementation commands. The agent must always query
actual data — never estimate or assume costs — and must obtain explicit approval before executing
any destructive operations.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/cost-optimization-report.md` | Comprehensive cost optimization report with executive summary, breakdown, and prioritized recommendations |
| `/app/results/cost-query-result.json` | Audit trail of all cost queries and raw responses from Azure Cost Management API |
| `/app/results/azqr-findings.json` | Raw output from Azure Quick Review (azqr) scan identifying orphaned resources |
| `/app/results/utilization-metrics.json` | Azure Monitor utilization metrics for rightsizing analysis |
| `/app/results/summary.md` | Executive summary with run metadata and key findings |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `/app/results` | Output directory for all result files | `/app/results` |
| `SUBSCRIPTION_ID` | Azure subscription ID to analyze | *(required — prompt user)* |
| `RESOURCE_GROUP` | Resource group to scope the analysis | *(optional — leave blank for subscription-wide)* |
| `START_DATE` | Start date for cost query (ISO 8601) | 30 days ago |
| `END_DATE` | End date for cost query (ISO 8601) | today |
| `ANALYSIS_SCOPE` | One of: `subscription`, `resource-group`, `redis-only`, `aks-only` | `subscription` |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Azure resource listing, cost queries, and metric collection |
| `azqr` (Azure Quick Review) | CLI | Yes | Orphaned resource detection |
| `costmanagement` extension | Azure CLI extension | Yes | Cost Management queries via REST |
| `resource-graph` extension | Azure CLI extension | Yes | Cross-subscription resource discovery |
| Azure Cost Management Reader role | Permission | Yes | Read cost data from Azure Cost Management API |
| Azure Monitoring Reader role | Permission | Yes | Read utilization metrics from Azure Monitor |
| Azure Reader role | Permission | Yes | List resources in subscription/resource group |

## Step 1: Environment Setup

Verify all required tools, permissions, and inputs are available before proceeding.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify az CLI
az --version || { echo "ERROR: Azure CLI not installed"; exit 1; }

# Verify azqr
azqr version || { echo "ERROR: Azure Quick Review (azqr) not installed"; exit 1; }

# Verify az extensions
az extension show --name costmanagement || az extension add --name costmanagement
az extension show --name resource-graph || az extension add --name resource-graph

# Verify authentication
az account show || { echo "ERROR: Not authenticated — run 'az login'"; exit 1; }

# Show subscription context
az account list --output table

# Create output directory
mkdir -p /app/results

echo "=== SETUP COMPLETE ==="
```

Prompt the user for:
- **SUBSCRIPTION_ID** (required): the Azure subscription to analyze
- **RESOURCE_GROUP** (optional): leave blank for subscription-wide analysis
- **ANALYSIS_SCOPE** (optional, default: `subscription`): narrow to `redis-only` or `aks-only` if the user specifies

## Step 2: Validate Prerequisites

```bash
SUBSCRIPTION_ID="<SUBSCRIPTION_ID>"
RESOURCE_GROUP="<RESOURCE_GROUP>"   # leave empty for subscription-wide

# Set subscription context
az account set --subscription "$SUBSCRIPTION_ID"

# Verify Cost Management Reader access
az role assignment list \
  --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --query "[?roleDefinitionName=='Cost Management Reader']" \
  --output table

# Verify Monitoring Reader access
az role assignment list \
  --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --query "[?roleDefinitionName=='Monitoring Reader']" \
  --output table
```

If the user is missing required roles, surface a clear error with the role names they need and the
scope at which they should be granted. Do not proceed until permissions are confirmed.

## Step 3: Conditional — Redis-Specific Analysis

**Skip this step unless** the user specifically asks about Redis, Azure Cache for Redis, or Azure
Managed Redis optimization.

When triggered:
1. Ask the user to select analysis scope: Specific Subscription ID / Subscription Name / Prefix /
   All My Subscriptions / Tenant-wide.
2. Use the `redis_list` MCP command to list Redis resources:

```python
# MCP call (preferred)
redis_list(subscription=SUBSCRIPTION_ID)
```

3. Apply Redis-specific optimization rules:
   - Failed or degraded cache instances (immediate deletion candidates)
   - Oversized SKU tiers relative to actual memory usage
   - Resources missing cost-allocation tags

Iterate max 3 rounds when initial results are incomplete or ambiguous.

## Step 4: Conditional — AKS-Specific Analysis

**Skip this step unless** the user mentions AKS, Kubernetes, cluster, node pool, pod, or kubectl.

When triggered:
1. Ask the user for scope: Specific Cluster / Resource Group / Subscription / All My Clusters.
2. Prefer MCP for AKS operations; fall back to `az aks` and `kubectl` only when MCP cannot perform
   the specific operation:

```bash
# Fallback CLI example
az aks list --subscription "$SUBSCRIPTION_ID" --output table
```

3. Enable the AKS cost analysis add-on for namespace-level cost visibility if not already enabled.
4. Investigate anomalies: cost spikes, scaling events, budget alerts.

## Step 5: Load Best Practices

Load Azure cost optimization best practices to inform recommendations:

```python
# MCP call
mcp_azure_mcp_get_azure_bestpractices(
    intent="Get cost optimization best practices",
    command="get_bestpractices",
    parameters={"resource": "cost-optimization", "action": "all"}
)
```

Incorporate the returned best practices into the recommendations generated in Step 9.

## Step 6: Run Azure Quick Review

Run azqr to identify orphaned resources eligible for immediate deletion:

```python
# MCP call (preferred)
extension_azqr(
    subscription="<SUBSCRIPTION_ID>",
    **{"resource-group": "<RESOURCE_GROUP>"}  # omit if subscription-wide
)
```

**What to look for in azqr results:**
- Orphaned resources: unattached disks, unused NICs, idle NAT gateways
- Over-provisioned resources: excessive retention periods, oversized SKUs
- Resources missing cost-allocation tags

Save results to `/app/results/azqr-findings.json`.

```bash
azqr scan --subscription-id "$SUBSCRIPTION_ID" --output-name /app/results/azqr-findings \
  ${RESOURCE_GROUP:+--resource-group "$RESOURCE_GROUP"}
```

## Step 7: Discover Resources

Use Azure Resource Graph for efficient cross-subscription resource discovery:

```bash
# List all resources in the subscription
az resource list \
  --subscription "$SUBSCRIPTION_ID" \
  ${RESOURCE_GROUP:+--resource-group "$RESOURCE_GROUP"} \
  --output json > /app/results/resource-list.json

# Resource Graph query for orphaned managed disks
az graph query -q "
Resources
| where type =~ 'microsoft.compute/disks'
| where properties.diskState == 'Unattached'
| project name, resourceGroup, location, properties.diskSizeGB, properties.diskState
" --subscriptions "$SUBSCRIPTION_ID" --output json
```

## Step 8: Query Actual Costs

Get actual cost data from Azure Cost Management API (last 30 days):

```bash
START_DATE=$(date -u -d '30 days ago' '+%Y-%m-%dT00:00:00Z' 2>/dev/null || \
             date -u -v-30d '+%Y-%m-%dT00:00:00Z')
END_DATE=$(date -u '+%Y-%m-%dT23:59:59Z')

# Create temp directory for query file
mkdir -p /tmp/cost-query

cat > /tmp/cost-query/cost-query.json <<COSTEOF
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
COSTEOF

# Execute cost query via REST API (more reliable than az costmanagement query)
SCOPE="/subscriptions/${SUBSCRIPTION_ID}"
if [ -n "$RESOURCE_GROUP" ]; then
  SCOPE="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}"
fi

az rest \
  --method post \
  --url "https://management.azure.com${SCOPE}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --body @/tmp/cost-query/cost-query.json \
  --output json > /app/results/cost-query-result.json

echo "Cost query result saved."
cat /app/results/cost-query-result.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
rows = data.get('properties', {}).get('rows', [])
print(f'Total resources with cost data: {len(rows)}')
if rows:
    costs = sorted(rows, key=lambda r: r[0] if r else 0, reverse=True)
    print('Top 5 cost drivers:')
    for row in costs[:5]:
        print(f'  Cost: \${row[0]:.2f} — ResourceId: {row[1] if len(row) > 1 else \"N/A\"}')
"

# Clean up temp files
rm -rf /tmp/cost-query
```

## Step 9: Validate Pricing

Fetch current pricing from official Azure pricing pages for the top resources identified in Step 8:

```python
# MCP call example for Container Apps pricing
fetch_webpage(
    urls=["https://azure.microsoft.com/en-us/pricing/details/container-apps/"],
    query="pricing tiers and costs"
)
```

Key services to validate:
- Container Apps: check free tier allowances (180K vCPU-sec/month)
- Virtual Machines: current hourly rates for recommended SKU alternatives
- App Service: plan tier pricing for rightsizing
- Log Analytics: ingestion pricing and retention costs

**Important**: Always check for free tier allowances — many Azure services have generous free limits
that may explain $0 costs for lightly-used resources.

## Step 10: Collect Utilization Metrics

Query Azure Monitor for utilization data (last 14 days) to support rightsizing recommendations:

```bash
START_TIME=$(date -u -d '14 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || \
             date -u -v-14d '+%Y-%m-%dT%H:%M:%SZ')
END_TIME=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# VM CPU utilization — replace RESOURCE_ID with actual resource ID
az monitor metrics list \
  --resource "<RESOURCE_ID>" \
  --metric "Percentage CPU" \
  --interval PT1H \
  --aggregation Average \
  --start-time "$START_TIME" \
  --end-time "$END_TIME" \
  --output json > /app/results/utilization-metrics.json

echo "Utilization metrics saved."
```

For each top-cost resource identified in Step 8, collect relevant utilization metrics and append to
`/app/results/utilization-metrics.json`.

## Step 11: Iterate on Errors (max 3 rounds)

If any step above returns an error or incomplete data:

1. Identify the specific failure (missing permission, wrong scope, API error).
2. Apply the targeted fix:
   - **Permission denied**: surface the required role and scope to the user.
   - **API 400/404**: verify the subscription ID, scope URL, and API version.
   - **azqr not found**: guide the user to install azqr from `https://github.com/Azure/azqr`.
   - **Empty cost results**: check that the subscription has actual spend; try broadening the date range.
3. Retry the failed step.
4. Repeat up to 3 times total. After 3 failed attempts, document the failure in `summary.md` and
   continue with available data rather than blocking report generation.

## Step 12: Generate Optimization Report

Create a comprehensive cost optimization report at `/app/results/cost-optimization-report.md`:

```markdown
# Azure Cost Optimization Report
**Generated**: <ISO timestamp>
**Subscription**: <SUBSCRIPTION_ID>
**Resource Group**: <RESOURCE_GROUP or "subscription-wide">
**Analysis Period**: Last 30 days (<START_DATE> to <END_DATE>)

## Executive Summary
- **Total Monthly Cost**: $X (ACTUAL DATA from Cost Management API)
- **Top Cost Drivers**: [List top 3 resources with Azure Portal links]
- **Estimated Monthly Savings**: $Y (from all recommendations)
- **Orphaned Resources Found**: N resources eligible for immediate deletion

## Cost Breakdown

| Resource | Resource Group | Cost (30d) | Azure Portal |
|----------|---------------|------------|-------------|
| ...      | ...           | $X.XX      | [Link](...)  |

## Free Tier Analysis
[Resources operating within free tiers showing $0 cost — explain why]

## Orphaned Resources (Immediate Savings)
[From azqr output — resources that can be deleted immediately]

| Resource | Type | Estimated Monthly Savings | Action |
|----------|------|--------------------------|--------|
| ...      | ...  | $X.XX                    | Delete |

## Optimization Recommendations

### Priority 1: High Impact, Low Risk
[Immediate actions: delete orphaned resources, stop idle services]
- Resource name — ACTUAL cost: $X/month — ESTIMATED savings: $Y/month
- Commands (with approval warning)

### Priority 2: Medium Impact, Medium Risk
[Rightsizing: VMs, App Service Plans, Redis SKU downgrades]
- Resource: ACTUAL baseline, ACTUAL metrics, VALIDATED pricing, ESTIMATED savings
- Commands (with approval warning and rollback procedure)

### Priority 3: Long-term Optimization
[Reserved Instances, Storage tiering, commitment plans]

## Total Estimated Savings
- Monthly: $X
- Annual: $Y

## Implementation Commands
[Commands with explicit "REQUIRES APPROVAL" warnings]

## Validation Appendix
- **Cost Query Results**: `/app/results/cost-query-result.json`
- **azqr Findings**: `/app/results/azqr-findings.json`
- **Utilization Metrics**: `/app/results/utilization-metrics.json`
- **Pricing Sources**: [links to Azure pricing pages used]
```

**Portal Link Format**:
```
https://portal.azure.com/#@<TENANT_ID>/resource/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/<RESOURCE_PROVIDER>/<RESOURCE_TYPE>/<RESOURCE_NAME>/overview
```

## Step 13: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/cost-optimization-report.md" \
  "$RESULTS_DIR/cost-query-result.json" \
  "$RESULTS_DIR/azqr-findings.json" \
  "$RESULTS_DIR/utilization-metrics.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Safety Checklist

- [ ] All cost data sourced from Azure Cost Management API (not estimated)
- [ ] All pricing validated from official Azure pricing pages
- [ ] All utilization metrics sourced from Azure Monitor (not assumed)
- [ ] No destructive commands issued without explicit user approval
- [ ] Rollback procedures included for all Priority 2+ recommendations
- [ ] Azure Portal links included for all referenced resources
- [ ] Audit trail files written to `/app/results/` for all data queries

## Tips

- **Always query actual costs first.** Never estimate or assume. Use `az rest` with the Cost Management REST API — it is more reliable than `az costmanagement query`.
- **Check free tier allowances.** Container Apps: 180K vCPU-sec/month free; many services show $0 because they operate within free limits, not because they are unused.
- **Use REST API for cost queries.** `az rest --method post` with a JSON body file is more reliable than `az costmanagement query` which has known edge-case bugs.
- **Prefer MCP over CLI.** For supported services (Redis, AKS), MCP tools provide richer metadata and are faster than CLI equivalents.
- **Save all audit data.** Keep cost query results, azqr output, and utilization metrics for at least 12 months to enable historical comparison.
- **Never execute destructive operations without approval.** Include `--dry-run` or equivalent flags and always print a warning before resource deletion commands.
- **For low-cost resources (< $10/month).** Emphasize operational improvements (tagging, compliance) over financial savings in your report.
- **Portal links must include tenant ID.** Broken portal links (wrong tenant or resource ID format) are a common pitfall — verify the format before including.
