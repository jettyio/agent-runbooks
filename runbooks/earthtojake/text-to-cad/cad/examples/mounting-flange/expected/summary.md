# Text-to-CAD — Results

## Brief
- **Prompt**: A round mounting flange: 60 mm outer diameter, 8 mm thick, with a 25 mm diameter central bore and six 5.5 mm bolt holes evenly spaced on a 46 mm bolt circle.
- **Parameters**:
  - `OUTER_DIAMETER` = 60.0 mm
  - `THICKNESS` = 8.0 mm
  - `BORE_DIAMETER` = 25.0 mm
  - `BOLT_HOLE_DIA` = 5.5 mm
  - `BOLT_CIRCLE_DIA` = 46.0 mm
  - `BOLT_COUNT` = 6
- **Assumptions**:
  - All dimensions in millimetres; XY base plane, +Z up
  - Flange centred at origin; Z spans −4 mm to +4 mm (symmetric about XY plane)
  - Bolt holes are through-holes (full depth = 8 mm), no countersink
  - No fillets or chamfers specified; none applied
  - Single closed solid (one boolean body)

## Artifacts
- STEP: model.step  |  STL: model.stl  |  GLB: model.glb  |  Generator: model.py
- Snapshot renderer: offscreen-mesh (trimesh + matplotlib Agg backend)

## Validation
| Check | Result |
|-------|--------|
| STEP generated + re-imports | PASS |
| Bounding box X (outer diameter) | PASS — 60.0 mm (expected 60.0 mm) |
| Bounding box Y (outer diameter) | PASS — 60.0 mm (expected 60.0 mm) |
| Thickness (Z extent) | PASS — 8.0 mm (expected 8.0 mm) |
| Closed positive-volume solid(s) | PASS — volume 17 552.1 mm³, 1 solid |
| Snapshot rendered | PASS — offscreen mesh render (75 338 bytes) |

## Caveats
- The bore diameter (25 mm) and bolt-hole diameter/count (6 × 5.5 mm on 46 mm PCD) are verified by construction in `model.py` but are not directly measurable from the bounding box alone; they are correct by parametric definition.
- No cosmetic fillets were added as the prompt does not specify them.
- The `scripts/snapshot` live render server was not available in this headless runtime; the offscreen mesh render is equivalent for validation purposes.
