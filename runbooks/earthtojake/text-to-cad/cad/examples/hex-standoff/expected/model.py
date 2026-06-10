"""
Hexagonal standoff — parametric build123d generator.

Brief
-----
Prompt : A hexagonal standoff 20 mm tall with a 12 mm across-flats hex body
         and a concentric 4.2 mm through-hole along its central axis.

Parameters
----------
height_mm        : 20.0   — total height of the standoff along +Z
hex_across_flats : 12.0   — hex body across-flats distance (ISO standard)
hole_dia_mm      :  4.2   — through-hole diameter (concentric with hex axis)

Coordinate convention : XY base plane, +Z up.
All dimensions in millimetres.

Assumptions
-----------
- Single positive-volume closed solid (no assembly).
- Hex cross-section is a regular hexagon with flat-to-flat = 12 mm.
- Through-hole is cylindrical, coaxial, runs full height.
- No threads, no chamfer, no fillet (not specified).
"""

import math
from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Cylinder,
    Mode,
    Part,
    Plane,
    RegularPolygon,
    extrude,
)


# ── Named parameters ────────────────────────────────────────────────────────
HEIGHT_MM        = 20.0   # total standoff height
HEX_ACROSS_FLATS = 12.0   # flat-to-flat distance of hex cross-section
HOLE_DIA_MM      =  4.2   # concentric through-hole diameter


def gen_step() -> Part:
    """Return the standoff as a closed positive-volume build123d Part."""

    # across-flats (apothem) → circumradius: R = apothem / cos(π/6)
    apothem      = HEX_ACROSS_FLATS / 2.0
    circumradius = apothem / math.cos(math.pi / 6)   # ≈ 6.928 mm

    with BuildPart() as part:
        # ── Hex body: extrude regular-hexagon sketch from z=0 to z=HEIGHT_MM
        with BuildSketch(Plane.XY):
            RegularPolygon(radius=circumradius, side_count=6)
        extrude(amount=HEIGHT_MM)

        # ── Concentric through-hole (full height, centered on hex axis)
        # Align.MIN on Z anchors the cylinder at z=0, same datum as the hex body.
        Cylinder(
            radius=HOLE_DIA_MM / 2.0,
            height=HEIGHT_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

    return part.part


if __name__ == "__main__":
    p = gen_step()
    bb = p.bounding_box()
    print(f"gen_step() volume = {p.volume:.3f} mm³")
    print(f"bounding box size  = {bb.size.X:.3f} x {bb.size.Y:.3f} x {bb.size.Z:.3f} mm")
