---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/microsoft/azure-skills/azure-kubernetes"
  source_host: "skills.sh"
  source_title: "Azure Kubernetes Service"
  imported_at: "2026-05-01T02:43:17Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-kubernetes"
    confidence: "high"
secrets: {}
---

# Azure Kubernetes Service — Agent Runbook

## Objective

Plan, create, and configure production-ready Azure Kubernetes Service (AKS) clusters. This runbook guides an agent through Day-0 decisions (networking, API server — hard to change later) and Day-1 features (can enable post-creation), covering SKU selection (Automatic vs Standard), networking options (private API server, Azure CNI Overlay, egress configuration), security hardening, and ongoing operations including autoscaling, upgrade strategy, and cost optimization. The agent will gather user requirements, determine the appropriate AKS configuration, and produce a recommended cluster setup with documented rationale for each decision.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`. The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/aks_config.md` | Recommended AKS cluster configuration with all decisions documented |
| `/app/results/cluster_create_command.sh` | Ready-to-run `az aks create` CLI command with all chosen parameters |
| `/app/results/day0_decisions.md` | Summary of Day-0 decisions and rationale (networking, API server, identity) |
| `/app/results/summary.md` | Executive summary with run metadata and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| AKS environment type | `production` | `dev/test` or `production` — affects SKU, SLA, and defaults |
| Region | *(required)* | Azure region for the cluster (e.g., `eastus`, `westeurope`) |
| Availability zones | `1 2 3` | Zones for zone-redundant deployment |
| Node VM size | `Standard_D4s_v5` | Node pool VM SKU (min 4 vCPU recommended for production) |
| Expected node count | `3` | Initial system node pool size |
| API server access | `public` | `public` or `private` |
| Pod IP model | `azure-cni-overlay` | `azure-cni-overlay` (recommended) or `azure-cni` (VNet-routable) |
| Enable KEDA | `true` | Event-driven autoscaling beyond HPA |
| AKS tier | `Standard` | `Free`, `Standard`, or `Premium` (for LTS + SLA) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Primary tool for AKS provisioning (`az aks create`, `az aks show`) |
| `kubectl` | CLI | Yes | Kubernetes cluster management after creation |
| `mcp_azure_mcp_aks` | MCP Tool | Preferred | AKS-specific MCP entry point — discover callable AKS tools first |
| Azure subscription | Credential | Yes | Active subscription with Contributor role on target resource group |
| Azure AD / Entra ID | External | Yes | For managed identity, Workload Identity, and RBAC |

## Step 1: Environment Setup

Verify all required tools and credentials are available before proceeding.

```bash
echo "=== Environment Verification ==="

# Check Azure CLI
az --version | head -1 || { echo "ERROR: Azure CLI not installed"; exit 1; }

# Check kubectl (warn if missing, not a hard blocker at this stage)
kubectl version --client --short 2>/dev/null | head -1 || echo "WARNING: kubectl not found; install before cluster operations"

# Check active Azure subscription (do NOT echo subscription ID back to user)
az account show --query "{name:name, tenantId:tenantId}" -o table 2>&1 || {
  echo "ERROR: Not logged in to Azure. Run: az login"
  exit 1
}

# Create output directory
mkdir -p /app/results
echo "Environment verification complete."
```

If `az account show` fails, guide the user through `az login` or `az login --use-device-code` for non-interactive environments. Do NOT ask the user to paste subscription IDs — resolve context via `az account show`.

## Step 2: Gather Requirements

Collect all required inputs before making Day-0 decisions. Use the MCP tool first, fall back to Azure CLI.

```python
# Use mcp_azure_mcp_aks to discover callable AKS tools
# Then choose the smallest tool that fits the task
```

Ask the user for the following (only what is needed; propose safe defaults if unsure):

1. **AKS environment type**: `dev/test` or `production`
2. **Region(s)**: Azure region(s) and availability zone preferences
3. **Scale**: expected node count, workload size, max pod density
4. **Networking**:
   - API server access: `public` or `private`
   - Pod IP model: Azure CNI Overlay (default, recommended) or Azure CNI VNet-routable
   - Egress control requirements (static outbound IPs, UDR + firewall)
5. **Security & identity**: Workload Identity needs, Key Vault usage, image registry preference
6. **Upgrade strategy**: auto-upgrade channel, maintenance window requirements
7. **Cost constraints**: spot nodes for batch workloads, reserved capacity

Document all gathered inputs in `/app/results/day0_decisions.md` as you go.

## Step 3: Select AKS SKU and Tier

Based on gathered requirements, determine the AKS SKU and tier:

| Decision | AKS Automatic | AKS Standard |
|----------|--------------|--------------|
| Control | Managed best practices | Full control |
| Autoscaling | Node Auto Provisioning (NAP) | Cluster Autoscaler (CAS) |
| Default choice | Yes — for most production workloads | Only when custom networking/autoscaling is required |

**Tier selection**:
- `Free`: dev/test only, no SLA, no zone redundancy
- `Standard`: zone-redundant control plane, 99.95% API server SLA — **recommended for production**
- `Premium`: LTS Kubernetes versions (2-year support) + Defender for Containers

Write tier decision and rationale to `day0_decisions.md`.

## Step 4: Design Networking (Day-0 Critical)

Networking decisions are the hardest to change after cluster creation — document each choice carefully.

### Pod IP Model (Key Day-0 decision)
- **Azure CNI Overlay** (recommended): pod IPs from private overlay range, not VNet-routable; scales to large environments; good for most workloads
- **Azure CNI (VNet-routable)**: pod IPs from VNet subnet — use only when pods must be directly addressable from VNet or on-prem

### Dataplane and Network Policy
- **Azure CNI powered by Cilium** (recommended): eBPF-based for high-performance packet processing, network policies, and observability

### Egress
- **Static Egress Gateway**: for stable, predictable outbound IPs
- **UDR + Azure Firewall / NVA**: for restricted egress environments

### Ingress
- **App Routing addon with Gateway API**: recommended default for HTTP/HTTPS workloads
- **Istio service mesh with Gateway API**: advanced traffic management, mTLS, canary releases
- **Application Gateway for Containers**: L7 load balancing with WAF integration

### DNS
Enable **LocalDNS** on all node pools for reliable, performant DNS resolution.

Append all networking decisions to `day0_decisions.md` with justification.

## Step 5: Configure Security

Apply security best practices (most are Day-1 but plan for them now):

- **Identity**: Microsoft Entra ID everywhere — `--enable-oidc-issuer --enable-workload-identity`; avoid static credentials
- **Secrets**: Azure Key Vault via Secrets Store CSI Driver (`--enable-azure-keyvault-kms`)
- **Policy**: Enable Azure Policy + Deployment Safeguards (`--enable-addons azure-policy`)
- **Encryption**: Encryption at rest for etcd/API server; in-transit for node-to-node
- **Images**: Allow only signed, policy-approved images (Azure Policy + Ratify); prefer Azure Container Registry
- **Isolation**: Use namespaces, network policies, and scoped logging

## Step 6: Generate AKS Cluster Configuration

Synthesize all decisions from Steps 2–5 into a complete `az aks create` command. Populate all parameters from gathered requirements.

```bash
#!/usr/bin/env bash
# AKS Cluster Creation Command
# Generated by: skill-to-runbook-converter v1.0.0
# All parameters should be reviewed and populated before running.

RESOURCE_GROUP="<resource-group>"
CLUSTER_NAME="<cluster-name>"
REGION="<region>"
LOG_ANALYTICS_WS_ID="<log-analytics-workspace-resource-id>"

az aks create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CLUSTER_NAME" \
  --location "$REGION" \
  --tier Standard \
  --zones 1 2 3 \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --node-osdisk-type Ephemeral \
  --os-sku AzureLinux \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --network-dataplane cilium \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --enable-azure-keyvault-kms \
  --enable-addons azure-policy \
  --enable-app-routing \
  --enable-keda \
  --enable-local-dns \
  --auto-upgrade-channel patch \
  --node-os-upgrade-channel NodeImage \
  --generate-ssh-keys
```

Write the populated command to `/app/results/cluster_create_command.sh`.

Also write the full configuration summary to `/app/results/aks_config.md` including:
- Selected SKU and tier with rationale
- All networking choices with justification
- Security features enabled
- Observability setup
- Node pool configuration

## Step 7: Configure Operations (Day-1 Features)

Set up post-creation operational features after the cluster is running.

### Autoscaling
```bash
# Cluster Autoscaler (Standard SKU) — adjust min/max to workload
az aks update \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CLUSTER_NAME" \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10
```

### Observability (Managed Prometheus + Container Insights + Grafana)
```bash
az aks enable-addons \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CLUSTER_NAME" \
  --addons monitoring \
  --workspace-resource-id "$LOG_ANALYTICS_WS_ID"
```

### Spot Node Pools (for batch/interruptible workloads — up to 90% savings)
```bash
az aks nodepool add \
  --resource-group "$RESOURCE_GROUP" \
  --cluster-name "$CLUSTER_NAME" \
  --name spotnodes \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --node-vm-size Standard_D4s_v5 \
  --node-count 1
```

### Fleet Upgrades (multi-cluster staged rollout)
Use **AKS Fleet Manager** to orchestrate staged rollouts from test to production environments.

### Reliability
- Configure `PodDisruptionBudgets` for all production workloads
- Set `topology spread constraints` to distribute pods across hosts/zones
- Enable **Microsoft Defender for Containers** for runtime protection

## Step 8: Iterate on Errors (max 3 rounds)

If any `az aks create` or `az aks update` command fails:

1. Read the full error message from the CLI output
2. Apply the targeted fix from the table below
3. Re-run the failing command
4. Repeat up to 3 times before escalating to the user

| Error / Symptom | Likely Cause | Remediation |
|-----------------|--------------|-------------|
| MCP tool call fails or times out | Invalid credentials or AKS context | Verify `az login`, confirm subscription with `az account show` |
| Quota exceeded | Regional vCPU or resource limits | Request quota increase or select different region/VM SKU |
| Networking conflict — IP exhaustion | Pod subnet too small for overlay/CNI | Re-plan IP ranges; may require cluster recreation (Day-0 decision) |
| Workload Identity not working | Missing OIDC issuer or federated credential | Enable `--enable-oidc-issuer --enable-workload-identity`, configure federated identity |
| 409 Conflict on `az aks create` | Cluster name already exists in resource group | Choose a unique name or update the existing cluster with `az aks update` |
| `ResourceGroupNotFound` | Resource group does not exist | Create it first: `az group create --name "$RESOURCE_GROUP" --location "$REGION"` |

## Step 9: Write Output Files

Confirm all output files are written and non-empty.

```bash
echo "=== Writing output files ==="
[ -s /app/results/cluster_create_command.sh ] && echo "PASS: cluster_create_command.sh" || echo "FAIL: cluster_create_command.sh missing"
[ -s /app/results/aks_config.md ] && echo "PASS: aks_config.md" || echo "FAIL: aks_config.md missing"
[ -s /app/results/day0_decisions.md ] && echo "PASS: day0_decisions.md" || echo "FAIL: day0_decisions.md missing"
[ -s /app/results/summary.md ] && echo "PASS: summary.md" || echo "FAIL: summary.md missing"
[ -s /app/results/validation_report.json ] && echo "PASS: validation_report.json" || echo "FAIL: validation_report.json missing"
echo "Output verification complete."
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/aks_config.md" \
  "$RESULTS_DIR/cluster_create_command.sh" \
  "$RESULTS_DIR/day0_decisions.md" \
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

- [ ] `aks_config.md` documents all Day-0 and Day-1 configuration decisions with rationale
- [ ] `cluster_create_command.sh` contains a populated, ready-to-run `az aks create` command
- [ ] `day0_decisions.md` lists each networking and security decision with justification
- [ ] `summary.md` captures run metadata, environment type, and any issues encountered
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Day-0 decisions are critical.** Networking (pod IP model, API server access) and identity cannot be changed without cluster recreation. Always document these before running `az aks create`.
- **Prefer `mcp_azure_mcp_aks` over Azure CLI.** Use the MCP tool to discover AKS-specific operations; fall back to `az aks` only when the needed functionality is not exposed through the MCP surface.
- **Default to AKS Automatic** unless the user explicitly needs features only available in AKS Standard (custom node pool configs, specific autoscaling setups).
- **Never echo subscription IDs or tokens.** Use `az account show` to resolve context — do not ask users to paste identifiers.
- **Spot nodes require application resilience.** Guide users to configure tolerations for `kubernetes.azure.com/scalesetpriority: spot` and set PodDisruptionBudgets.
- **Use Azure Linux** as the node OS for smaller footprint and faster boot times compared to Ubuntu.
- **For deep-dive scenarios**, load the relevant reference from the source skill repository: `azure-aks-rightsizing.md` (pod rightsizing), `azure-aks-vpa.md` (VPA), `azure-aks-autoscaler.md` (cluster autoscaler), `azure-aks-spot.md` (spot node pools).
- **Stop/start dev/test clusters** to reduce costs: `az aks stop` / `az aks start` — clusters in stopped state do not incur compute charges.
