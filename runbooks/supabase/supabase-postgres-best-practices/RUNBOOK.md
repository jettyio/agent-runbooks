---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices"
  source_host: "skills.sh"
  source_title: "Supabase Postgres Best Practices"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "supabase"
    skill_name: "supabase-postgres-best-practices"
    confidence: "high"
secrets: {}
---

# Supabase Postgres Best Practices — Agent Runbook

## Objective

Apply Postgres performance optimization best practices from Supabase when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations. This runbook covers eight prioritized categories — from critical concerns like query performance, connection management, and security/RLS to incremental improvements in advanced features. Each category provides structured guidance with correct and incorrect SQL examples, EXPLAIN output, and performance metrics to guide automated optimization and code generation. Use this runbook whenever working with Supabase-hosted Postgres databases or any Postgres environment requiring performance tuning.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the optimization run, issues found, and recommendations applied |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/optimization_report.md` | Detailed report of all checks performed and recommendations across all 8 rule categories |
| `/app/results/sql_review.md` | Annotated SQL review output with flagged issues and suggested rewrites |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target database URL | *(required)* | PostgreSQL connection string (e.g. `postgres://user:pass@host:5432/db`) |
| Schema name | `public` | Schema to analyze (default: `public`) |
| Rule categories | `all` | Comma-separated list of categories to apply, or `all` |
| Severity threshold | `MEDIUM` | Minimum severity to report: `CRITICAL`, `HIGH`, `MEDIUM-HIGH`, `MEDIUM`, `LOW-MEDIUM`, `LOW` |
| Dry run | `false` | If `true`, analyze and report without applying any fixes |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `psql` | CLI | Yes | Run queries and introspection against the target Postgres database |
| `python3` | Runtime | Yes | Execute analysis scripts |
| `requests` | Python package | Yes | Fetch latest rule references if needed |
| `pyyaml` | Python package | Yes | Parse skill and configuration files |
| PostgreSQL ≥ 13 | External | Yes | Target database; some rules require pg_stat_statements extension |

## Step 1: Environment Setup

Verify all required tools and access are available before proceeding.

```bash
# Verify psql is available
command -v psql >/dev/null || { echo "ERROR: psql not installed"; exit 1; }

# Verify Python packages
python3 -c "import requests, yaml" || pip install requests pyyaml

# Verify database connectivity
psql "$TARGET_DATABASE_URL" -c "SELECT version();" || { echo "ERROR: cannot connect to database"; exit 1; }

# Verify pg_stat_statements is available (recommended for query analysis)
psql "$TARGET_DATABASE_URL" -c "SELECT * FROM pg_stat_statements LIMIT 1;" 2>/dev/null \
  && echo "pg_stat_statements: available" \
  || echo "WARNING: pg_stat_statements not available — some query-performance rules will be skipped"

# Create output directory
mkdir -p /app/results
```

## Step 2: Collect Database Metadata

Gather schema, index, and statistics metadata for analysis.

```sql
-- Check for missing indexes on foreign keys
SELECT
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Check table bloat
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(quote_ident(tablename))) AS total_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(quote_ident(tablename)) DESC
LIMIT 20;

-- Identify slow queries (requires pg_stat_statements)
SELECT
  query,
  calls,
  mean_exec_time,
  total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

```bash
# Save metadata to work directory
mkdir -p /app/results/work
psql "$TARGET_DATABASE_URL" -c "\d+" > /app/results/work/schema_metadata.txt 2>&1
psql "$TARGET_DATABASE_URL" -c "SELECT * FROM pg_indexes WHERE schemaname = 'public';" \
  > /app/results/work/indexes.txt 2>&1
```

## Step 3: Apply Rule Categories (max 3 rounds per category)

Apply checks from each enabled rule category in priority order. For each category, identify violations, record findings, and suggest fixes.

### Priority 1 — Query Performance (CRITICAL, prefix: `query-`)

```sql
-- Check for sequential scans on large tables
SELECT
  schemaname,
  relname,
  seq_scan,
  seq_tup_read,
  idx_scan,
  n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND n_live_tup > 10000
ORDER BY seq_tup_read DESC;

-- Check for missing indexes
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <your_query>;
```

**Key rules:**
- Avoid `SELECT *`; select only needed columns
- Use partial indexes for filtered queries (`WHERE deleted_at IS NULL`)
- Avoid functions on indexed columns in WHERE clauses
- Use `EXPLAIN (ANALYZE, BUFFERS)` to verify index use

### Priority 2 — Connection Management (CRITICAL, prefix: `conn-`)

```sql
-- Check current connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Check for connection limits
SHOW max_connections;
```

**Key rules:**
- Use a connection pooler (PgBouncer or Supabase Pooler) — never connect directly at scale
- Keep transactions short; release connections promptly
- Use `statement_timeout` and `idle_in_transaction_session_timeout`

### Priority 3 — Security & RLS (CRITICAL, prefix: `security-`)

```sql
-- Check which tables have RLS enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- Check existing RLS policies
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public';
```

**Key rules:**
- Enable RLS on all user-facing tables: `ALTER TABLE <t> ENABLE ROW LEVEL SECURITY;`
- Define explicit policies for SELECT, INSERT, UPDATE, DELETE
- Never rely on application-layer filtering alone for multi-tenant data

### Priority 4 — Schema Design (HIGH, prefix: `schema-`)

**Key rules:**
- Use `uuid` or `bigserial` for primary keys; avoid `serial` for new tables
- Normalize where appropriate; denormalize for read-heavy paths with benchmarks
- Use appropriate column types (e.g., `timestamptz` over `timestamp`, `text` over `varchar(n)`)

### Priority 5 — Concurrency & Locking (MEDIUM-HIGH, prefix: `lock-`)

```sql
-- Check for lock contention
SELECT pid, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';
```

**Key rules:**
- Use `SELECT ... FOR UPDATE SKIP LOCKED` for queue patterns
- Avoid long-running transactions that hold locks
- Use advisory locks for application-level mutual exclusion

### Priority 6 — Data Access Patterns (MEDIUM, prefix: `data-`)

**Key rules:**
- Batch inserts/updates; avoid row-by-row loops in application code
- Use `COPY` for bulk loads
- Use materialized views for expensive aggregations refreshed on schedule

### Priority 7 — Monitoring & Diagnostics (LOW-MEDIUM, prefix: `monitor-`)

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Check index usage
SELECT
  indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 20;
```

**Key rules:**
- Enable `pg_stat_statements` and review it regularly
- Set up alerting on `pg_stat_activity` for long-running queries
- Use `auto_explain` for capturing slow query plans

### Priority 8 — Advanced Features (LOW, prefix: `advanced-`)

**Key rules:**
- Use table partitioning for very large tables (>100M rows)
- Use `pg_partman` for automated partition management
- Consider `timescaledb` for time-series workloads on Supabase

## Step 4: Iterate on Errors (max 3 rounds)

If any check from Step 3 returned errors or inconclusive results:

1. Read the specific failure from `/app/results/work/`
2. Apply the targeted fix or re-run the query with adjusted parameters
3. Re-record the result
4. Repeat up to 3 times per category

After 3 rounds, record the unresolved issue in `optimization_report.md` and continue.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `pg_stat_statements` unavailable | `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;` then reconnect |
| Permission denied on `pg_stat_activity` | Grant `pg_monitor` role: `GRANT pg_monitor TO <user>;` |
| EXPLAIN plan shows Seq Scan | Add index; verify with `SET enable_seqscan = off;` to test index path |
| RLS policy blocks query | Check `pg_policies` for the table; ensure policy covers the auth role |
| Lock contention | Identify blocking PID via `pg_stat_activity`; consider query re-ordering |

## Step 5: Write Optimization Report

Write `/app/results/optimization_report.md` with findings across all categories:

```bash
cat > /app/results/optimization_report.md << 'EOF'
# Postgres Optimization Report

## Database
- Target: <database URL (redacted credentials)>
- Schema: <schema>
- Run date: <ISO date>

## Findings by Category

### CRITICAL Findings
...

### HIGH Findings
...

### Summary Table
| Category | Checked | Violations | Fixed |
|----------|---------|------------|-------|
| Query Performance | ... | ... | ... |
...
EOF
```

## Step 6: Write SQL Review

Write `/app/results/sql_review.md` with annotated SQL and suggested rewrites:

```bash
cat > /app/results/sql_review.md << 'EOF'
# SQL Review

## Flagged Queries

### Query 1 — [Description of issue]
**Original:**
```sql
SELECT * FROM users WHERE email = lower($1);
```
**Issue:** Function on column `email` prevents index use.
**Suggested rewrite:**
```sql
CREATE INDEX idx_users_email_lower ON users (lower(email));
SELECT * FROM users WHERE lower(email) = lower($1);
```
EOF
```

## Step 7: Write Executive Summary

Write `/app/results/summary.md` with an overview of the run:

```bash
cat > /app/results/summary.md << 'EOF'
# Supabase Postgres Best Practices — Run Summary

## Overview
- Date: <run date>
- Database: <host (redacted)>
- Schema: <schema>
- Categories applied: <list>
- Dry run: <true|false>

## Findings

| Severity | Count |
|----------|-------|
| CRITICAL | ... |
| HIGH | ... |
| MEDIUM-HIGH | ... |
| MEDIUM | ... |
| LOW-MEDIUM | ... |
| LOW | ... |

## Top Recommendations
1. ...
2. ...
3. ...

## References
- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://wiki.postgresql.org/wiki/Performance_Optimization
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
EOF
```

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/optimization_report.md" \
  "$RESULTS_DIR/sql_review.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `summary.md` exists and includes findings overview and top recommendations
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `optimization_report.md` exists with findings across all 8 categories
- [ ] `sql_review.md` exists with annotated queries and suggested rewrites
- [ ] All CRITICAL violations are documented
- [ ] All rule categories were applied (or documented as skipped with reason)
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it before stopping.**

## Tips

- **Use `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)`** — the `BUFFERS` flag shows cache hits vs disk reads, which is critical for diagnosing I/O-bound queries.
- **Enable `pg_stat_statements` early.** Without it, query-performance rules (Priority 1) are severely limited.
- **RLS policies can silently return empty results.** Always test queries as the actual application role, not a superuser.
- **Connection pool sizing matters.** A common mistake is setting the pool size equal to `max_connections` — instead, target `num_cores * 2` to avoid memory pressure.
- **Partial indexes are underused.** For any query with a common WHERE filter (e.g., `status = 'active'`), a partial index is often a large win.
- **Supabase-specific:** Use the Supabase Dashboard's "Query Performance" advisor tab as a complement to these rules — it surfaces slow queries from `pg_stat_statements` with one-click EXPLAIN.
