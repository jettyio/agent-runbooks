---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/create-dashboard/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/create-dashboard
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: create-dashboard
  imported_at: '2026-05-03T02:33:17Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: create-dashboard
    confidence: high
secrets: null
---

# create-dashboard - Agent Runbook

## Objective

This runbook converts the `create-dashboard` skill into a repeatable agent workflow for building a custom dashboard. The source skill says: Create a custom web dashboard (React + Vite + Express) inside your sandbox to visualize the agent's Turso database. The dashboard is served on port 3847 and the user sees it live in the "App" tab in Gooseworks. Use when the user asks for a dashboard, visualization, chart, metric view, or any custom UI powered by their agent's data. It preserves the key operating constraints from the skill: work from the runnable dashboard directory, keep one Express process serving API routes and the built React UI, and verify the user can access the finished dashboard. Source context: The **runnable project folder is `/home/user/dashboard`**. That is the ONLY directory you should `cd` into for any npm / build / server command. Most files inside it are symlinks pointing back into the canonical source under the agent's workspace folder (the file you'd see at the canonical path is the same file you'd see through the symlink — it's one file, two paths). The runnable project folder also holds two real local directories that must NO

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Summary of dashboard changes, run commands, server URL, and validation status |
| `/app/results/validation_report.json` | Structured validation results with stages, messages, and `overall_passed` |
| `/app/results/dashboard_build.log` | Captured output from the production dashboard build |
| `/app/results/dashboard_server.log` | Captured output from the dashboard server smoke run |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Output directory for required run artifacts |
| Dashboard directory | `/home/user/dashboard` | Runnable project directory for npm, build, and server commands |
| Dashboard port | `3847` | Port exposed to the Gooseworks App tab |

## Dependencies

| Dependency | Required | Notes |
|---|---|---|
| Node.js and npm | Yes | Used to install dependencies, build the Vite UI, and run the Express server |
| React + Vite project | Yes | Expected at `/home/user/dashboard` |
| Express server | Yes | Serves both API routes and the built React UI from one process |
| Browser or HTTP client | Yes | Used for the final smoke check |
| Source tools observed | Informational | `Express, React, Turso, Vite, express, node, npm, vite` |

## Step 1: Environment Setup

1. Create `/app/results` if it does not already exist.
2. Confirm `/home/user/dashboard` exists before running npm commands.
3. Run `npm install` only from `/home/user/dashboard` if dependencies are missing.
4. Confirm port `3847` is available, or stop the stale process that owns it.

```bash
mkdir -p /app/results
test -d /home/user/dashboard
cd /home/user/dashboard
npm --version
node --version
```

## Step 2: Inspect Dashboard Source

Read the existing dashboard files before editing. Treat `/home/user/dashboard` as the runnable project root even when files are symlinked to a workspace path. Identify available data access helpers, API routes, UI components, and any database schema examples already present in the project.

## Step 3: Implement Dashboard Changes

Build the requested dashboard inside the existing React + Vite + Express app. Keep the Express server as the single serving process, add or update API routes as needed, and keep frontend state handling explicit enough that loading, empty, and error states render clearly. Do not move `node_modules`, `dist`, `.vite`, or cache directories onto the workspace mount.

## Step 4: Build the Dashboard

Run the production build from the dashboard directory and capture the output.

```bash
cd /home/user/dashboard
npm run build > /app/results/dashboard_build.log 2>&1
```

## Step 5: Smoke Test the Server

Start the Express server on port `3847`, capture logs, and verify the app responds. If the project has a dedicated start command, use it; otherwise use the local server entrypoint documented in the project.

```bash
cd /home/user/dashboard
(npm run start > /app/results/dashboard_server.log 2>&1 & echo $! > /tmp/dashboard-server.pid)
sleep 3
curl -fsS http://127.0.0.1:3847/ >/tmp/dashboard-home.html
```

## Step 6: Validate the User Experience

Open the App tab or a browser pointed at `http://127.0.0.1:3847/`. Confirm the page is not blank, the main dashboard data loads, interactive controls work, and the layout is usable at the target viewport. Record the validation outcome in `/app/results/validation_report.json`.

## Step 7: Iterate on Errors (max 3 rounds)

If build, server, or browser validation fails, make the smallest targeted fix and repeat Steps 4-6. Stop after max 3 rounds and write the remaining failure clearly into `summary.md` and `validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Port `3847` already in use | Stop the stale dashboard process and rerun the smoke test |
| Vite build cannot resolve a module | Run `npm install` from `/home/user/dashboard` and verify import paths |
| API returns empty data | Inspect the local database helpers and add defensive empty-state UI |
| App tab is blank | Check browser console, server logs, and built asset paths served by Express |

## Tips

Work from `/home/user/dashboard` for every npm, build, and server command. Keep the final interface focused on the user's requested metrics rather than adding a landing page or explanatory copy.

## Final Checklist

- [ ] Dashboard source was inspected before edits.
- [ ] Build completed and `/app/results/dashboard_build.log` is non-empty.
- [ ] Server smoke test completed and `/app/results/dashboard_server.log` is non-empty.
- [ ] Dashboard responds on port `3847`.
- [ ] `/app/results/summary.md` documents what changed and how to view it.
- [ ] `/app/results/validation_report.json` has `overall_passed` and per-stage results.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/dashboard_build.log" \
  "$RESULTS_DIR/dashboard_server.log"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```
