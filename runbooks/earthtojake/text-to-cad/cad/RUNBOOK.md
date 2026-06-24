---
version: "1.2.0"
evaluation: programmatic
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: text-to-cad
# Eat our own dog food: declare the headline deliverables so Mise surfaces them.
primary_outputs:
  - model.step
  - snapshot.png
origin:
  url: "https://github.com/earthtojake/text-to-cad/blob/main/skills/cad/SKILL.md"
  user_supplied_url: "https://github.com/earthtojake/text-to-cad"
  is_directory_mirror: false
  source_host: "github.com"
  source_title: "CAD generation, inspection, and validation"
  imported_at: "2026-06-10T14:33:57Z"
  imported_by: "skill-to-runbook-converter@1.1.0"
  attribution:
    collection_or_org: "earthtojake"
    source_collection: "text-to-cad"
    skill_name: "cad"
    confidence: "high"
secrets: {}
---

# Text-to-CAD — Agent Runbook

## Objective

Turn a natural-language part description into a **validated, STEP-first
parametric CAD model** using the [`earthtojake/text-to-cad`](https://github.com/earthtojake/text-to-cad)
`cad` skill (build123d + OpenCascade). Author a parametric build123d
generator, export a STEP file (plus STL/GLB mesh sidecars), inspect the
geometry for the facts the prompt calls out, render a static verification
snapshot, and write everything to `{{results_dir}}`. STEP is the primary
artifact; STL/3MF/GLB are secondary exports that branch from it.

The runtime (`snapshot: text-to-cad`) bakes the skill at
`/opt/text-to-cad` with `build123d`, `cadquery-ocp`, and the skill's
`cadpy` runtime already installed — no network install needed.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/model.py` | The parametric build123d generator (defines `gen_step()`), the source of truth for the geometry |
| `{{results_dir}}/model.step` | The primary CAD artifact — a valid STEP solid/assembly exported from `model.py` |
| `{{results_dir}}/model.stl` | STL mesh sidecar exported alongside the STEP |
| `{{results_dir}}/snapshot.png` | A static verification render of the STEP/mesh (see Step 5) |
| `{{results_dir}}/inspect_report.json` | Geometry facts: bounding box, volume, solid count, and the spec dimensions you verified |
| `{{results_dir}}/summary.md` | Executive summary: the brief, parameters chosen, validation results, assumptions/caveats |
| `{{results_dir}}/validation_report.json` | Structured validation with `stages`, `results`, and `overall_passed` |

If you finish your analysis but have not written every file, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all results |
| Prompt | `{{prompt}}` | *(required)* | Natural-language description of the part to model (dimensions, features, intent) |

### Inputs

```yaml
# REPLACE-AT-RUNTIME — orchestrator fills {{prompt}}; {{results_dir}} is auto-substituted by Jetty.
results_dir: /app/results
prompt: <REQUIRED — natural-language CAD spec, e.g. "a 40x40x10mm aluminum mounting bracket with four M4 clearance holes 8mm from each corner and a 5mm fillet on the top edges">
```

If `{{prompt}}` is empty, fail fast in Step 1 with `validation_report.json`
stage `setup` set to `passed=false` and a message naming the missing input.

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `text-to-cad` snapshot | Runtime | Yes | Daytona snapshot with `/opt/text-to-cad`, `build123d`, `cadquery-ocp`, `cadpy` baked in |
| `build123d` / `cadquery-ocp` | Python | Yes (baked) | Parametric CAD kernel (OpenCascade bindings) |
| `cadpy` | Python | Yes (baked) | The skill's STEP/GLB artifact runtime (`scripts/step` imports it) |
| `trimesh`, `matplotlib` | Python | Yes (baked) | Headless fallback render for `snapshot.png` |

No secrets are required — the geometry pipeline is fully local.

---

## Step 1: Environment Setup

```bash
set -e
mkdir -p {{results_dir}}
SKILL=/opt/text-to-cad/skills/cad          # baked skill dir (scripts/step|inspect|snapshot)
WORK={{results_dir}}/work
mkdir -p "$WORK"

# Verify the CAD runtime is present (baked into the text-to-cad snapshot).
python -c "import build123d, cadpy; from build123d import Box; print('build123d', build123d.__version__)" \
  || { echo 'ERROR: CAD runtime missing — is snapshot=text-to-cad?'; exit 1; }
test -f "$SKILL/scripts/step/__main__.py" || { echo "ERROR: cad skill not at $SKILL"; exit 1; }

# Fail fast on an empty prompt.
PROMPT='{{prompt}}'
[ -n "$PROMPT" ] || { echo 'ERROR: prompt is empty'; exit 1; }
```

---

## Step 2: Write a CAD Brief

From `{{prompt}}`, extract into a short brief (record it in `summary.md`):
dimensions + units (default **mm**), coordinate convention (base plane **XY**,
up **+Z**), feature intent (holes, fillets, pockets, bosses, …), the output
geometry kind (single solid vs assembly), and any spec dimensions you will
verify in Step 4. Apply the skill's defaults when unspecified: closed
positive-volume solids; M3/M4/M5 clearance holes = 3.4/4.5/5.5 mm; cosmetic
fillet 1–3 mm; plastic enclosure wall 2–3 mm. State every assumption explicitly.

---

## Step 3: Author the build123d Generator + Export STEP

Write `{{results_dir}}/work/model.py` — a parametric build123d script that
defines **`gen_step()`** returning the part (a build123d `Part`/`Compound`/
`BuildPart` result). Use named parameters at the top, verbose labels, and
closed solids. Then export with the skill's `scripts/step` launcher:

```bash
cd "$WORK"
# Generated Python target -> writes model.step next to it, plus mesh sidecars.
python "$SKILL/scripts/step" model.py -o model.step --stl model.stl --glb model.glb --verbose
test -s model.step || { echo 'ERROR: STEP not generated'; exit 1; }
```

`scripts/step` infers `--kind` from `gen_step()`. Keep `model.py` and
`model.step` in the same directory with the same basename. If generation
fails, fix the **smallest** responsible section of `model.py` and rerun
(see Step 6).

---

## Step 4: Inspect & Validate Geometry

Run the skill's deterministic inspection, then verify the spec dimensions
the brief called out. Persist a machine-readable summary to
`inspect_report.json`.

```bash
cd "$WORK"
python "$SKILL/scripts/inspect" refs model.step --facts --planes --positioning \
  | tee inspect_refs.txt
```

Then compute and record canonical facts directly from the STEP (robust even
if the CLI output format shifts), writing `inspect_report.json`. Always record
spec dimension checks under a `spec_checks` key using the canonical format
`{"ok": bool, "expected_mm": float, "actual_mm": float}` — consistent format
across runs is required for the evaluation harness to parse them.

```bash
python - <<'PY'
import json, pathlib
from build123d import import_step
shape = import_step("model.step")
bb = shape.bounding_box()
solids = shape.solids()
rep = {
    "bounding_box_mm": {
        "min": [round(bb.min.X,3), round(bb.min.Y,3), round(bb.min.Z,3)],
        "max": [round(bb.max.X,3), round(bb.max.Y,3), round(bb.max.Z,3)],
        "size": [round(bb.size.X,3), round(bb.size.Y,3), round(bb.size.Z,3)],
    },
    "solid_count": len(solids),
    "total_volume_mm3": round(sum(s.volume for s in solids), 3),
    "is_closed_positive_volume": all(s.volume > 0 for s in solids) and len(solids) >= 1,
    # Add one entry per named dimension in the prompt brief.
    # Use EXACTLY this layout for every check — the evaluation harness parses it:
    #   spec_checks: { "<label>": { "ok": bool, "expected_mm": float, "actual_mm": float } }
    # Example (replace with actual dimensions from the brief):
    "spec_checks": {
        # "outer_diameter_x_mm": {"ok": abs(round(bb.size.X,3) - EXPECTED) < 0.1,
        #                          "expected_mm": EXPECTED, "actual_mm": round(bb.size.X,3)},
    },
}
pathlib.Path("inspect_report.json").write_text(json.dumps(rep, indent=2))
print(json.dumps(rep, indent=2))
PY
```

Populate `spec_checks` with every dimension the brief names (outer diameter,
height, bore diameter, etc.). Any `"ok": false` entry is a Step 6 repair target.

---

## Step 5: Render a Verification Snapshot (MANDATORY)

A visual snapshot is mandatory after creating geometry. First try the skill's
renderer; if the interactive viewer renderer is unavailable in this headless
runtime, fall back to a deterministic offscreen mesh render — **never skip the
snapshot**.

```bash
cd "$WORK"
# Preferred: the skill's snapshot tool (needs the CAD Viewer render server).
if python "$SKILL/scripts/snapshot" model.step -o snapshot.png 2>snapshot_err.txt && [ -s snapshot.png ]; then
  echo "snapshot via scripts/snapshot"
else
  echo "scripts/snapshot unavailable in headless runtime; using offscreen mesh render"
  python - <<'PY'
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh, numpy as np
m = trimesh.load("model.stl", force="mesh")
fig = plt.figure(figsize=(6,6)); ax = fig.add_subplot(111, projection="3d")
ax.add_collection3d(Poly3DCollection(m.vertices[m.faces], alpha=0.9,
                                     facecolor="#9bb7d4", edgecolor="#33536e", linewidths=0.1))
b = m.bounds; ctr = b.mean(axis=0); r = (b[1]-b[0]).max()/2 * 1.1
for set_lim, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), ctr):
    set_lim(c-r, c+r)
ax.set_box_aspect((1,1,1)); ax.view_init(elev=22, azim=-55); ax.set_axis_off()
fig.savefig("snapshot.png", dpi=130, bbox_inches="tight", pad_inches=0.1)
print("offscreen snapshot.png written")
PY
fi
test -s snapshot.png || { echo 'ERROR: no snapshot.png produced'; exit 1; }
```

Record which renderer produced the snapshot in `summary.md`.

---

## Step 6: Iterate on Errors (max 3 rounds)

If STEP generation failed, a spec dimension didn't match, or the snapshot is
empty/degenerate:

1. Read the specific failure (traceback, bounding-box mismatch, empty render).
2. Change the **smallest** responsible section of `model.py`.
3. Rerun Step 3 (export), then Step 4 (inspect) and Step 5 (snapshot).
4. Repeat up to **3 rounds total**. Keep the best result and flag any
   remaining mismatch honestly in `summary.md`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `gen_step()` not found | The generator MUST define a top-level `gen_step()` returning the part; `scripts/step` calls it |
| STEP exports but volume is 0 / open shell | Ensure closed positive-volume solids; check boolean order and that fillets/chamfers don't over-cut |
| Bounding box wrong vs spec | Parameter/units error — keep all dims in mm; re-check the offending named parameter |
| `scripts/snapshot` errors (no render server) | Expected headless — the offscreen trimesh/matplotlib fallback in Step 5 handles it |
| `import_step` fails on re-read | The STEP is malformed; regenerate from source, don't hand-edit the STEP |

---

## Step 7: Copy Outputs + Write Reports

```bash
cd "$WORK"
cp -f model.py model.step model.stl snapshot.png inspect_report.json {{results_dir}}/ 2>/dev/null || true
# model.glb is optional; copy if present.
[ -s model.glb ] && cp -f model.glb {{results_dir}}/ || true
```

Write `{{results_dir}}/summary.md`:

```markdown
# Text-to-CAD — Results

## Brief
- **Prompt**: {{prompt}}
- **Parameters**: {named params + values}
- **Assumptions**: {units, datum, defaults applied}

## Artifacts
- STEP: model.step  |  STL: model.stl  |  Generator: model.py
- Snapshot renderer: {scripts/snapshot | offscreen-mesh}

## Validation
| Check | Result |
|-------|--------|
| STEP generated + re-imports | ... |
| Bounding box vs spec | ... |
| Closed positive-volume solid(s) | ... |
| Snapshot rendered | ... |

## Caveats
- {anything ambiguous, any spec dimension that couldn't be matched}
```

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.2.0",
  "run_date": "<ISO-8601>",
  "parameters": { "prompt": "{{prompt}}" },
  "stages": [
    { "name": "setup",       "passed": true, "message": "CAD runtime present" },
    { "name": "generate",    "passed": true, "message": "model.step exported from model.py" },
    { "name": "inspect",     "passed": true, "message": "facts computed; spec dims verified" },
    { "name": "snapshot",    "passed": true, "message": "snapshot.png rendered (<renderer>)" },
    { "name": "report",      "passed": true, "message": "all output files written" }
  ],
  "results": { "pass": 0, "partial": 0, "fail": 0 },
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/model.py",
    "{{results_dir}}/model.step",
    "{{results_dir}}/model.stl",
    "{{results_dir}}/snapshot.png",
    "{{results_dir}}/inspect_report.json",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

---

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in \
  "$RESULTS_DIR/model.py" \
  "$RESULTS_DIR/model.step" \
  "$RESULTS_DIR/model.stl" \
  "$RESULTS_DIR/snapshot.png" \
  "$RESULTS_DIR/inspect_report.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then echo "FAIL: $f is missing or empty"; else echo "PASS: $f ($(wc -c < "$f") bytes)"; fi
done
# STEP must re-import cleanly.
python -c "from build123d import import_step; s=import_step('$RESULTS_DIR/model.step'); assert s.volume>0; print('PASS: STEP re-imports, volume=%.1f mm^3' % s.volume)" \
  || echo "FAIL: STEP does not re-import as a positive-volume solid"
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `model.py` defines `gen_step()` and is the source of the geometry
- [ ] `model.step` exists, is non-empty, and re-imports as a positive-volume solid
- [ ] `model.stl` mesh sidecar exported
- [ ] `snapshot.png` rendered (skill renderer or offscreen fallback)
- [ ] `inspect_report.json` has bounding box, volume, solid count; spec dims verified
- [ ] `summary.md` records brief, parameters, assumptions, validation, caveats
- [ ] `validation_report.json` has `stages`, `results`, `overall_passed`
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Changelog

| Version | Change |
|---------|--------|
| 1.2.0 | Standardize `inspect_report.json` spec_checks format: every dimension check now uses `{ok, expected_mm, actual_mm}` for consistent harness parsing. Bumped validation_report version to match. |
| 1.1.0 | Added `primary_outputs` frontmatter; added GLB sidecar export; offscreen-mesh snapshot fallback documented. |
| 1.0.0 | Initial import from `earthtojake/text-to-cad` cad skill. |

---

## Tips

- **STEP is the primary artifact.** Author parametric source (`model.py`),
  never hand-edit the exported STEP. STL/3MF/GLB are secondary sidecars.
- **`gen_step()` is the contract.** `scripts/step` calls it; without a
  top-level `gen_step()` the export is a no-op.
- **Keep everything in millimeters** with the XY base plane / +Z up unless the
  prompt says otherwise — most bounding-box mismatches are a units slip.
- **The snapshot is mandatory but the live `$cad-viewer` handoff is not part
  of headless eval** — render a static `snapshot.png` (skill renderer when the
  CAD Viewer render server is up, offscreen mesh render otherwise).
- **Validate against the spec, not just "it exported."** Check the bounding
  box and the dimensions the prompt named; report any you couldn't match.
