# Text-to-CAD

Turn a natural-language part description into a **validated, STEP-first
parametric CAD model** — authored as build123d Python, exported to STEP (plus
STL/GLB), geometrically inspected against the spec, and rendered to a
verification snapshot.

Imported from the [`earthtojake/text-to-cad`](https://github.com/earthtojake/text-to-cad)
`cad` skill (build123d + OpenCascade).

## Runtime

Runs on the **`text-to-cad`** Daytona snapshot, which bakes the skill at
`/opt/text-to-cad` with `build123d`, `cadquery-ocp`, and the skill's `cadpy`
runtime preinstalled — no network install at run time. Build the snapshot with
`mise/scripts/build_text_to_cad_snapshot.py`.

## Input

| Variable | Example |
|----------|---------|
| `prompt` | `A 40×40×10 mm aluminum mounting bracket with four M4 clearance holes 8 mm in from each corner and a 3 mm fillet on the top outer edges.` |

## Outputs

| File | What |
|------|------|
| `model.step` | Primary CAD artifact (STEP solid/assembly) |
| `model.py` | The parametric build123d generator (`gen_step()`) |
| `model.stl` / `model.glb` | Mesh sidecars |
| `snapshot.png` | Verification render (offscreen-mesh in headless runtime) |
| `inspect_report.json` | Bounding box, volume, solid count, spec-dimension checks (`spec_checks` with `ok`/`expected_mm`/`actual_mm`) |
| `summary.md`, `validation_report.json` | Process report |

## Example gallery

Three production runs on v1.2.0 across distinct part families — a bolt-circle
flange, a hex standoff, and a filletted mounting bracket — each spec-verified
(all named dimensions checked against the prompt) and rendered.

| Example | Trajectory | Pass |
|---------|-----------|------|
| [Bolt-circle mounting flange](examples/mounting-flange/) | `79800836` | 5/5 stages |
| [Hex standoff with axial bore](examples/hex-standoff/) | `4bdc06e9` | 5/5 stages |
| [Mounting bracket with fillets](examples/mounting-bracket/) | `47a93b73` | 5/5 stages |

See `examples/` for input prompts, expected outputs, thumbnails, and trajectory provenance.

## Changelog

| Version | Change |
|---------|--------|
| 1.2.0 | Standardized `inspect_report.json` spec_checks format (`ok`/`expected_mm`/`actual_mm`); curated 3-example launch payload with fresh green trajectories. |
| 1.1.0 | Added `primary_outputs` frontmatter; GLB sidecar export; offscreen-mesh snapshot fallback documented. |
| 1.0.0 | Initial import from `earthtojake/text-to-cad` cad skill. |
