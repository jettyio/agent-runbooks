---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/earthtojake/text-to-cad/main/skills/cad/SKILL.md
  user_supplied_url: https://github.com/earthtojake/text-to-cad/blob/main/skills/cad/SKILL.md
  is_directory_mirror: false
  source_host: raw.githubusercontent.com
  source_title: CAD generation, inspection, and validation
  imported_at: '2026-06-10T14:33:57Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: earthtojake
    skill_name: cad
    confidence: high
---

# CAD Generation, Inspection, and Validation — Agent Runbook

## Objective

Create or modify parametric CAD models from natural-language requirements, generate validated STEP/STP artifacts, inspect geometry references, and return checked outputs. STEP is the primary CAD artifact; STL, 3MF, and native GLB are secondary export workflows that branch from a STEP-first process. For assemblies, prefer `cadpy.assembly.AssemblyHelper` with source-level build123d joints, named mating datums, and native labels. There are two entry points: generate from build123d Python source, or import an existing STEP/STP file directly.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `{{results_dir}}/step_artifact.<ext>` | Primary STEP/STP artifact (or updated artifact path) |
| `{{results_dir}}/snapshot.png` | Mandatory snapshot of primary STEP/STP after creation or update |
| `{{results_dir}}/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `{{results_dir}}/summary.md` | Executive summary: CAD brief, validation results, viewer links, caveats |

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all required files |
| CAD specification | `{{cad_spec}}` | *(required)* | Natural-language description of the part or assembly to create or modify |
| Output filename base | `{{output_name}}` | `output` | Basename for generated STEP and sidecar files (no extension) |
| Existing STEP target | `{{existing_step}}` | *(optional)* | Path to an existing STEP/STP file to inspect or modify |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python` | Runtime | Yes | Python interpreter for build123d and CAD scripts |
| `scripts/step` | CAD CLI | Yes | STEP generation, GLB/topology artifacts, mesh sidecars |
| `scripts/inspect` | CAD CLI | Yes | Selector refs, measure, align, frame, diff |
| `scripts/snapshot` | CAD CLI | Yes | PNG/GIF visual review packets — mandatory after STEP creation/update |
| `cadpy.assembly.AssemblyHelper` | Python package | Yes | Assembly construction with build123d joints and mating datums |
| `build123d` | Python package | Yes | Parametric CAD modeling library |
| `$cad-viewer` | Skill | Conditional | Hand off artifact paths for live viewer links; required when installed |
| `$step-parts` | Skill | Conditional | Search for purchasable off-the-shelf component STEP files |

---

## Step 1: Environment Setup

```bash
mkdir -p "{{results_dir}}"
# Verify required CAD scripts are accessible
for s in step inspect snapshot; do
  python scripts/$s --help > /dev/null 2>&1 || echo "WARNING: scripts/$s not found in PATH"
done
```

Confirm `{{cad_spec}}` is non-empty. If it is empty, write `validation_report.json` with `stages[0].passed=false` and message `"cad_spec is required"`, then stop.

---

## Step 2: Classify the Task and Load References

Determine which workflow applies:

| Task type | Description | Key references |
|-----------|-------------|----------------|
| `new_part` | Designing a new part from scratch | `cad-brief.md`, `build123d-modeling.md`, `step-generation.md` |
| `new_assembly` | Multi-part assembly | Same + `positioning.md` |
| `source_modification` | Edit existing build123d generator | `build123d-modeling.md`, `step-generation.md`, `repair-loop.md` |
| `step_inspection` | Inspect/measure an existing STEP/STP | `inspection-and-validation.md` |
| `secondary_export` | STL/3MF/GLB from existing geometry | `supported-exports.md` |
| `snapshot_review` | Snapshot-only visual review | `snapshot-review.md` |

Load only the reference files whose trigger applies. Do **not** load all references preemptively.

---

## Step 3: Write the CAD Brief

Using `references/cad-brief.md`, extract from `{{cad_spec}}` (and any attached images or drawings):

- Dimensions and units (default: millimeters)
- Coordinate convention (default: base plane XY, Z up)
- Feature intent (holes, fillets, bosses, etc.)
- Output paths and basenames
- Explicit assumptions for anything unspecified
- Validation targets (key dimensions to verify)

Apply default assumptions unless the user overrides them:

| Parameter | Default |
|-----------|---------|
| Units | mm |
| Origin | per `references/positioning.md`; center of main part otherwise |
| Base plane | XY |
| Extrusion axis | +Z |
| Output geometry | Closed positive-volume solid |
| STEP structure | One valid solid or labeled assembly compound |
| Enclosure wall | 2.0–3.0 mm |
| Cosmetic fillet | 1.0–3.0 mm |
| M3/M4/M5 clearance holes | 3.4 / 4.5 / 5.5 mm |

Check `$step-parts` for any named off-the-shelf components (servos, connectors, boards) before creating placeholder geometry. Record misses and substitute a documented envelope.

---

## Step 4: Plan the Model

Before writing code, define:

1. Named parameters (dimensions as Python variables)
2. Intent labels for each feature (build123d `label=` arguments)
3. Source and output paths
4. Expected bounding box (approximate)
5. Mating/positioning datums (for assemblies)

---

## Step 5: Author and Run the Generator

```python
# Minimal build123d generator structure
import build123d as b3d
from build123d import *

# --- parameters ---
length_mm = 100.0
width_mm  = 50.0
height_mm = 25.0

# --- geometry ---
part = Box(length_mm, width_mm, height_mm, label="enclosure_body")
# ... features ...

# --- export ---
from cadpy.utils import gen_step
gen_step(part, "{{results_dir}}/{{output_name}}.step")
```

Run via the CAD skill launcher from the workspace directory (not the skill directory):

```bash
python scripts/step {{results_dir}}/{{output_name}}.py --kind part
```

Rules:
- Edit Python source; never edit exported STEP files directly.
- Run `scripts/step` on explicit targets only — not directory-wide.
- Keep STEP output and its Python generator in the same directory with the same basename.

---

## Step 6: Validate Geometry

```bash
# Baseline — facts, planes, positioning
python scripts/inspect refs {{results_dir}}/{{output_name}}.step --facts --planes --positioning

# Targeted checks (run those relevant to the spec)
python scripts/inspect measure {{results_dir}}/{{output_name}}.step --selector "#o1.2" --measurement length
python scripts/inspect align   {{results_dir}}/{{output_name}}.step
python scripts/inspect frame   {{results_dir}}/{{output_name}}.step
```

Verify every dimension and relationship the CAD brief calls out. If a check fails, change the smallest responsible source section and rerun (see Step 7).

---

## Step 7: Iterate on Errors (max 3 rounds)

If any validation check from Step 6 fails:

1. Identify the smallest responsible source section from the error output.
2. Apply a targeted fix from the table below.
3. Re-run the generator (Step 5) and re-run the failed check (Step 6).
4. Repeat up to 3 rounds.

After 3 rounds, if the check still fails: record the failure in `validation_report.json` with `overall_passed=false` and document the unresolved issue in `summary.md`.

### Common Fixes

| Failure | Fix |
|---------|-----|
| Invalid solid / zero volume | Check for open edges; ensure all solids are closed |
| Selector ref not found | Re-run `--facts` to discover current topology labels |
| Dimension mismatch | Correct the relevant named parameter; check unit convention |
| Assembly placement error | Verify `AssemblyHelper` mating datums; see `references/positioning.md` |
| Snapshot fails (no visible geometry) | Check that STEP export completed; verify output path |

---

## Step 8: Snapshot (Mandatory)

After creating or visibly updating any primary STEP/STP part or assembly, ALWAYS run:

```bash
python scripts/snapshot {{results_dir}}/{{output_name}}.step --output {{results_dir}}/snapshot.png
```

Review the snapshot output. The only valid skip cases are documented in `references/snapshot-review.md`; if skipping, report the reason in `summary.md`.

---

## Step 9: Hand Off to CAD Viewer

If `$cad-viewer` is installed:

1. Pass the explicit file path(s) of every created or modified `.step`, `.stp`, `.stl`, `.3mf`, or `.glb` artifact to `$cad-viewer`.
2. `$cad-viewer` must start CAD Viewer if not already running and return live viewer link(s).
3. Include those viewer link(s) in the final response.

If `$cad-viewer` is unavailable or startup fails, report that and rely on CLI inspection output and snapshots instead.

---

## Step 10: Write Output Files

Write `{{results_dir}}/validation_report.json`:

```json
{{
  "version": "1.0.0",
  "run_date": "<ISO-8601>",
  "stages": [
    {"name": "setup",              "passed": true,  "message": "Environment verified"},
    {"name": "classify",           "passed": true,  "message": "Task type: <task_type>"},
    {"name": "cad_brief",          "passed": true,  "message": "Brief extracted, <N> assumptions recorded"},
    {"name": "generation",         "passed": true,  "message": "STEP generated at <path>"},
    {"name": "geometry_validation","passed": true,  "message": "All spec-driven checks passed"},
    {"name": "snapshot",           "passed": true,  "message": "Snapshot written to <path>"},
    {"name": "handoff",            "passed": true,  "message": "Viewer links returned or $cad-viewer unavailable"},
    {"name": "report_generation",  "passed": true,  "message": "All output files written"}
  ],
  "results": {"pass": 0, "partial": 0, "fail": 0},
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/step_artifact.step",
    "{{results_dir}}/snapshot.png",
    "{{results_dir}}/validation_report.json",
    "{{results_dir}}/summary.md"
  ]
}}
```

Write `{{results_dir}}/summary.md`:

```markdown
# CAD Run — Results

## Overview
- **Date**: <run date>
- **Specification**: {{cad_spec}}
- **Task type**: <classified task type>
- **Output artifact**: <path>
- **Viewer links**: <links from $cad-viewer or "unavailable">

## Validation

| Stage | Status | Notes |
|---|---|---|
| Setup | ... | ... |
| Classify | ... | ... |
| CAD Brief | ... | ... |
| Generation | ... | ... |
| Validation | ... | ... |
| Snapshot | ... | ... |
| Handoff | ... | ... |

## Assumptions
- <List all assumptions applied during modeling>

## Issues / Manual Follow-up
- <Any unresolved errors or caveats>

## Final Verification
- <Snapshot or viewer thumbnail, if available>
```

---

## Step 11: Final Checklist (MANDATORY — do not skip)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
# Required files
for f in "$RESULTS_DIR/validation_report.json" "$RESULTS_DIR/summary.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# STEP artifact
STEP=$(ls "$RESULTS_DIR"/*.step "$RESULTS_DIR"/*.stp 2>/dev/null | head -1)
if [ -n "$STEP" ]; then
  echo "PASS: STEP artifact present: $STEP ($(wc -c < "$STEP") bytes)"
else
  echo "FAIL: No STEP/STP artifact found in $RESULTS_DIR"
fi

# Snapshot
SNAP=$(ls "$RESULTS_DIR"/*.png "$RESULTS_DIR"/*.gif 2>/dev/null | head -1)
if [ -n "$SNAP" ]; then
  echo "PASS: Snapshot present: $SNAP"
else
  echo "FAIL: No snapshot PNG/GIF in $RESULTS_DIR (mandatory unless skip is documented)"
fi

# Validation report passes
PASSED=$(python3 -c "import json,sys; d=json.load(open('$RESULTS_DIR/validation_report.json')); print(d.get('overall_passed'))" 2>/dev/null)
echo "Validation overall_passed: $PASSED"
```

### Checklist

- [ ] `validation_report.json` exists and `overall_passed` reflects actual validation results
- [ ] `summary.md` exists and includes assumptions, viewer links (or explains absence), and any caveats
- [ ] A STEP/STP artifact exists in `{{results_dir}}`
- [ ] A snapshot PNG/GIF exists (or skip is documented with reason in `summary.md`)
- [ ] All spec-driven geometry checks passed (or failures are recorded)
- [ ] CAD viewer handoff completed or unavailability reported
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it before finishing.**

---

## Tips

- **STEP is primary; everything else is derived.** Never treat STL/3MF/GLB as a substitute for the validated STEP.
- **Edit source, not artifacts.** When a Python generator exists, always edit and re-run the generator; never hand-edit the exported STEP.
- **Snapshot is mandatory.** `scripts/snapshot` is not optional after creating or visibly updating a primary STEP/STP. Document the skip reason explicitly in `summary.md` if skipping.
- **One clarification question at a time.** Ask only when a missing value makes the model impossible, fit-critical, safety-critical, or compliance-bound. Otherwise proceed with explicit assumptions.
- **Selector refs are artifact-local.** `#o1.2.f1` and similar tokens are not stable across regenerations — always re-run `--facts` after changes.
- **Do not use git diff for large binary artifacts.** Use `scripts/inspect` summaries, source diffs, and topology output to compare CAD artifacts; path-limited `git status` for bookkeeping only.
- **Report only checks that ran.** Never assert a check passed if you didn't execute it.
- **Provenance**: Imported from `https://raw.githubusercontent.com/earthtojake/text-to-cad/main/skills/cad/SKILL.md` via skill-to-runbook-converter v1.1.0.
