---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-cost"
  source_host: "skills.sh"
  source_title: "Azure Cost Management Skill"
  imported_at: "2026-05-01T02:44:36Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-cost"
    confidence: "high"
secrets: {}
---

# Azure Cost Management Skill — Agent Runbook

## Objective

This runbook enables an AI agent to perform Azure cost management tasks on behalf of a user. It covers three core workflows: (1) querying historical Azure costs by service, resource, location, or tag; (2) forecasting future Azure spending and projecting end-of-month costs; and (3) optimizing Azure spend by identifying orphaned resources, rightsizing VMs and containers, and generating cost optimization reports. The agent must always retrieve actual cost data from the Azure Cost Management API — never estimate or assume — and must always present the full bill alongside any optimization recommendations. Destructive operations require explicit user approval before execution.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/cost_report.md` | Human-readable cost analysis report with breakdown by service/resource and any optimization recommendations |
| `/app/results/raw_cost_data.json` | Raw JSON response(s) from the Azure Cost Management Query API |
| `/app/results/forecast_data.json` | Raw JSON response(s) from the Azure Cost Management Forecast API (if forecast was requested) |
| `/app/results/optimization_report.md` | List of identified optimization opportunities with estimated savings and Azure Portal links (if optimization was requested) |
| `/app/results/summary.md` | Executive summary: scope queried, total cost retrieved, key findings, any errors |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `scope` | *(required)* | Azure scope path — see Scope Reference below |
| `report_type` | `ActualCost` | `ActualCost` or `AmortizedCost` |
| `timeframe` | `MonthToDate` | `MonthToDate`, `BillingMonthToDate`, `TheLastMonth`, or `Custom` |
| `start_date` | *(required if Custom)* | ISO date `YYYY-MM-DD`, only used when `timeframe=Custom` |
| `end_date` | *(required if Custom)* | ISO date `YYYY-MM-DD`, only used when `timeframe=Custom` |
| `api_version` | `2023-11-01` | Azure Cost Management API version |
| `run_optimization` | `false` | Set `true` to also execute the cost optimization workflow |
| `run_forecast` | `false` | Set `true` to also execute the cost forecast workflow |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` CLI | CLI | Yes | Azure CLI — used for `az rest` cost queries and resource listing |
| `azure__documentation` MCP tool | MCP | Recommended | Search Azure docs for API parameters |
| `azure__extension_cli_generate` MCP tool | MCP | Recommended | Generate `az rest` commands from plain intent |
| `azure__get_azure_bestpractices` MCP tool | MCP | Recommended | Retrieve Azure cost management best practices |
| `azure__extension_azqr` MCP tool | MCP | Optional | Run Azure Quick Review for orphaned resource discovery |
| `azure__aks` MCP tool | MCP | Optional | AKS cost analysis — list clusters, node pools, config |
| Azure RBAC: Cost Management Reader | Credential | Yes | Required on the target scope |
| Azure RBAC: Monitoring Reader | Credential | Yes | Required for utilization metrics via `az monitor` |
| Azure RBAC: Reader | Credential | Yes | Required for resource listing on scope |
| `jq` | CLI | Yes | JSON processing for API responses |
| `python3` | Runtime | Yes | Parsing and report generation |

---

## Step 1: Environment Setup

```bash
# Verify required CLIs are present
command -v az   >/dev/null || { echo "ERROR: az CLI not installed"; exit 1; }
command -v jq   >/dev/null || { echo "ERROR: jq not installed"; exit 1; }

# Confirm Azure login
az account show --query "{subscriptionId:id, name:name, tenantId:tenantId}" -o json || {
  echo "ERROR: Not logged in to Azure. Run: az login"
  exit 1
}

# Confirm the scope is accessible
SCOPE="${SCOPE:-/subscriptions/$(az account show --query id -o tsv)}"
az rest --method GET \
  --url "${SCOPE}/providers/Microsoft.CostManagement/query?api-version=2023-11-01" \
  --headers "ClientType=GitHubCopilotForAzure" 2>&1 | head -5 || true

# Create output directory
mkdir -p /app/results
echo "Environment ready. Scope: $SCOPE"
```

---

## Step 2: Cost Query Workflow

Query historical costs from the Azure Cost Management API. Use `az rest` (more reliable than `az costmanagement query`). Always include `ClientType: GitHubCopilotForAzure` header.

### 2.1 Select Scope

Determine the scope from user input using the reference table:

| Scope | URL Pattern |
|-------|-------------|
| Subscription | `/subscriptions/<subscription-id>` |
| Resource Group | `/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>` |
| Management Group | `/providers/Microsoft.Management/managementGroups/<management-group-id>` |
| Billing Account | `/providers/Microsoft.Billing/billingAccounts/<billing-account-id>` |
| Billing Profile | `/providers/Microsoft.Billing/billingAccounts/<billing-account-id>/billingProfiles/<billing-profile-id>` |

> **Tip:** These are scope paths only — not complete URLs. Combine with the API endpoint and version.

### 2.2 Query API Call

```bash
SCOPE="/subscriptions/<subscription-id>"
REPORT_TYPE="ActualCost"  # or AmortizedCost
API_VERSION="2023-11-01"

az rest --method POST \
  --url "${SCOPE}/providers/Microsoft.CostManagement/query?api-version=${API_VERSION}" \
  --headers "ClientType=GitHubCopilotForAzure" \
  --body '{
    "type": "'"$REPORT_TYPE"'",
    "timeframe": "MonthToDate",
    "dataset": {
      "granularity": "Daily",
      "aggregation": {
        "totalCost": {
          "name": "PreTaxCost",
          "function": "Sum"
        }
      },
      "grouping": [
        {"type": "Dimension", "name": "ServiceName"},
        {"type": "Dimension", "name": "ResourceGroupName"}
      ]
    }
  }' > /app/results/raw_cost_data.json

echo "Cost query complete. Records: $(jq '.properties.rows | length' /app/results/raw_cost_data.json)"
```

### 2.3 Handle Pagination

```bash
# Check for nextLink and paginate if present
NEXT_LINK=$(jq -r '.properties.nextLink // empty' /app/results/raw_cost_data.json)
PAGE=1
while [ -n "$NEXT_LINK" ]; do
  PAGE=$((PAGE + 1))
  az rest --method POST --url "$NEXT_LINK" \
    --headers "ClientType=GitHubCopilotForAzure" \
    > /app/results/raw_cost_data_page${PAGE}.json
  NEXT_LINK=$(jq -r '.properties.nextLink // empty' /app/results/raw_cost_data_page${PAGE}.json)
done
echo "Pagination complete. Pages fetched: $PAGE"
```

### 2.4 Handle Rate Limiting (429)

On a 429 response, check all `x-ms-ratelimit-microsoft.costmanagement-*-retry-after` headers (`qpu-retry-after`, `entity-retry-after`, `tenant-retry-after`), wait for the longest value, and do not retry until that duration has elapsed. The per-scope limit is 4 requests/minute.

---

## Step 3: Cost Optimization Workflow (if `run_optimization=true`)

### 3.1 Prerequisites

- Confirm Cost Management Reader + Monitoring Reader + Reader roles on scope
- Run cost query (Step 2) first — always present the total bill alongside optimization recommendations
- Use `azure__extension_azqr` MCP tool to find orphaned resources
- Use `az monitor metrics list` for utilization data (14-day lookback)

### 3.2 Find Orphaned Resources

```bash
# Use Azure Quick Review via MCP tool (preferred)
# azure__extension_azqr --subscription <subscription-id> [--resource-group <rg>]

# Fallback: list unattached managed disks
az resource list --query "[?type=='Microsoft.Compute/disks' && properties.diskState=='Unattached']" \
  --output json > /tmp/unattached_disks.json
echo "Unattached disks: $(jq length /tmp/unattached_disks.json)"
```

### 3.3 VM Rightsizing

```bash
# Get utilization metrics for VMs (14-day lookback)
az monitor metrics list \
  --resource <vm-resource-id> \
  --metric "Percentage CPU" \
  --start-time "$(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --interval PT1H \
  --output json
```

### 3.4 Optimization Report

Write `/app/results/optimization_report.md` with:
- Total current monthly cost
- List of optimization opportunities, each with: resource name, current cost, estimated savings, Azure Portal link, recommended action
- Data classification labels: `ACTUAL DATA`, `ACTUAL METRICS`, `VALIDATED PRICING`, `ESTIMATED SAVINGS`
- Rollback procedures for any recommended changes

> **Safety:** Never execute destructive operations (delete, resize, modify) without explicit user approval. Always provide dry-run commands first.

---

## Step 4: Cost Forecast Workflow (if `run_forecast=true`)

### 4.1 Forecast API Call

```bash
# Forecast API uses a different endpoint and body shape
FORECAST_START="$(date -u +%Y-%m-01)"  # first day of current month
FORECAST_END="$(date -u -d 'next month - 1 day' +%Y-%m-%d)"  # last day of current month

az rest --method POST \
  --url "${SCOPE}/providers/Microsoft.CostManagement/forecast?api-version=${API_VERSION}" \
  --headers "ClientType=GitHubCopilotForAzure" \
  --body '{
    "type": "ActualCost",
    "timeframe": "Custom",
    "timePeriod": {
      "from": "'"$FORECAST_START"'",
      "to": "'"$FORECAST_END"'"
    },
    "dataset": {
      "granularity": "Daily",
      "aggregation": {
        "totalCost": {
          "name": "PreTaxCost",
          "function": "Sum"
        }
      }
    },
    "includeActualCost": true,
    "includeFreshPartialCost": false
  }' > /app/results/forecast_data.json

echo "Forecast complete. Records: $(jq '.properties.rows | length' /app/results/forecast_data.json)"
```

### 4.2 Interpret Forecast

- Separate rows where `ChargeType == "Forecast"` from `ChargeType == "Actual"`
- Compute projected end-of-month total
- Flag any anomalies: day-over-day spike > 20% of rolling average

---

## Step 5: Generate Cost Report

Write `/app/results/cost_report.md` including:

```markdown
# Azure Cost Report — <scope> — <date>

## Summary
- **Scope**: <scope>
- **Report Type**: <ActualCost|AmortizedCost>
- **Timeframe**: <timeframe>
- **Total Cost**: $<total> USD

## Cost Breakdown by Service

| Service | Cost (USD) | % of Total |
|---------|-----------|------------|
| ...     | ...       | ...        |

## Cost Breakdown by Resource Group
...

## Top Cost Drivers
...

## Optimization Opportunities (if requested)
...

## Forecast (if requested)
...

## Data Classification
- ACTUAL DATA: from Azure Cost Management API
- ACTUAL METRICS: from Azure Monitor
- VALIDATED PRICING: from Azure pricing pages
- ESTIMATED SAVINGS: calculated from actual data + validated pricing

## Azure Portal Links
- [Cost Analysis](<portal-link>)
```

---

## Step 6: Iterate on Errors (max 3 rounds)

If any API call fails:

| Error | Fix |
|-------|-----|
| 401 Unauthorized | Re-authenticate: `az login` then retry |
| 403 Forbidden | Check RBAC: Cost Management Reader role required on scope |
| 404 Not Found | Verify scope path format matches Scope Reference table |
| 429 Too Many Requests | Read all `x-ms-ratelimit-*-retry-after` headers, wait longest, retry once |
| 400 Bad Request | Use `az rest` with JSON body — not `az costmanagement query` |
| Pagination failure | Retry the specific page; check nextLink URL is still valid |

Retry up to 3 times per API call. After 3 failures, record the error in `summary.md` and continue with partial data where possible.

---

## Step 7: Write Summary and Validation

### summary.md

Write `/app/results/summary.md`:

```markdown
# Azure Cost Management — Run Summary

## Run Details
- Scope: <scope>
- Timeframe: <timeframe>
- Report type: <ActualCost|AmortizedCost>
- Run date: <ISO date>
- Workflows executed: query[, optimization][, forecast]

## Results
- Total cost retrieved: $<total> USD
- Optimization opportunities found: <N>
- Forecast projected end-of-month: $<total> USD

## Issues
- <Any errors encountered>
- <Any partial data warnings>

## Output Files
- /app/results/cost_report.md
- /app/results/raw_cost_data.json
- /app/results/forecast_data.json (if forecast)
- /app/results/optimization_report.md (if optimization)
- /app/results/summary.md
- /app/results/validation_report.json
```

### validation_report.json

Write `/app/results/validation_report.json` with stages: setup, cost_query, pagination, rate_limit_handling, optimization (if run), forecast (if run), report_generation, output_verification.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/cost_report.md" \
  "$RESULTS_DIR/raw_cost_data.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] Cost data retrieved from actual Azure Cost Management API (not estimated)
- [ ] Total bill presented alongside any optimization recommendations
- [ ] All cost figures labeled with data classification (ACTUAL DATA / ESTIMATED SAVINGS / etc.)
- [ ] No destructive operations executed without explicit user approval
- [ ] Azure Portal links included for all referenced resources
- [ ] Rate limiting handled (429 responses respected)
- [ ] `cost_report.md` exists and is non-empty
- [ ] `raw_cost_data.json` exists and contains valid JSON
- [ ] `summary.md` exists with scope, total cost, and any issues
- [ ] `validation_report.json` exists with `overall_passed` field
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Always use `az rest` for cost queries**, not `az costmanagement query` — the latter is less reliable and has more limited options.
- **Always include `ClientType: GitHubCopilotForAzure` header** on every Cost Management API request.
- **Prefer MCP tools** (`azure__documentation`, `azure__extension_cli_generate`, `azure__get_azure_bestpractices`) over manual CLI commands — they provide validated, up-to-date parameter guidance.
- **30/14 day rule**: Use 30-day lookback for cost analysis; use 14-day lookback for utilization/metrics.
- **Scope paths are not full URLs** — combine with the API endpoint base URL and `?api-version=` query parameter.
- **For costs < $10/month**, emphasize operational improvements over pure financial savings in your recommendations.
- **Audit trail**: Save all API request bodies and responses so the user can review and reproduce the analysis.
- **Free tier awareness**: Many Azure services have free allowances — always account for these before reporting savings opportunities.
- **Never echo credentials** — use `az login` device flow or managed identity; do not write tokens to output files.
