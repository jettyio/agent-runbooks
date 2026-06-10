# Text-to-CAD — Results

## Brief
- **Prompt**: A 40 x 40 x 10 mm aluminum mounting bracket. Add four M4 clearance holes (4.5 mm diameter) positioned 8 mm in from each corner, and a 3 mm fillet on the four vertical outer edges.
- **Parameters**:
  - WIDTH = 40.0 mm
  - DEPTH = 40.0 mm
  - HEIGHT = 10.0 mm
  - HOLE_DIA = 4.5 mm (M4 clearance)
  - HOLE_INSET = 8.0 mm (from each corner edge)
  - VERT_FILLET_R = 3.0 mm (on four vertical outer edges)
- **Assumptions**:
  - All dimensions in millimetres
  - Coordinate datum: XY base plane, +Z up; part centred at origin
  - "Vertical outer edges" = the four edges parallel to Z running at the plate corners
  - Through-holes only (no counterbore/countersink — not specified)
  - Single solid, no assembly hierarchy

## Artifacts
- STEP: model.step  |  STL: model.stl  |  GLB: model.glb  |  Generator: model.py
- Snapshot renderer: offscreen-mesh (trimesh + matplotlib; skill render server not present in headless runtime)

## Validation
| Check | Result |
|-------|--------|
| STEP generated and re-imports | PASS |
| Bounding box 40 × 40 × 10 mm | PASS (40.000 × 40.000 × 10.000 mm) |
| Closed positive-volume solid | PASS (volume = 15 286.571 mm³, 1 solid) |
| Four through-holes present | PASS (face count 14 indicates 4 cylindrical through-holes + top/bottom + 4 filleted vertical faces) |
| 3 mm fillets on vertical edges | PASS (4 vertical fillet faces visible in face topology) |
| Snapshot rendered | PASS (offscreen mesh render, 76 KB) |

## Caveats
- The `scripts/snapshot` render server was not available in the headless runtime; a static offscreen matplotlib render was used instead.
- Volume figure (15 286.6 mm³) is for reference only — not a spec constraint.
