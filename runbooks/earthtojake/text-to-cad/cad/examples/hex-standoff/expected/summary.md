# Text-to-CAD — Results

## Brief
- **Prompt**: A hexagonal standoff 20 mm tall with a 12 mm across-flats hex body and a concentric 4.2 mm through-hole along its central axis.
- **Parameters**:
  - `HEIGHT = 20.0 mm` — total standoff height
  - `ACROSS_FLATS = 12.0 mm` — hex body width across flats (flat-to-flat)
  - `BORE_DIAMETER = 4.2 mm` — central through-hole diameter
- **Assumptions**:
  - Units: millimetres (mm) throughout
  - Coordinate convention: XY base plane, +Z up; part rests on Z=0
  - Hex orientation: `rotation=30` gives flat faces aligned with X/Y axes (flat-on-top/bottom)
  - No chamfers or fillets — the prompt does not specify them
  - Through-hole is a simple cylindrical bore (no threads modelled)
  - `RegularPolygon(major_radius=False)` interprets radius as the inradius (apothem = across_flats / 2)
  - Spec dimensions to verify: height, across-flats, bore diameter

## Artifacts
- STEP: model.step  |  STL: model.stl  |  GLB: model.glb  |  Generator: model.py
- Snapshot renderer: offscreen-mesh (trimesh + matplotlib, headless runtime)

## Validation
| Check | Result |
|-------|--------|
| STEP generated + re-imports | PASS — volume 2217.065 mm³, 1 closed solid |
| Height (Z) = 20 mm | PASS — actual 20.000 mm |
| Across-flats (X) = 12 mm | PASS — actual 12.000 mm |
| Bore diameter = 4.2 mm | PASS — actual 4.200 mm |
| Closed positive-volume solid(s) | PASS — 1 solid, volume > 0 |
| Snapshot rendered | PASS — offscreen-mesh fallback (38 994 bytes) |

## Caveats
- The skill's `scripts/snapshot` render server is not available in this headless runtime; the offscreen trimesh/matplotlib fallback was used instead.
- The hex bounding box in Y is ~13.856 mm (corner-to-corner diagonal), not 12 mm — this is correct geometry; across-flats maps to the X dimension.
