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
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "microsoft"
    skill_name: "azure-kubernetes"
    confidence: "high"
secrets: {}
---

# Azure Kubernetes Service — Agent Runbook

## Objective

Plan, create, and configure production-ready Azure Kubernetes Service (AKS) clusters. This runbook covers the full Day-0 decision checklist — SKU selection (Automatic vs Standard), networking options (private API server, Azure CNI Overlay, egress configuration), security hardening, and Day-1 operations including autoscaling, upgrade strategy, observability setup, and cost analysis. Use this runbook when provisioning a new AKS environment, designing AKS networking, securing an AKS cluster, enabling AKS observability, or optimizing AKS cost and performance. The agent will gather requirements, apply authoritative Microsoft guidance, and produce a complete, validated cluster configuration recommendation.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/cluster_config.md` | Recommended AKS cluster configuration with all Day-0 decisions documented |
| `/app/results/az_commands.sh` | Ready-to-run `az aks create` and related CLI commands reflecting the chosen configuration |
| `/app/results/summary.md` | Executive summary: cluster type, networking model, key decisions, and any open items |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| AKS environment type | `production` | `dev/test` or `production` — affects SKU, redundancy, and cost defaults |
| Azure region | *(required)* | Target Azure region (e.g., `eastus`, `westeurope`) |
| Availability zones | `1 2 3` | Comma-separated AZ list; use `""` for regions without zone support |
| Cluster name | *(required)* | Name for the AKS cluster resource |
| Resource group | *(required)* | Existing or new Azure resource group name |
| AKS SKU | `Automatic` | `Automatic` (default, recommended) or `Standard` (full control) |
| Node VM size | `Standard_D4s_v5` | System node pool VM size; avoid B-series |
| Node count (system pool) | `3` | Minimum 2 for production |
| Networking model | `azure-cni-overlay` | `azure-cni-overlay` (recommended) or `azure-cni` |
| Enable private API server | `false` | Set `true` to restrict API server access to VNet |
| Dry run | `false` | If `true`, generate config and commands but do not execute `az aks create` |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `az` (Azure CLI) | CLI | Yes | Primary interface for AKS cluster operations |
| `kubectl` | CLI | Yes | Kubernetes control-plane interaction and workload validation |
| `jq` | CLI | Yes | Parse JSON output from `az` and `kubectl` commands |
| Azure subscription | Credential | Yes | Active subscription with Contributor or AKS Cluster Admin role |
| `mcp_azure_mcp_aks` | MCP Tool | Preferred | AKS-specific MCP tool; discover available tools before falling back to CLI |
| `requests` | Python package | Yes | HTTP fetch of supplementary reference files if needed |

## Step 1: Environment Setup

```bash
# Verify CLI tools
command -v az     >/dev/null || { echo "ERROR: az not installed"; exit 1; }
command -v kubectl>/dev/null || { echo "ERROR: kubectl not installed"; exit 1; }
command -v jq     >/dev/null || { echo "ERROR: jq not installed"; exit 1; }

# Confirm active Azure subscription (do NOT echo subscription IDs back to user)
az account show --query "{name:name, state:state}" -o table

# Create output directory
mkdir -p /app/results

# Verify GITHUB_PAT or Azure credentials are available
az account list --query "[?isDefault].{name:name}" -o tsv
```

Confirm all tools are available and the correct subscription is active before proceeding. If `az account show` fails, run `az login` and set the target subscription with `az account set`.

## Step 2: Gather Requirements

Ask the user only for information not already provided in parameters. Apply safe defaults for anything not specified:

| Requirement | Default | Notes |
|-------------|---------|-------|
| Environment type | `production` | Affects HA, tier, cost settings |
| Region | *(ask)* | Must support AZ for production |
| Node VM size | `Standard_D4s_v5` | Min 4 vCPU; avoid B-series |
| Networking model | Azure CNI Overlay | Recommended for most workloads |
| API server access | Public | Private requires additional VNet setup |
| Identity model | Workload Identity + Managed Identity | Avoids static credentials |
| Observability | Managed Prometheus + Container Insights + Grafana | Full stack recommended |
| Upgrade policy | Auto-upgrade control plane + node OS | Keeps security patches current |
| Cost constraints | *(ask)* | May affect SKU, reserved instances, Spot pools |

Document collected requirements. If a Day-0 decision (networking model, API server access) is ambiguous, ask a clarifying question before proceeding — these are hard to change post-creation.

## Step 3: Determine AKS SKU

```bash
# AKS SKU decision logic
# Default: AKS Automatic (curated best practices, includes NAP, reduced operational overhead)
# Use AKS Standard if:
#   - Custom networking not supported by NAP
#   - Advanced node pool configuration required
#   - Full control over autoscaling configuration needed

echo "Cluster type decision: AKS Automatic (default)"
echo "Override to Standard only if specific customization requirements exist"
```

**AKS Automatic** (recommended default): Pre-configured security, reliability, performance. Includes Node Auto Provisioning (NAP). Best for most production workloads.

**AKS Standard**: Full control over all cluster settings. Additional operational overhead. Use only if Automatic SKU cannot satisfy requirements.

Document the SKU choice and rationale in `/app/results/cluster_config.md`.

## Step 4: Design Networking (Day-0 — Irreversible)

Networking decisions are the most critical Day-0 choices. Document all decisions with rationale.

### Pod IP Model

| Option | Recommendation | When to Use |
|--------|---------------|-------------|
| **Azure CNI Overlay** | ✅ Recommended | Most workloads; pod IPs from private overlay, not VNet-routable; scales to large environments |
| **Azure CNI (VNet-routable)** | Situational | Pods must be directly addressable from VNet or on-premises |

### Dataplane & Network Policy

- **Azure CNI powered by Cilium** (recommended): eBPF-based, high-performance, rich observability, network policy enforcement.

### Egress

- **Static Egress Gateway**: Stable, predictable outbound IPs — recommended for regulated workloads.
- Restricted egress: UDR + Azure Firewall or NVA.

### Ingress

| Option | Use Case |
|--------|----------|
| App Routing addon + Gateway API | Default for HTTP/HTTPS workloads |
| Istio service mesh + Gateway API | Advanced traffic management, mTLS, canary releases |
| Application Gateway for Containers | L7 load balancing with WAF integration |

### DNS

Enable **LocalDNS** on all node pools for reliable, performant DNS resolution.

```bash
# Generate networking parameters for cluster creation
POD_CIDR="192.168.0.0/16"   # Overlay CIDR — not routable in VNet
NETWORK_PLUGIN="azure"
NETWORK_PLUGIN_MODE="overlay"
NETWORK_DATAPLANE="cilium"
echo "Networking: CNI Overlay + Cilium dataplane"
```

## Step 5: Configure Security

```bash
# Security configuration flags
SECURITY_FLAGS=(
  "--enable-aad"
  "--enable-azure-rbac"
  "--enable-oidc-issuer"
  "--enable-workload-identity"
  "--enable-secret-rotation"     # Secrets Store CSI Driver
  "--enable-azure-policy"
  "--enable-encryption-at-host"
  "--node-os-upgrade-channel NodeImage"
)
echo "Security: Entra ID RBAC + Workload Identity + Policy + Encryption at Host"
```

**Security checklist:**
- [ ] Microsoft Entra ID for control plane and pod identity (Workload Identity)
- [ ] Azure Key Vault via Secrets Store CSI Driver — no static credentials
- [ ] Azure Policy + Deployment Safeguards enabled
- [ ] Encryption at rest for etcd/API server; in-transit for node-to-node
- [ ] Only signed, policy-approved images (Azure Policy + Ratify) from Azure Container Registry
- [ ] Namespace isolation + network policies scoped per workload

## Step 6: Configure Observability

```bash
# Enable Managed Prometheus + Container Insights + Grafana
OBSERVABILITY_FLAGS=(
  "--enable-azure-monitor-metrics"
  "--enable-container-log-v2"
  "--workspace-resource-id <LOG_ANALYTICS_WORKSPACE_ID>"
)

# Enable Diagnostic Settings for control plane logs (post-creation)
az monitor diagnostic-settings create \
  --name "aks-diagnostics" \
  --resource "<AKS_RESOURCE_ID>" \
  --logs '[{"category":"kube-apiserver","enabled":true},{"category":"kube-audit","enabled":true}]' \
  --workspace "<LOG_ANALYTICS_WORKSPACE_ID>"
```

**Observability stack:**
- Managed Prometheus + Grafana: metrics and dashboards
- Container Insights: log collection (ContainerLogV2)
- Diagnostic Settings: control plane + audit logs → Log Analytics
- Additional: Application Insights, Resource Health Center, AppLens detectors, Azure Advisor

## Step 7: Configure Upgrades, Performance, and Node Pools

```bash
# Upgrade strategy
UPGRADE_FLAGS=(
  "--auto-upgrade-channel stable"
  "--node-os-upgrade-channel NodeImage"
  "--maintenance-window-config @maintenance-window.json"
)

# Performance
PERF_FLAGS=(
  "--node-osdisk-type Ephemeral"
  "--os-sku AzureLinux"
)

# Node pool — system pool spec
SYSTEM_POOL_FLAGS=(
  "--node-count 3"
  "--min-count 2"
  "--max-count 10"
  "--zones 1 2 3"
  "--vm-set-type VirtualMachineScaleSets"
  "--enable-cluster-autoscaler"
)
```

**Node pool guidance:**
- Dedicated system node pool: min 2 nodes, tainted `CriticalAddonsOnly=true:NoSchedule`
- Enable Node Auto Provisioning (NAP) for cost-efficient responsive scaling
- Use latest-gen SKUs (v5/v6): min 4 vCPU, avoid B-series burstable VMs
- Topology spread constraints to distribute pods across hosts/zones per SLO

## Step 8: Reliability and Cost Controls

**Reliability checklist:**
- [ ] 3 Availability Zones deployed (`--zones 1 2 3`)
- [ ] Standard tier for zone-redundant control plane + 99.95% SLA
- [ ] Microsoft Defender for Containers enabled (runtime protection)
- [ ] PodDisruptionBudgets configured for all production workloads
- [ ] Topology spread constraints for pod distribution across failure domains

**Cost controls:**
- Spot node pools for batch/interruptible workloads (up to 90% savings): `az aks nodepool add --priority Spot`
- Stop/start dev/test clusters: `az aks stop` / `az aks start`
- Reserved Instances or Savings Plans for steady-state workloads

## Step 9: Generate and Write Cluster Configuration

Assemble all decisions into the output files:

```bash
# Write cluster_config.md with all decisions documented
cat > /app/results/cluster_config.md << 'EOF'
# AKS Cluster Configuration

## Day-0 Decisions
...
EOF

# Write az_commands.sh with full create command
cat > /app/results/az_commands.sh << 'SHELL'
#!/usr/bin/env bash
# Generated AKS cluster creation commands
# Review before executing — especially resource group and subscription context

CLUSTER_NAME="<cluster-name>"
RG="<resource-group>"
REGION="<region>"
K8S_VERSION="$(az aks get-versions --location $REGION --query 'orchestrators[-1].orchestratorVersion' -o tsv)"

az aks create \
  --name "$CLUSTER_NAME" \
  --resource-group "$RG" \
  --location "$REGION" \
  --tier Standard \
  --sku automatic \
  --kubernetes-version "$K8S_VERSION" \
  --node-count 3 \
  --min-count 2 \
  --max-count 10 \
  --node-vm-size Standard_D4s_v5 \
  --zones 1 2 3 \
  --node-osdisk-type Ephemeral \
  --os-sku AzureLinux \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --network-dataplane cilium \
  --enable-aad \
  --enable-azure-rbac \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --enable-azure-policy \
  --enable-encryption-at-host \
  --auto-upgrade-channel stable \
  --node-os-upgrade-channel NodeImage \
  --enable-cluster-autoscaler \
  --enable-azure-monitor-metrics \
  --enable-container-log-v2
SHELL
chmod +x /app/results/az_commands.sh
```

## Step 10: Iterate on Errors (max 3 rounds)

If any validation check or `az aks create` command fails:

1. Read the specific error message from the CLI or validation output
2. Apply the targeted fix from the Common Fixes table below
3. Re-run the relevant step and re-validate
4. Repeat up to 3 times total; abort with documented failure if still failing after 3 rounds

### Common Fixes

| Error / Symptom | Likely Cause | Remediation |
|-----------------|--------------|-------------|
| MCP tool call fails or times out | Invalid credentials or subscription context | Verify `az login`, confirm subscription with `az account show` |
| Quota exceeded | Regional vCPU or resource limits | Request quota increase or select different region/VM SKU |
| Networking conflict (IP exhaustion) | Pod subnet too small for overlay/CNI | Re-plan IP ranges; may require cluster recreation (Day-0 decision) |
| Workload Identity not working | Missing OIDC issuer or federated credential | Enable `--enable-oidc-issuer --enable-workload-identity`, configure federated identity |
| `az aks create` SKU not available | Region doesn't support AKS Automatic | Fall back to Standard SKU with equivalent flags |
| Validation JSON missing required sections | Template gap | Add missing section per runbook spec and re-validate |

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/cluster_config.md" \
  "$RESULTS_DIR/az_commands.sh" \
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

- [ ] `cluster_config.md` documents all Day-0 decisions with rationale
- [ ] `az_commands.sh` contains a ready-to-run cluster creation command
- [ ] Networking model is explicitly chosen and documented (not left as default)
- [ ] Security: Entra ID, Workload Identity, Policy, Encryption all configured
- [ ] Observability: Prometheus, Container Insights, Grafana, Diagnostic Settings
- [ ] Reliability: 3 AZs, Standard tier, PDB guidance, topology spread
- [ ] Cost: Spot pool guidance and stop/start documented if applicable
- [ ] `summary.md` exists and summarizes the full configuration
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer AKS Automatic for new clusters.** It encodes Microsoft's current best practices and reduces the operational burden of managing node pools, scaling, and security baselines manually.
- **Day-0 networking decisions are permanent.** Pod IP model and API server access mode cannot be changed post-creation without recreating the cluster — gather these requirements carefully before running `az aks create`.
- **Never echo subscription IDs or tokens.** Use `az account show` and MCP tools to discover context; do not reflect subscription identifiers back to the user.
- **Use `--dry-run` for quota preflight.** Run `az aks create ... --dry-run` to validate the request and catch quota or validation errors before spending provisioning time.
- **MCP-first, CLI-fallback.** Always discover and prefer `mcp_azure_mcp_aks` tools; fall back to `az aks` CLI only when the needed operation is not exposed via MCP.
- **Attribution low-confidence is not a blocker.** If the origin URL pattern is ambiguous, flag it in `summary.md` for human review before merging.
- **AKS Automatic does not support all node pool customizations.** If NAP cannot satisfy requirements (e.g., GPU pools, specific VM families), switch to Standard SKU and document the reason.
