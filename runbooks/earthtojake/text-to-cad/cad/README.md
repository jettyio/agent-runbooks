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
| `snapshot.png` | Verification render |
| `inspect_report.json` | Bounding box, volume, solid count, spec-dimension checks |
| `summary.md`, `validation_report.json` | Process report |

## Example gallery

Three production runs across distinct part families — a four-hole mounting
bracket, a hex standoff, and a bolt-circle flange — each spec-verified
(bounding box and named dimensions checked against the prompt) and rendered.
See `examples/`.
