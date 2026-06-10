"""
Parametric hexagonal standoff generator.
Prompt: A hexagonal standoff 20 mm tall with a 12 mm across-flats hex body
        and a concentric 4.2 mm through-hole along its central axis.

Parameters (all in mm):
  HEIGHT          : 20.0  - total standoff height
  ACROSS_FLATS    : 12.0  - hex body width across flats (flat-to-flat)
  BORE_DIAMETER   : 4.2   - diameter of the central through-hole

Coordinate convention: XY base plane, +Z up.
Orientation: rotation=30 places a flat face along X and Y axes (flat-on-top).
  bounding_box.X = ACROSS_FLATS
  bounding_box.Y = ACROSS_FLATS / cos(30°) ≈ 13.856 (corner-to-corner)
  bounding_box.Z = HEIGHT
"""
from build123d import (
    BuildPart, BuildSketch, RegularPolygon, Circle, extrude,
    Mode, Axis, Part
)

# Named parameters
HEIGHT        = 20.0   # mm — standoff height
ACROSS_FLATS  = 12.0   # mm — hex across-flats (flat-to-flat)
BORE_DIAMETER  = 4.2   # mm — central through-hole diameter


def gen_step() -> Part:
    """Return the hexagonal standoff as a closed positive-volume solid."""
    inradius = ACROSS_FLATS / 2  # apothem = across_flats / 2

    with BuildPart() as standoff:
        # --- Hex body ---
        with BuildSketch():
            # major_radius=False => radius is the inradius (apothem)
            # rotation=30 => flat faces aligned with X/Y axes
            RegularPolygon(
                radius=inradius,
                side_count=6,
                major_radius=False,
                rotation=30,
            )
        extrude(amount=HEIGHT)

        # --- Central through-hole (subtractive) ---
        with BuildSketch():
            Circle(radius=BORE_DIAMETER / 2)
        extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

    return standoff.part


if __name__ == "__main__":
    part = gen_step()
    bb = part.bounding_box()
    print(f"Height Z  : {bb.size.Z:.3f} mm  (target {HEIGHT})")
    print(f"Width  X  : {bb.size.X:.3f} mm  (target across-flats {ACROSS_FLATS})")
    print(f"Width  Y  : {bb.size.Y:.3f} mm")
    print(f"Volume    : {part.volume:.3f} mm³")
    print(f"Solid cnt : {len(part.solids())}")
