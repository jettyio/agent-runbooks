"""
Parametric build123d generator for a 40x40x10mm aluminum mounting bracket.

Features:
  - Rectangular base plate 40 x 40 x 10 mm (XY plane, +Z up)
  - Four M4 clearance holes (4.5 mm dia) 8 mm in from each corner
  - 3 mm fillet on the four vertical outer edges (parallel to Z)
"""

from build123d import (
    BuildPart,
    Box, Cylinder, fillet,
    Location, Locations, Plane, Axis,
    Mode,
)

# ── Named parameters ─────────────────────────────────────────────────────────
WIDTH          = 40.0   # mm, X extent
DEPTH          = 40.0   # mm, Y extent
HEIGHT         = 10.0   # mm, Z extent
HOLE_DIA       = 4.5    # mm, M4 clearance
HOLE_INSET     = 8.0    # mm, in from each corner edge
VERT_FILLET_R  = 3.0    # mm, radius on four vertical outer edges
# ─────────────────────────────────────────────────────────────────────────────


def gen_step():
    """Return the mounting-bracket part as a build123d solid."""

    # Hole centre positions (8 mm in from each corner)
    offset = HOLE_INSET - WIDTH / 2     # -12 mm from centroid → 20-8=12 from centre
    hole_positions = [
        ( offset,  offset),   # front-left
        (-offset,  offset),   # front-right
        ( offset, -offset),   # back-left
        (-offset, -offset),   # back-right
    ]

    with BuildPart() as bp:
        # 1. Base block
        Box(WIDTH, DEPTH, HEIGHT)

        # 2. Four through-holes (bottom → top)
        for x, y in hole_positions:
            with Locations(Location((x, y, 0))):
                Cylinder(
                    radius=HOLE_DIA / 2,
                    height=HEIGHT,
                    mode=Mode.SUBTRACT,
                )

        # 3. Fillet the four vertical outer edges (those parallel to Z-axis)
        vert_edges = bp.edges().filter_by(Axis.Z)
        fillet(vert_edges, radius=VERT_FILLET_R)

    return bp.part


if __name__ == "__main__":
    import sys
    part = gen_step()
    bb = part.bounding_box()
    print(f"Bounding box: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
    print(f"Volume: {part.volume:.2f} mm³")
    print(f"Solids: {len(part.solids())}")
