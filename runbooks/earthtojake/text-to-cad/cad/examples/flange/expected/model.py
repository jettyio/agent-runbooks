"""
Parametric build123d generator for a round mounting flange.

Prompt: A round mounting flange: 60 mm outer diameter, 8 mm thick, with a
25 mm diameter central bore and six 5.5 mm bolt holes evenly spaced on a
46 mm bolt circle.
"""

from build123d import (
    BuildPart, BuildSketch, Circle, Cylinder, Hole, PolarLocations, Part,
    Mode, Align, Axis
)
import math

# --- Named Parameters ---
OUTER_DIAMETER_MM   = 60.0   # flange outer diameter
THICKNESS_MM        =  8.0   # flange axial thickness
BORE_DIAMETER_MM    = 25.0   # central through-bore diameter
BOLT_HOLE_DIA_MM    =  5.5   # bolt hole clearance diameter
BOLT_HOLE_COUNT     =  6     # number of bolt holes
BOLT_CIRCLE_DIA_MM  = 46.0   # bolt hole PCD (bolt circle diameter)


def gen_step() -> Part:
    """Return the mounting flange as a single closed solid Part."""
    with BuildPart() as flange:
        # 1. Main disc body
        Cylinder(
            radius=OUTER_DIAMETER_MM / 2,
            height=THICKNESS_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # 2. Central bore (subtract)
        Cylinder(
            radius=BORE_DIAMETER_MM / 2,
            height=THICKNESS_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
        # 3. Bolt holes — evenly spaced on the bolt circle
        with PolarLocations(
            radius=BOLT_CIRCLE_DIA_MM / 2,
            count=BOLT_HOLE_COUNT,
        ):
            Cylinder(
                radius=BOLT_HOLE_DIA_MM / 2,
                height=THICKNESS_MM,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    return flange.part


if __name__ == "__main__":
    part = gen_step()
    print(f"Flange volume: {part.volume:.1f} mm³")
    bb = part.bounding_box()
    print(f"Bounding box size: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
