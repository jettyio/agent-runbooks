"""
Parametric build123d generator for a 40x40x10mm aluminum mounting bracket.

Brief:
- 40 x 40 x 10 mm rectangular plate (all dims in mm, XY base plane, +Z up)
- Four M4 clearance holes (4.5 mm diameter) positioned 8 mm in from each corner
- 3 mm fillet on the four vertical (Z-axis-parallel) outer edges
"""

from build123d import (
    BuildPart,
    Box,
    Cylinder,
    Locations,
    Mode,
    Axis,
    Part,
    fillet,
)

# ── Named parameters ─────────────────────────────────────────────────────────
PLATE_X        = 40.0   # mm — plate length (X)
PLATE_Y        = 40.0   # mm — plate width  (Y)
PLATE_Z        = 10.0   # mm — plate height / thickness (Z)
HOLE_DIAMETER  = 4.5    # mm — M4 clearance hole diameter (standard = 4.5 mm)
HOLE_INSET     = 8.0    # mm — distance from each plate edge to hole centre
FILLET_RADIUS  = 3.0    # mm — fillet radius on the four vertical outer edges
# ─────────────────────────────────────────────────────────────────────────────


def gen_step() -> Part:
    """Return the mounting bracket as a closed positive-volume solid."""

    # Hole centres: 8 mm in from each edge → offset from plate centre
    cx = PLATE_X / 2.0 - HOLE_INSET   # = 12 mm
    cy = PLATE_Y / 2.0 - HOLE_INSET   # = 12 mm

    with BuildPart() as part:
        # Base plate, centred on origin
        Box(PLATE_X, PLATE_Y, PLATE_Z)

        # Fillet the four vertical outer edges (parallel to Z)
        vertical_edges = part.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=FILLET_RADIUS)

        # Four through-holes (M4 clearance, 4.5 mm dia), one near each corner
        with Locations(
            ( cx,  cy, 0),
            ( cx, -cy, 0),
            (-cx,  cy, 0),
            (-cx, -cy, 0),
        ):
            Cylinder(
                radius=HOLE_DIAMETER / 2.0,
                height=PLATE_Z,
                mode=Mode.SUBTRACT,
            )

    return part.part


if __name__ == "__main__":
    p = gen_step()
    bb = p.bounding_box()
    print(f"Bounding box: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
    print(f"Volume: {p.volume:.2f} mm³")
