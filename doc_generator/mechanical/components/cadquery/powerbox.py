# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad


width = 113.5
width_inner = width - 5
height = 115
height_inner = height - 4
depth = 56
depth_inner = depth - 2
nose_width = 13
nose_height = 14
holders_width = 155
holders_side1 = 30
holders_side2 = 34
holders_height = 26
hole_dia = 3.8
beam_width = 20
hole_dist_y = 14
hole_offset = hole_dist_y / 2
v_hole_z1 = 14
v_hole_z2 = 26
v_hole_z3 = 38



def create():
    sketch = cad.make_sketch()
    sketch.add_rect(width, height, center="X")
    sketch.add_rect(nose_width, (height, height + nose_height), center="X")
    sketch_holders = cad.make_sketch()
    sketch_holders.add_rect(holders_width, holders_side1, center="X")
    sketch_holders.add_rect(holders_width, (height - holders_side2, height), center="X")
    sketch_inner = cad.make_sketch()
    sketch_inner.add_rect(width_inner, height_inner, center="X")

    block = cad.make_extrude_z(sketch, depth)
    holders = cad.make_extrude_z(sketch_holders, holders_height)
    holders.chamfer(">Z and |Y", (holders_width - width) / 2)
    block.add(holders)
    block_inner = cad.make_extrude_z(sketch_inner, depth_inner)
    block.cut(block_inner)

    hole_pos_x = (holders_width - beam_width) / 2
    for x in [-hole_pos_x, +hole_pos_x]:
        for y in [0, 1, 6, 7]:
            p = (x, hole_offset + y * hole_dist_y)
            block = block.cut_hole(">Z", d=hole_dia, pos=p)

    for z in [v_hole_z1, v_hole_z2, v_hole_z3]:
        p = (height + nose_height / 2, z)
        block = block.cut_hole(">X", d=hole_dia, pos=p)

    return block


if __name__ == "__cqgi__":
    result = create()
    cad.show(result)  # when run in cq-cli, will return result

if __name__ == "__main__":
    result = create()
    result.export_stl("powerbox.stl")
