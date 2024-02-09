# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad

beam_width = 20
hole_dia = 4.7
hole_countersink_dia = 10
corner_fillet = 2
rail_width = 5
rail_height = 3
star_width = 9


def create_end_plate(width, depth, height):

    rail_length = width - beam_width - hole_countersink_dia
    rail_offset = (width - beam_width) / 2

    # Make the main body
    plate = cad.make_box(width, depth, height, center="XY")
    plate.fillet("|Z", corner_fillet)

    # add star pattern to save material
    cutout = cad.make_sketch()
    cutout.add_rect(width - 2 * beam_width, depth - 2 * beam_width)
    for i in range(4):
        cutout.cut_rect(star_width, width + depth, angle=(i * 45))
    plate.cut_extrude(">Z", cutout, -height)

    # Add the corner mounting holes with countersinks
    hole_positions = cad.pattern_rect(width - beam_width, depth - beam_width)
    plate.cut_hole(">Z", d=hole_dia, d2=hole_countersink_dia, countersink_angle=90, pos=hole_positions)

    # add "rails" between the holes
    # basic shape with chamfers
    rail = cad.make_box(rail_length, rail_width, height + rail_height, center="XY")
    rail.chamfer(">Z and |Y", rail_height)
    # add 4 instances
    rail.move((0, rail_offset, 0))
    for _ in range(4):
        plate.add(rail)
        rail.rotate("Z", 90)

    return plate


# for debugging purposes
if __name__ == "main":
    result = create_end_plate(155, 155, 3)
    cad.show(result)
