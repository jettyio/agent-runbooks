# Text-to-CAD — Results

## Brief

- **Prompt**: A 40 x 40 x 10 mm aluminum mounting bracket. Add four M4 clearance holes (4.5 mm diameter) positioned 8 mm in from each corner, and a 3 mm fillet on the four vertical outer edges.
- **Parameters**:
  - `PLATE_X = 40.0 mm`
  - `PLATE_Y = 40.0 mm`
  - `PLATE_Z = 10.0 mm`
  - `HOLE_DIAMETER = 4.5 mm` (standard M4 clearance)
  - `HOLE_INSET = 8.0 mm` (distance from plate edge to hole centre)
  - `FILLET_RADIUS = 3.0 mm` (applied to four vertical outer edges)
- **Assumptions**:
  - All dimensions in millimetres; XY base plane with +Z up; part centred at origin.
  - "Vertical outer edges" interpreted as the four corner edges parallel to the Z axis.
  - "8 mm in from each corner" interpreted as 8 mm from each adjacent plate edge to the hole centre, placing holes at (±12, ±12) from centre.
  - Holes are through-holes (full PLATE_Z depth).
  - Material designation (aluminium) is noted but does not affect geometry.

## Artifacts

- **STEP**: model.step | **STL**: model.stl | **GLB**: model.glb | **Generator**: model.py
- **Snapshot renderer**: offscreen mesh render (trimesh + matplotlib Agg backend; live render server not available in headless runtime)

## Validation

| Check | Result |
|-------|--------|
| STEP generated + re-imports | PASS — model.step exported, re-imports with volume = 15 286.571 mm³ |
| Bounding box vs spec (40×40×10 mm) | PASS — 40.0 × 40.0 × 10.0 mm |
| Hole diameter (4.5 mm) | PASS — parameter exact |
| Hole inset (8 mm from each edge) | PASS — parameter exact |
| Fillet radius (3 mm on vertical edges) | PASS — parameter exact |
| Closed positive-volume solid | PASS — 1 solid, volume > 0 |
| Snapshot rendered | PASS — snapshot.png (96 978 bytes, offscreen mesh render) |

## Caveats

- The live `scripts/snapshot` tool requires a running CAD Viewer render server
  which is not available in this headless environment; the offscreen
  trimesh/matplotlib fallback was used instead.
- Hole positions are confirmed at (±12, ±12) mm from plate centre = 8 mm from
  each edge. The prompt says "8 mm in from each corner"; both edges share
  8 mm distance, so holes are at the symmetric 45° diagonal from each corner.
