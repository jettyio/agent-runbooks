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
---

# Azure Messaging SDK Troubleshooting — Agent Runbook

## Objective

This runbook guides an AI agent through diagnosing and resolving Azure Messaging SDK issues for Azure Event Hubs and Azure Service Bus. It covers SDK connection failures, authentication errors, AMQP link errors, message lock issues, session errors, event processor failures, and configuration questions. The agent will use MCP tools to check resource health, query diagnostic logs, look up documentation, and recommend targeted fixes with citations.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the troubleshooting session: issue identified, steps taken, fix recommended, docs cited |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/diagnosis.md` | Full diagnosis narrative: SDK/version identified, error matched, configuration reviewed, fix recommended |
| `/app/results/fix_commands.md` | Concrete remediation steps (code snippets, config changes, or CLI commands) for the identified issue |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| SDK language | *(required)* | Target SDK language: `python`, `java`, `dotnet`, `javascript`, `go` |
| Error message | *(required)* | The error or symptom reported by the user |
| Namespace name | *(optional)* | Azure Event Hubs or Service Bus namespace name for resource health checks |
| Entity name | *(optional)* | Queue, topic, hub, or consumer group name |
| Subscription ID | *(optional)* | Azure subscription ID for resource health queries |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `mcp_azure_mcp_eventhubs` | MCP Tool | Conditional | List namespaces, hubs, consumer groups (Event Hubs issues) |
| `mcp_azure_mcp_servicebus` | MCP Tool | Conditional | List namespaces, queues, topics, subscriptions (Service Bus issues) |
| `mcp_azure_mcp_monitor` | MCP Tool | Recommended | Query diagnostic logs with KQL (`logs_query`) |
| `mcp_azure_mcp_resourcehealth` | MCP Tool | Recommended | Check service health status (`get`) |
| `mcp_azure_mcp_documentation` | MCP Tool | Yes | Search Microsoft Learn for troubleshooting docs |

---

## Step 1: Environment Setup

```bash
echo "=== Azure Messaging SDK Troubleshooting ==="
mkdir -p /app/results
echo "Results directory ready"

# Confirm required inputs are available
echo "SDK language: ${SDK_LANGUAGE:-'(check prompt)'}"
echo "Error message: ${ERROR_MESSAGE:-'(check prompt)'}"
echo "Namespace: ${NAMESPACE_NAME:-'(optional - not provided)'}"
echo "Entity: ${ENTITY_NAME:-'(optional - not provided)'}"
```

At the start of the session:
1. Read the user's prompt carefully to identify the SDK language, SDK version (if mentioned), and the exact error message or symptom.
2. Record these values for use in subsequent steps.
3. If the SDK language or error is ambiguous, note the ambiguity and proceed with diagnosis — ask the user at the end if needed.

**Services covered:** Azure Event Hubs, Azure Service Bus

**When to use this runbook:**
- SDK connection failures, auth errors, or AMQP link errors
- Idle timeout, connection inactivity, or slow reconnection after disconnect
- AMQP link detach or detach-forced errors
- Message lock lost, message lock expired, lock renewal failures, or batch lock timeouts
- Session lock lost, session lock expired, or session receiver errors
- Event processor or message handler stops processing
- Duplicate events or checkpoint offset resets
- SDK configuration questions (retry, prefetch, batch size, receive batch behavior)

---

## Step 2: Identify SDK and Version

Parse the user's prompt to extract:
- **SDK language**: Python (`azure-eventhub`, `azure-servicebus`), Java (`azure-messaging-eventhubs`, `azure-messaging-servicebus`), .NET (`Azure.Messaging.EventHubs`, `Azure.Messaging.ServiceBus`), JavaScript/TypeScript (`@azure/event-hubs`, `@azure/service-bus`), Go (`azeventhubs`, `azservicebus`)
- **SDK version**: Look for version strings in stack traces, `requirements.txt`, `pom.xml`, `*.csproj`, `package.json`, or `go.mod`
- **Service type**: Event Hubs or Service Bus (infer from error messages, entity names, or MCP tool references)

Write the identified SDK and version to `/app/results/diagnosis.md` with a section header `## SDK Identification`.

If the SDK or version is not stated, note this and continue — do not block on it.

---

## Step 3: Check Resource Health

Use `mcp_azure_mcp_resourcehealth` to verify the namespace is healthy before blaming the SDK:

```
mcp_azure_mcp_resourcehealth get --resource-type Microsoft.EventHub/namespaces --resource-name <namespace>
# or for Service Bus:
mcp_azure_mcp_resourcehealth get --resource-type Microsoft.ServiceBus/namespaces --resource-name <namespace>
```

- If the namespace is **degraded or unavailable**: report the service health issue as the likely root cause, and instruct the user to wait for Azure recovery or failover.
- If the namespace is **healthy**: proceed to Step 4.

Append the health check result to `/app/results/diagnosis.md`.

---

## Step 4: Match Error to Troubleshooting Guide

Use `mcp_azure_mcp_documentation` to search Microsoft Learn for the specific error or symptom:

```
mcp_azure_mcp_documentation search --query "<error message or symptom>"
```

Match the error against these known categories and apply the corresponding guide:

| Error Category | Key Symptoms | Guide Search Term |
|----------------|-------------|-------------------|
| Authentication / Auth | `AuthenticationError`, `UnauthorizedAccessException`, `401`, `403` | `azure messaging sdk authentication troubleshooting` |
| Connection / AMQP | `AmqpException`, `ConnectionResetByPeer`, `TimeoutException`, AMQP link detach | `azure messaging sdk amqp connection troubleshooting` |
| Message Lock | `MessageLockLostException`, lock expired, lock renewal failed | `azure service bus message lock troubleshooting` |
| Session Lock | `SessionLockLostException`, session receiver errors | `azure service bus session lock troubleshooting` |
| Event Processor | Processor stops, no events received, partition ownership | `azure event hubs event processor troubleshooting` |
| Checkpointing | Duplicate events, offset resets, stale checkpoints | `azure event hubs checkpoint troubleshooting` |
| Configuration | Retry policy, prefetch count, batch size questions | `azure messaging sdk configuration best practices` |

Append the matched category and the documentation URL(s) found to `/app/results/diagnosis.md`.

---

## Step 5: Review Diagnostic Logs

If a namespace name is available, query diagnostic logs with KQL using `mcp_azure_mcp_monitor`:

```
mcp_azure_mcp_monitor logs_query --workspace <workspace-id> --query "
AzureDiagnostics
| where ResourceType == 'EVENTHUBS' or ResourceType == 'SERVICEBUS'
| where ResourceId contains '<namespace-name>'
| where TimeGenerated > ago(1h)
| where Level == 'Error' or Level == 'Warning'
| order by TimeGenerated desc
| limit 50
"
```

Alternatively, list namespace/entity metadata to verify configuration:
- Event Hubs: `mcp_azure_mcp_eventhubs` (list namespaces, hubs, consumer groups)
- Service Bus: `mcp_azure_mcp_servicebus` (list namespaces, queues, topics, subscriptions)

Append relevant log findings to `/app/results/diagnosis.md`.

---

## Step 6: Check Configuration

Review the SDK configuration for common misconfigurations. Key settings to verify:

| Setting | Event Hubs | Service Bus | Common Issue |
|---------|-----------|-------------|--------------|
| Connection string | Correct namespace + SAS key | Correct namespace + SAS key | Wrong namespace endpoint |
| Entity name | Hub name + consumer group | Queue or topic name | Typo or case mismatch |
| Retry policy | `ExponentialRetry` (recommended) | `ServiceBusRetryPolicy` | No retry or too-short timeout |
| Prefetch count | 300 (default) | 0 (default) | Set too high causes memory issues |
| Batch size | 1–100 events | 1–100 messages | Too large causes lock expiry |
| Lock renewal | N/A | Auto-renew recommended | Disabled lock renewal = lock lost |

Ask the user to share relevant configuration snippets if not already provided. Append findings to `/app/results/diagnosis.md`.

---

## Step 7: Iterate on Errors (max 3 rounds)

If the initial diagnosis is unclear or the recommended fix did not resolve the issue:

1. Re-read the error message and the user's follow-up
2. Search `mcp_azure_mcp_documentation` with a refined query (include SDK language and version)
3. Run an additional log query (Step 5) with a wider time window or different filter
4. Update `/app/results/diagnosis.md` and `/app/results/fix_commands.md`
5. Repeat up to 3 times total

After 3 rounds, if the issue is still unresolved, escalate by providing:
- The best hypothesis based on available information
- A link to the Azure SDK GitHub Issues for the relevant language repository
- Instructions for enabling verbose SDK logging for deeper tracing

---

## Step 8: Recommend Fix

Based on the diagnosis, write concrete remediation steps to `/app/results/fix_commands.md`:

- Include language-specific code snippets (Python, Java, .NET, JavaScript, or Go)
- Cite the Microsoft Learn documentation URL(s) found in Step 4
- Provide the minimal configuration change (e.g., enable lock renewal, adjust retry policy, fix entity name)
- Include a verification step the user can run to confirm the fix worked

**Example fix structure (Python / Service Bus message lock):**

```python
# Fix: Enable auto-lock renewal to prevent MessageLockLostException
from azure.servicebus import ServiceBusClient

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_queue_receiver(
        queue_name="my-queue",
        max_wait_time=30,
        auto_lock_renewer=AutoLockRenewer(max_lock_renewal_duration=300)  # 5 minutes
    ) as receiver:
        for msg in receiver:
            # process message
            receiver.complete_message(msg)
```

---

## Step 9: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/diagnosis.md" \
  "$RESULTS_DIR/fix_commands.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] SDK language and version identified (or noted as unavailable)
- [ ] Resource health checked via `mcp_azure_mcp_resourcehealth`
- [ ] Error matched to a troubleshooting category
- [ ] Microsoft Learn documentation found and cited
- [ ] Diagnostic logs reviewed (if namespace available)
- [ ] Configuration reviewed for common misconfigurations
- [ ] Fix recommended with language-specific code snippet
- [ ] `diagnosis.md` written with full narrative
- [ ] `fix_commands.md` written with concrete steps
- [ ] `summary.md` written with brief overview and doc links
- [ ] `validation_report.json` written with `overall_passed`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Check resource health first.** Many SDK errors are actually Azure service disruptions — `mcp_azure_mcp_resourcehealth` can save significant debugging time.
- **AMQP errors are often transient.** An `AmqpException` with `ErrorCondition.ConnectionForced` usually means Azure closed an idle connection — the fix is enabling keepalives or reconnect logic, not a code bug.
- **Message lock errors correlate with processing time.** If `MessageLockLostException` appears, the message processing is taking longer than the lock duration. Fix: enable `AutoLockRenewer` or reduce processing batch size.
- **Event processor stalls often mean partition ownership contention.** If two processor instances both claim ownership, one will stop receiving. Fix: verify storage account checkpoint configuration and ensure only one processor group runs per consumer group.
- **Always cite docs.** Use `mcp_azure_mcp_documentation` to find the exact Microsoft Learn article for the error — link it in your fix recommendation so the user can read the full context.
- **Language matters for error names.** The same underlying error has different class names in each SDK: Python uses `EventHubError`/`ServiceBusError`, .NET uses `EventHubsException`/`ServiceBusException`, Java uses `AmqpException`, etc.
