# SPDX-FileCopyrightText: 2023 Jeremy Wright <wrightjmf@gmail.com>
# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad

width = 100
depth = 100
height = 3
beam_width = 20
countersink_from_top = 1


def create(width, depth, height, countersink_from_top):
    # Make the main body
    plate = cad.make_box(width, depth, height, center="XY")

    # Add the corner mounting holes with countersinks
    hole_positions = cad.pattern_rect(width - beam_width, depth - beam_width)
    face = ">Z" if countersink_from_top else "<Z"
    plate.cut_hole(face, d=4.7, d2=10, countersink_angle=90, pos=hole_positions)

    return plate



result = create(width, depth, height, countersink_from_top)
cad.show(result)

