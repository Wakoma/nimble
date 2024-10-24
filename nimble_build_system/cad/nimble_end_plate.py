
"""
A generic function for the end plates of the rack (top and bottom plates.
This currently only generates the flat plates, not ones that can hold and 
instrument on top.
"""

import cadscript as cad
from nimble_build_system.cad import RackParameters



def create_end_plate(width, depth, height, rack_params=None):
    """
    Create the top and bottom of the rack.
    """

    if not rack_params:
        rack_params = RackParameters()

    rail_length = width - rack_params.beam_width - rack_params.end_plate_hole_countersink_dia
    rail_offset = (width - rack_params.beam_width) / 2

    # Make the main body
    plate = cad.make_box(width, depth, height, center="XY")
    plate.fillet("|Z", rack_params.corner_fillet)

    # add star pattern to save material
    cutout = cad.make_sketch()
    cutout.add_rect(width - 2 * rack_params.beam_width, depth - 2 * rack_params.beam_width)
    for i in range(4):
        cutout.cut_rect(rack_params.end_plate_star_width, width + depth, angle=i*45)
    plate.cut_extrude(">Z", cutout, -height)

    # Add the corner mounting holes with countersinks
    hole_positions = cad.pattern_rect(
        width - rack_params.beam_width,
        depth - rack_params.beam_width
    )
    plate.cut_hole(
        ">Z",
        d=rack_params.end_plate_hole_dia,
        d2=rack_params.end_plate_hole_countersink_dia,
        countersink_angle=90,
        pos=hole_positions
    )

    # add "rails" between the holes
    # basic shape with chamfers
    rail = cad.make_box(
        rail_length,
        rack_params.end_plate_rail_width,
        height + rack_params.end_plate_rail_height,
        center="XY"
    )
    rail.chamfer(">Z and |Y", rack_params.end_plate_rail_height)
    # add 4 instances
    rail.move((0, rail_offset, 0))
    for _ in range(4):
        plate.add(rail)
        rail.rotate("Z", 90)

    return plate


# for debugging purposes
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    result = create_end_plate(155, 155, 3)
    cad.show(result)
