---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/github-copilot-for-azure/azure-messaging"
  source_host: "skills.sh"
  source_title: "Azure Messaging SDK Troubleshooting"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-messaging"
    confidence: "high"
secrets: {}
---

# Azure Messaging SDK Troubleshooting — Agent Runbook

## Objective

Diagnose and resolve issues with the Azure Messaging SDK for Azure Event Hubs and Azure Service Bus. This runbook guides an agent through a structured workflow for identifying SDK connection failures, authentication errors, AMQP link errors, message lock issues, session lock problems, and event processor anomalies. The agent uses Azure MCP tools (`mcp_azure_mcp_eventhubs`, `mcp_azure_mcp_servicebus`, `mcp_azure_mcp_resourcehealth`, `mcp_azure_mcp_monitor`, `mcp_azure_mcp_documentation`) to gather diagnostic data, match known error patterns, and recommend remediation steps with documentation citations.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/diagnosis.md` | Structured diagnosis report: error classification, root cause, recommended fix, and documentation references |
| `/app/results/resource_health.json` | Raw output from `mcp_azure_mcp_resourcehealth` for the affected namespace |
| `/app/results/summary.md` | Executive summary with run metadata, diagnosis outcome, and any follow-up actions |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `error_description` | *(required)* | The error message or symptom reported by the user (paste verbatim) |
| `sdk_language` | *(optional)* | The SDK language: `python`, `java`, `dotnet`, `javascript`, or `go` |
| `sdk_version` | *(optional)* | The SDK version string (e.g. `azure-eventhub==5.11.5`) |
| `namespace_name` | *(optional)* | The Event Hubs or Service Bus namespace name |
| `entity_name` | *(optional)* | Queue, topic, hub, or consumer group name |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `mcp_azure_mcp_eventhubs` | MCP Tool | Conditional | List namespaces, hubs, and consumer groups for Event Hubs diagnostics |
| `mcp_azure_mcp_servicebus` | MCP Tool | Conditional | List namespaces, queues, topics, and subscriptions for Service Bus diagnostics |
| `mcp_azure_mcp_monitor` | MCP Tool | Recommended | Query Azure Monitor diagnostic logs with KQL to surface error events |
| `mcp_azure_mcp_resourcehealth` | MCP Tool | Yes | Verify Azure namespace health before deeper diagnosis |
| `mcp_azure_mcp_documentation` | MCP Tool | Yes | Search Microsoft Learn for language-specific troubleshooting guidance |

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Services** | Azure Event Hubs, Azure Service Bus |
| **MCP Tools** | `mcp_azure_mcp_eventhubs`, `mcp_azure_mcp_servicebus` |
| **Best For** | Diagnosing SDK connection, auth, and message processing issues |

---

## Step 1: Environment Setup

Verify MCP tools are available and output directory is ready.

```bash
echo "=== ENVIRONMENT SETUP ==="
mkdir -p /app/results

# Verify required MCP tools are accessible
for tool in mcp_azure_mcp_resourcehealth mcp_azure_mcp_documentation mcp_azure_mcp_eventhubs mcp_azure_mcp_servicebus mcp_azure_mcp_monitor; do
  echo "Checking: $tool"
done

echo "Output directory: /app/results"
echo "Setup complete"
```

Confirm that `error_description` is provided. If missing, ask the user to describe the error or symptom before continuing.

---

## Step 2: Identify the SDK and Version

Examine the user's prompt for SDK and version clues.

1. Look for import statements (e.g. `from azure.eventhub import`, `com.azure.messaging.eventhubs`)
2. Look for error stack traces indicating the package name and version
3. If the language or version is not explicitly stated, proceed with the diagnosis and note "SDK unspecified" — ask later if needed

Record the identified `sdk_language` and `sdk_version` in the diagnosis report.

---

## Step 3: Check Resource Health

Use `mcp_azure_mcp_resourcehealth` to verify the namespace is healthy before assuming an SDK bug.

```python
# If namespace_name is known:
result = mcp_azure_mcp_resourcehealth.get(resource_type="Microsoft.EventHub/namespaces", resource_name=namespace_name)
# Or for Service Bus:
result = mcp_azure_mcp_resourcehealth.get(resource_type="Microsoft.ServiceBus/namespaces", resource_name=namespace_name)

import json, pathlib
pathlib.Path("/app/results/resource_health.json").write_text(json.dumps(result, indent=2))
```

If the namespace is **degraded or unavailable**, report this as the root cause and skip SDK-level diagnosis. If **healthy**, continue.

---

## Step 4: Classify the Error

Match the `error_description` against the following categories. Stop at the first match.

| Error Category | Symptoms | Primary Guide |
|----------------|----------|---------------|
| **Connection / Auth** | `AuthorizationFailedException`, `UnauthorizedAccessException`, connection refused, AMQP open error | Search "Azure Event Hubs authentication" or "Service Bus SAS token" |
| **AMQP Link Error** | `LinkDetachException`, `detach-forced`, `link:detach-forced` | Search "Azure SDK AMQP link detach" |
| **Idle Timeout / Reconnect** | `ConnectionDroppedException`, idle timeout, slow reconnect after network blip | Search "Azure SDK idle timeout reconnect" |
| **Message Lock** | `MessageLockLostException`, `lock expired`, lock renewal failures, batch lock timeouts | Search "Service Bus message lock renewal" |
| **Session Lock** | `SessionLockLostException`, session receiver errors | Search "Service Bus session lock" |
| **Processor Stopped** | Event processor stops, `EventProcessorClient` stops, no more messages received | Search "Event Hubs event processor stopped" |
| **Duplicate / Checkpoint** | Duplicate events, checkpoint offset resets, consumer group conflicts | Search "Event Hubs checkpoint duplicate events" |
| **Configuration** | Questions about retry policy, prefetch count, batch size, receive batch behavior | Search "Azure SDK retry configuration" |

Record the matched category in `diagnosis.md`.

---

## Step 5: Look Up Documentation (max 3 rounds)

Use `mcp_azure_mcp_documentation` to search Microsoft Learn for the matched error category.

```python
docs = mcp_azure_mcp_documentation.search(query="<error category + sdk_language>")
# Example: "Azure Event Hubs AMQP link detach python SDK"
```

1. Run the search and note the top 3 results with URLs
2. If the first search yields no relevant results, reformulate the query with the error message verbatim and retry
3. After max 3 search rounds, proceed with the best documentation found

---

## Step 6: Diagnose with Logs (if namespace_name is known)

Query Azure Monitor for relevant error events from the last hour.

```python
kql_query = f"""
AzureDiagnostics
| where ResourceType == "EVENTHUBS" or ResourceType == "SERVICEBUSNAMESPACESOPERATIONLOGS"
| where TimeGenerated > ago(1h)
| where Category in ("OperationalLogs", "RuntimeAuditLogs")
| where Message contains "<key_error_term>"
| project TimeGenerated, OperationName, ResultDescription, Message
| order by TimeGenerated desc
| take 20
"""
result = mcp_azure_mcp_monitor.logs_query(query=kql_query, workspace_id="<workspace_id>")
```

If `namespace_name` or `workspace_id` is unknown, skip this step and note it in the diagnosis.

---

## Step 7: Verify Configuration

Check the following configuration parameters that commonly cause the reported error:

| Issue | Configuration Check |
|-------|-------------------|
| Message lock lost | `message_lock_duration` vs processing time; enable lock renewal |
| AMQP link detach | `transport_type` (AMQP vs AMQP over WebSocket); firewall port 5671 vs 443 |
| Idle timeout | `idle_timeout` setting; keepalive intervals |
| Processor stopped | `checkpoint_store` connectivity; consumer group exclusivity |
| Auth error | SAS token expiry; managed identity role assignment (`Azure Event Hubs Data Receiver`) |
| Duplicate events | Checkpoint not called after processing; partition ownership conflicts |

---

## Step 8: Recommend Fix

Compose the remediation recommendation. The recommendation must:

1. Cite the specific documentation URL(s) found in Step 5
2. Provide a concrete code change or configuration change
3. Indicate whether the fix requires a restart of the processor/receiver
4. Note any follow-up verification steps (e.g., monitor logs for 10 minutes post-fix)

Write the full diagnosis and recommendation to `/app/results/diagnosis.md`.

---

## Step 9: Iterate on Incomplete Diagnosis (max 3 rounds)

If the diagnosis is inconclusive after Steps 4–8:

1. Identify the missing information (SDK language? namespace name? full stack trace?)
2. Ask the user for the specific missing detail
3. Re-run Steps 4–8 with the new information
4. Repeat up to 3 times total

After 3 rounds, if the error cannot be classified, write a "Could not classify" diagnosis with the closest candidate categories and escalation steps.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Auth error with managed identity | Assign `Azure Event Hubs Data Receiver` or `Azure Service Bus Data Receiver` role |
| AMQP link detach on firewalled network | Switch to AMQP over WebSocket (port 443) |
| Message lock lost | Reduce batch size, increase `message_lock_duration`, or enable auto-lock-renewal |
| Processor stopped silently | Add error handler to `EventProcessorClient`; check checkpoint store connectivity |
| Duplicate events | Ensure checkpoint is persisted after successful processing, not before |

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/diagnosis.md" \
  "$RESULTS_DIR/resource_health.json" \
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

### Checklist

- [ ] Error classified into one of the 8 categories (or "unclassified" with reasoning)
- [ ] Resource health checked and result saved to `resource_health.json`
- [ ] Documentation searched and at least one relevant URL cited
- [ ] `diagnosis.md` written with root cause, fix, and documentation citations
- [ ] `summary.md` exists with run metadata and outcome
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Check resource health first.** Many apparent SDK bugs are actually Azure service incidents. Always run `mcp_azure_mcp_resourcehealth` before deep SDK diagnosis.
- **AMQP link detach on corporate networks** is almost always a firewall issue — switch to WebSocket transport (port 443) rather than debugging the SDK.
- **Message lock lost** usually means the processing time exceeds `message_lock_duration`. Enable auto-lock-renewal or reduce batch size.
- **Processor stopped silently** always requires an error handler — the default behavior is to swallow errors. Register an error handler and inspect exceptions.
- **Duplicate events after restart** means the checkpoint was not persisted. Ensure `update_checkpoint()` is called after every successfully processed event.
- **SDK version matters.** Many bugs are fixed in recent releases. Always check the SDK changelog and recommend upgrading if the reported version is old.
