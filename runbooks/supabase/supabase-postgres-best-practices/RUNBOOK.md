---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices
  source_host: skills.sh
  source_title: Supabase Postgres Best Practices
  imported_at: '2026-05-01T02:59:56Z'
  imported_by: skill-to-runbook-converter@1.0.0
  attribution:
    collection_or_org: supabase
    skill_name: supabase-postgres-best-practices
    confidence: high
---

# Supabase Postgres Best Practices — Agent Runbook

## Objective

Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations.

This runbook operationalizes the Supabase Postgres Best Practices skill as a Jetty-deployable agent task. The agent applies 8 categories of Postgres performance optimization rules — from critical query performance and connection management guidance to incremental advanced-feature recommendations — to a target database context. It produces structured output reports covering identified issues, recommended SQL changes, and verification steps.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the optimization review |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/query_performance.md` | Query performance findings and recommendations (Priority 1 — CRITICAL) |
| `/app/results/connection_management.md` | Connection pooling and management findings (Priority 2 — CRITICAL) |
| `/app/results/security_rls.md` | Security and Row-Level Security findings (Priority 3 — CRITICAL) |
| `/app/results/schema_design.md` | Schema design recommendations (Priority 4 — HIGH) |
| `/app/results/concurrency_locking.md` | Concurrency and locking findings (Priority 5 — MEDIUM-HIGH) |
| `/app/results/data_access_patterns.md` | Data access pattern recommendations (Priority 6 — MEDIUM) |
| `/app/results/monitoring_diagnostics.md` | Monitoring and diagnostics setup (Priority 7 — LOW-MEDIUM) |
| `/app/results/advanced_features.md` | Advanced Postgres feature recommendations (Priority 8 — LOW) |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target schema | *(required)* | The database schema or SQL file to analyze |
| Postgres version | `15` | Target Postgres version for compatibility checks |
| Supabase mode | `true` | Apply Supabase-specific recommendations (RLS, pgBouncer, etc.) |
| Rule categories | `all` | Comma-separated list of categories to apply, or `all` |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `psql` or SQL input files | CLI/File | Yes | Target SQL schema, queries, or migration files to analyze |
| Supabase CLI | CLI | Optional | For Supabase-specific RLS and connection pooling checks |
| `EXPLAIN ANALYZE` access | DB access | Optional | For query plan analysis; can use provided EXPLAIN output |
| `pg_stat_statements` | Postgres extension | Optional | For monitoring and diagnostics recommendations |

## Step 1: Environment Setup

```bash
# Verify required tools
command -v psql >/dev/null 2>&1 && echo "psql present" || echo "psql not found (analysis will use provided SQL files)"

# Create output directories
mkdir -p /app/results

# Verify input parameters
if [ -z "$TARGET_SCHEMA" ] && [ -z "$SQL_INPUT" ]; then
  echo "WARNING: No target schema specified. Using interactive mode."
fi

echo "=== Environment ready ==="
echo "Results dir: /app/results"
echo "Postgres Best Practices version: 1.1.1 (Supabase, January 2026)"
```

## Step 2: Load and Index the Best Practices Rules

Load the 8-category rule framework from the Supabase Postgres Best Practices skill.

### Rule Categories by Priority

| Priority | Category | Impact | Prefix | Key Rules |
|----------|----------|--------|--------|-----------|
| 1 | Query Performance | CRITICAL | `query-` | missing-indexes, partial-indexes, composite-indexes, covering-indexes, index-types |
| 2 | Connection Management | CRITICAL | `conn-` | pooling, limits, idle-timeout, prepared-statements |
| 3 | Security & RLS | CRITICAL | `security-` | row-level-security |
| 4 | Schema Design | HIGH | `schema-` | data-types, constraints |
| 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` | deadlock-prevention, advisory, skip-locked, short-transactions |
| 6 | Data Access Patterns | MEDIUM | `data-` | n-plus-one, batch-inserts, pagination, upsert |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM | `monitor-` | explain-analyze, pg-stat-statements, vacuum-analyze |
| 8 | Advanced Features | LOW | `advanced-` | full-text-search, jsonb-indexing |

Reference the individual rule files in the source skill repository:
- `references/query-missing-indexes.md`
- `references/query-partial-indexes.md`
- `references/_sections.md`

## Step 3: Analyze Query Performance (CRITICAL — Priority 1)

Apply `query-*` rules to identify missing indexes, suboptimal index usage, and query patterns.

For each query in the target schema/workload:
1. Check for sequential scans on large tables (missing indexes)
2. Identify partial index opportunities (WHERE clauses with selective conditions)
3. Check composite index column ordering (most selective first)
4. Verify covering indexes for hot query paths
5. Confirm correct index types (GIN for JSONB/arrays, GiST for geometry, BRIN for time-series)

Write findings to `/app/results/query_performance.md` with:
- Missing index candidates with CREATE INDEX statements
- Incorrect vs. correct SQL examples for each finding
- EXPLAIN output analysis where available
- Estimated performance impact

## Step 4: Analyze Connection Management (CRITICAL — Priority 2)

Apply `conn-*` rules to review pooling configuration, connection limits, and prepared statement handling.

Check for:
1. PgBouncer configuration (transaction vs session mode — Supabase default: transaction mode on port 6543)
2. `max_connections` setting vs actual peak usage
3. `idle_in_transaction_session_timeout` configuration (recommended: 30s–60s)
4. Prepared statement compatibility (must use direct connection port 5432 when using prepared statements)

Write findings to `/app/results/connection_management.md`.

## Step 5: Analyze Security & RLS (CRITICAL — Priority 3)

Apply `security-*` rules to verify Row-Level Security policies are correctly configured.

Check for:
1. Tables without RLS enabled that contain user-scoped data
2. Overly permissive policies (`USING (true)` without intent)
3. SECURITY DEFINER function risks
4. `auth.uid()` usage patterns and performance implications

Write findings to `/app/results/security_rls.md` with correct policy SQL examples.

## Step 6: Analyze Lower-Priority Categories (Priorities 4–8)

Apply remaining rule categories in priority order.
Write each category's findings to its designated output file (see REQUIRED OUTPUT FILES).

For each category, follow the rule file structure:
- Brief explanation of why the issue matters
- Incorrect SQL example with explanation
- Correct SQL example with explanation
- Optional EXPLAIN output or performance metrics
- Supabase-specific notes where applicable

## Step 7: Iterate on Errors (max 3 rounds)

If any output file from Steps 3–6 is empty or contains only placeholder text after agent execution:

1. Read the specific failed check from `validation_report.json`
2. Apply the targeted fix from the Common Fixes table below
3. Re-run the affected step and overwrite the output file
4. Re-evaluate
5. Repeat up to 3 times total

After 3 rounds, if any CRITICAL category output is still empty, abort with `overall_passed=false`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| No SQL to analyze | Document that input is required; write placeholder with specific schema questions |
| EXPLAIN output unavailable | Apply rules based on query patterns alone; note where EXPLAIN would add value |
| Supabase-specific rules not applicable | Skip gracefully with a note in the output file |
| RLS analysis requires auth context | Document the auth schema assumptions made |
| Missing output file | Re-run the corresponding step and write the file |

## Step 8: Write Validation Report

Write `/app/results/validation_report.json` with all stage results:

```json
{
  "version": "1.0.0",
  "stages": [
    { "name": "query_performance",      "passed": true, "message": "..." },
    { "name": "connection_management",  "passed": true, "message": "..." },
    { "name": "security_rls",           "passed": true, "message": "..." },
    { "name": "schema_design",          "passed": true, "message": "..." },
    { "name": "concurrency_locking",    "passed": true, "message": "..." },
    { "name": "data_access_patterns",   "passed": true, "message": "..." },
    { "name": "monitoring_diagnostics", "passed": true, "message": "..." },
    { "name": "advanced_features",      "passed": true, "message": "..." }
  ],
  "overall_passed": true
}
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/query_performance.md" \
  "$RESULTS_DIR/connection_management.md" \
  "$RESULTS_DIR/security_rls.md" \
  "$RESULTS_DIR/schema_design.md" \
  "$RESULTS_DIR/concurrency_locking.md" \
  "$RESULTS_DIR/data_access_patterns.md" \
  "$RESULTS_DIR/monitoring_diagnostics.md" \
  "$RESULTS_DIR/advanced_features.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] All 8 category output files exist and are non-empty
- [ ] `summary.md` exists with findings summary table populated
- [ ] `validation_report.json` exists with `overall_passed` field
- [ ] CRITICAL category findings (query, connection, security) reviewed first
- [ ] All SQL recommendations include both incorrect and correct examples
- [ ] Supabase-specific notes included where applicable
- [ ] References verified and accessible

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Apply rules in priority order.** CRITICAL rules (query performance, connection management, security) have the highest impact and should be analyzed first.
- **Each rule has a specific structure.** Follow the pattern: why it matters → incorrect SQL → correct SQL → EXPLAIN output (optional) → performance metrics.
- **Supabase-specific guidance.** In Supabase mode, pay extra attention to RLS policies, pgBouncer transaction mode compatibility, and `auth.uid()` function usage.
- **Index selection matters.** Use GIN for JSONB/arrays/full-text, GiST for geometry/ranges, BRIN for time-series append-only data, and B-tree for everything else.
- **Connection pooling in Supabase.** Supabase uses pgBouncer in transaction mode by default — prepared statements must use the session-mode connection string (port 5432) rather than the pooler (port 6543).
- **RLS performance.** Poorly written RLS policies can cause sequential scans even on indexed columns. Always test with `EXPLAIN ANALYZE` and `SET role` to simulate user context.
