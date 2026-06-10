# Text-to-CAD — Results

## Brief

- **Prompt**: A hexagonal standoff 20 mm tall with a 12 mm across-flats hex body and a concentric 4.2 mm through-hole along its central axis.
- **Parameters**:
  - `HEIGHT_MM = 20.0` — total standoff height along +Z
  - `HEX_ACROSS_FLATS = 12.0` — hex body flat-to-flat distance
  - `HOLE_DIA_MM = 4.2` — concentric through-hole diameter
- **Assumptions**:
  - All dimensions in millimetres; XY base plane, +Z up.
  - Regular hexagon cross-section; circumradius computed as `(6.0) / cos(π/6) ≈ 6.928 mm`.
  - Single closed positive-volume solid (no assembly, no threads).
  - No chamfer or fillet (not specified in prompt).
  - Through-hole is a plain cylindrical bore (not tapped/threaded).

## Artifacts

- STEP: `model.step`  |  STL: `model.stl`  |  GLB: `model.glb`  |  Generator: `model.py`
- Snapshot renderer: **offscreen-mesh** (trimesh + matplotlib; live CAD Viewer render server unavailable)

## Validation

| Check | Result |
|-------|--------|
| STEP generated | PASS |
| STEP re-imports as positive-volume solid | PASS — volume = 2217.065 mm³ |
| Height = 20 mm | PASS — measured 20.000 mm |
| Hex across-flats = 12 mm | PASS — measured 12.000 mm (Y extent) |
| Through-hole diameter = 4.2 mm | PASS — back-calc = 4.200 mm from cylindrical face area |
| Closed positive-volume solid | PASS — 1 solid, volume > 0 |
| Snapshot rendered | PASS — snapshot.png (offscreen-mesh, 37905 bytes) |
| All output files written | PASS |

## Geometry Details

- Bounding box: 13.856 × 12.000 × 20.000 mm (X × Y × Z)
- Face count: 9 (6 hex side faces + 2 end caps + 1 inner cylindrical wall)
- Edge count: 21

## Caveats

- The across-flats is exact on the Y axis (flat faces at ±6 mm); the X extent is `2 × circumradius ≈ 13.856 mm`, which is correct for a regular hexagon.
- No threading or chamfer was modelled; the prompt did not specify these.
- Live `scripts/snapshot` renderer unavailable in headless environment; offscreen trimesh/matplotlib fallback used for `snapshot.png`.
