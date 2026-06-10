"""
Round mounting flange generator.

Spec:
  - Outer diameter:   60 mm
  - Thickness:         8 mm
  - Central bore:     25 mm diameter
  - Bolt holes:        6 × 5.5 mm diameter, evenly spaced on a 46 mm bolt circle
"""

from build123d import (
    BuildPart, Circle, Cylinder, Hole, PolarLocations,
    Mode, Axis, Part, export_step
)
import math

# ── Parameters (all in mm) ──────────────────────────────────────────────────
OUTER_DIAMETER   = 60.0    # outer flange diameter
THICKNESS        =  8.0    # flange thickness (height)
BORE_DIAMETER    = 25.0    # central through-bore diameter
BOLT_HOLE_DIA    =  5.5    # bolt hole diameter
BOLT_CIRCLE_DIA  = 46.0    # PCD of bolt holes
BOLT_COUNT       =  6      # number of bolt holes


def gen_step() -> Part:
    """Return the completed mounting flange as a build123d Part."""
    with BuildPart() as flange:
        # Main disc
        Cylinder(radius=OUTER_DIAMETER / 2, height=THICKNESS)

        # Central bore (removed)
        Hole(radius=BORE_DIAMETER / 2, depth=THICKNESS)

        # Six bolt holes evenly spaced on the bolt circle
        with PolarLocations(radius=BOLT_CIRCLE_DIA / 2, count=BOLT_COUNT):
            Hole(radius=BOLT_HOLE_DIA / 2, depth=THICKNESS)

    return flange.part


if __name__ == "__main__":
    part = gen_step()
    print(f"Volume: {part.volume:.1f} mm³")
    bb = part.bounding_box()
    print(f"Bounding box: {bb.size.X:.2f} × {bb.size.Y:.2f} × {bb.size.Z:.2f} mm")
