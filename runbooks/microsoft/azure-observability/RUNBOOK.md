---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/github-copilot-for-azure/azure-observability"
  source_host: "skills.sh"
  source_title: "Azure Observability Services"
  imported_at: "2026-05-01T02:41:52Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-observability"
    confidence: "high"
secrets: {}
---

# Azure Observability Services — Agent Runbook

## Objective

Query metrics, logs, and traces across Azure Monitor, Application Insights, and Log Analytics. This runbook enables an agent to access Azure Monitor metrics, Application Insights APM data, and Log Analytics KQL queries through MCP tools or Azure CLI commands. It supports distributed tracing, performance analysis, and infrastructure monitoring across applications and resources. Interactive workbooks are available for building custom dashboards and reports on observability data. Common use cases include error tracking, request performance analysis, resource utilization monitoring, and security log queries.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata, query results, and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/query_results.json` | Results of observability queries executed (metrics, logs, traces) |
| `/app/results/monitoring_report.md` | Human-readable monitoring report with insights from the observability data |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `WORKSPACE_ID` | *(required)* | Log Analytics workspace ID for KQL queries |
| `RESOURCE_ID` | *(required)* | Azure resource ID for metric queries |
| `TIME_RANGE` | `1h` | Time range for queries (e.g. `1h`, `24h`, `7d`) |
| `METRIC_NAME` | `Percentage CPU` | Metric name to query from Azure Monitor |
| `SUBSCRIPTION_ID` | *(from az login context)* | Azure subscription ID |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Query Azure Monitor, Application Insights, and Log Analytics |
| `azure__monitor` MCP tool | MCP | Preferred | Query metrics and logs via Azure MCP server |
| `azure__applicationinsights` MCP tool | MCP | Optional | List and query Application Insights resources |
| `azure__kusto` MCP tool | MCP | Optional | Execute KQL queries against Log Analytics clusters |
| `azure__workbooks` MCP tool | MCP | Optional | Access interactive workbooks for dashboards |
| `jq` | CLI | Yes | Parse JSON output from Azure CLI commands |
| Azure credentials | Credential | Yes | Active `az login` session or service principal |

## Step 1: Environment Setup

Verify Azure CLI is installed and the user is authenticated.

```bash
echo "=== Environment Setup ==="

# Verify required tools
command -v az  >/dev/null || { echo "ERROR: Azure CLI not installed"; exit 1; }
command -v jq  >/dev/null || { echo "ERROR: jq not installed"; exit 1; }

# Verify Azure authentication
az account show --output table || { echo "ERROR: Not logged in to Azure. Run 'az login'"; exit 1; }

# Create output directory
mkdir -p /app/results

echo "Environment ready."
echo "Subscription: $(az account show --query 'name' -o tsv)"
echo "Tenant: $(az account show --query 'tenantId' -o tsv)"
```

**If Azure MCP is available:** Check MCP connectivity with `azure__monitor` tool first. If MCP is not enabled, run `/azure:setup` or enable via `/mcp`.

## Step 2: Discover Resources

List available Azure Monitor resources, Log Analytics workspaces, and Application Insights components.

```bash
echo "=== Discovering Azure Observability Resources ==="

# List Log Analytics workspaces
echo "--- Log Analytics Workspaces ---"
az monitor log-analytics workspace list --output table

# List Application Insights components
echo "--- Application Insights Components ---"
az monitor app-insights component list --output table

# List active alerts
echo "--- Active Alerts ---"
az monitor alert list --output table
```

**If using MCP:**
- `azure__applicationinsights` with command `applicationinsights_component_list` — List App Insights resources
- `azure__kusto` with command `kusto_cluster_list` — List Log Analytics clusters

Save the workspace ID and resource IDs you need for subsequent queries.

## Step 3: Query Metrics

Query Azure Monitor metrics for the target resource.

```bash
echo "=== Querying Azure Monitor Metrics ==="

# Query CPU metrics (adjust --metric as needed)
az monitor metrics list \
  --resource "${RESOURCE_ID}" \
  --metric "${METRIC_NAME:-Percentage CPU}" \
  --output json | jq '{
    metric: .value[0].name.localizedValue,
    timeseries: (.value[0].timeseries[0].data[-5:] // [])
  }' > /app/results/query_results.json

echo "Metrics written to /app/results/query_results.json"
cat /app/results/query_results.json
```

**If using MCP:** Use `azure__monitor` with command `monitor_metrics_query` to query metrics interactively.

## Step 4: Query Logs with KQL

Run KQL queries against Log Analytics to retrieve application logs, errors, and performance data.

```bash
echo "=== Querying Log Analytics ==="

# Recent application errors (last 1 hour)
echo "--- Recent Application Errors ---"
az monitor log-analytics query \
  --workspace "${WORKSPACE_ID}" \
  --analytics-query "AppExceptions | where TimeGenerated > ago(${TIME_RANGE:-1h}) | project TimeGenerated, Message, StackTrace | order by TimeGenerated desc | take 20" \
  --output json | jq '.' >> /app/results/query_results.json

# Request performance
echo "--- Request Performance ---"
az monitor log-analytics query \
  --workspace "${WORKSPACE_ID}" \
  --analytics-query "AppRequests | where TimeGenerated > ago(${TIME_RANGE:-1h}) | summarize avg(DurationMs), count() by Name | order by avg_DurationMs desc | take 10" \
  --output json | jq '.' >> /app/results/query_results.json

# Resource utilization
echo "--- Resource Utilization ---"
az monitor log-analytics query \
  --workspace "${WORKSPACE_ID}" \
  --analytics-query "AzureMetrics | where TimeGenerated > ago(${TIME_RANGE:-1h}) | where MetricName == 'Percentage CPU' | summarize avg(Average) by Resource | take 10" \
  --output json | jq '.' >> /app/results/query_results.json
```

**If using MCP:** Use `azure__monitor` with command `monitor_logs_query` for KQL queries, or `azure__kusto` with command `kusto_query`.

## Step 5: Query Application Insights

Retrieve APM data, distributed traces, and dependency information from Application Insights.

```bash
echo "=== Querying Application Insights ==="

# List App Insights resources
az monitor app-insights component list --output json | jq '[.[] | {name: .name, instrumentationKey: .instrumentationKey, location: .location}]' >> /app/results/query_results.json

echo "Application Insights data appended to query_results.json"
```

**If using MCP:** Use `azure__applicationinsights` with command `applicationinsights_component_list`.

## Step 6: Iterate on Errors (max 3 rounds)

If any queries fail, apply targeted fixes:

| Issue | Fix |
|-------|-----|
| `WORKSPACE_ID` not set | Run Step 2 to discover workspace IDs; set `WORKSPACE_ID` from the list |
| `RESOURCE_ID` not set | Use `az resource list --output table` to find the resource ID |
| KQL query fails | Verify workspace has data; try a simpler query like `AzureActivity \| take 5` |
| `az login` required | Run `az login` or configure a service principal via `az login --service-principal` |
| MCP tool unavailable | Fall back to Azure CLI commands; run `/azure:setup` to enable MCP |
| Permission denied | Ensure the account has `Monitoring Reader` or `Log Analytics Reader` role |

After each fix, re-run the failed step and verify output. Repeat up to 3 times total.

## Step 7: Generate Monitoring Report

Synthesize the collected observability data into a human-readable report.

```bash
echo "=== Generating Monitoring Report ==="

cat > /app/results/monitoring_report.md << 'REPORT_EOF'
# Azure Observability Monitoring Report

## Query Summary

- **Time Range**: ${TIME_RANGE:-1h}
- **Generated At**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Resource**: ${RESOURCE_ID:-Not specified}
- **Workspace**: ${WORKSPACE_ID:-Not specified}

## Metrics

See `query_results.json` for raw metric data.

## Application Errors

See `query_results.json` for recent AppExceptions.

## Performance

See `query_results.json` for request performance summary.

## Recommendations

- Monitor `AppExceptions` count daily; alert when error rate exceeds baseline by 20%
- Set up Azure Monitor alerts on CPU > 80% for more than 5 minutes
- Use Application Insights availability tests for external endpoint monitoring
- Review KQL dashboards weekly for resource utilization trends

REPORT_EOF

echo "monitoring_report.md written"
```

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/query_results.json" \
  "$RESULTS_DIR/monitoring_report.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] Azure CLI authenticated and account verified
- [ ] Log Analytics workspaces and App Insights components discovered
- [ ] Metrics queried and written to `query_results.json`
- [ ] KQL log queries executed (errors, performance, utilization)
- [ ] Application Insights APM data retrieved
- [ ] `monitoring_report.md` written with summary and recommendations
- [ ] `summary.md` exists with run metadata
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **MCP preferred over CLI.** When Azure MCP is enabled, MCP tool calls are faster and return structured JSON. Fall back to Azure CLI only when MCP is unavailable.
- **KQL time ranges.** Use `ago(1h)`, `ago(24h)`, or `ago(7d)` in KQL queries. Adjust `TIME_RANGE` parameter accordingly.
- **Workspace ID format.** `WORKSPACE_ID` should be the workspace GUID (e.g. `a1b2c3d4-...`), not the workspace name. Use `az monitor log-analytics workspace list --query '[].customerId' -o tsv` to find it.
- **Resource ID format.** `RESOURCE_ID` is the full ARM path: `/subscriptions/<sub>/resourceGroups/<rg>/providers/<type>/<name>`. Use `az resource show` to get it.
- **Distributed tracing.** For end-to-end traces, use Application Insights with `azure__applicationinsights` MCP tool or query the `AppDependencies` and `AppRequests` KQL tables together.
- **Cost awareness.** Log Analytics queries incur costs based on data scanned. Use time-bounded queries (`ago(1h)`) and `take` limits during exploration.

## Common Fixes

| Issue | Fix |
|-------|-----|
| No data returned from KQL | Verify `TimeGenerated` range; check workspace has ingested data |
| `ResourceNotFound` error | Confirm `RESOURCE_ID` is correct and resource exists in the subscription |
| `Unauthorized` on metrics query | Assign `Monitoring Reader` role: `az role assignment create --role "Monitoring Reader" --assignee <upn> --scope <resource-id>` |
| App Insights component not found | Ensure the resource group and subscription are correct; try `az monitor app-insights component list --subscription <id>` |
| MCP tool times out | Retry with a narrower time range or smaller `take` limit |
