# SPDX-FileCopyrightText: 2024 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad
from nimble_builder import shelf_builder

# parameters to be set in exsource-def.yaml file

# shelf types
# "stuff"                   - for general stuff
# "stuff-thin"              - for general stuff, thin version
# "nuc"                     - for Intel NUC
# "usw-flex"                - for Ubiquiti USW-Flex
# "flex-mini"               - for Ubiquiti Flex Mini
# "anker-powerport5"        - for Anker PowerPort 5
# "anker-A2123"             - for Anker 360 Charger 60W
# "hdd35"                   - for 3.5" HDD
shelf_type = "stuff"
hole_count = 2


def get_builder(hole_count) -> shelf_builder.ShelfBuilder:
    shelf = shelf_builder.ShelfBuilder(hole_count, width="6inch")
    return shelf


def create_6in_shelf(shelf_type, hole_count) -> cad.Body:
    if shelf_type == "stuff":
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="broad", depth="standard", sides="w-pattern", back="open")
        return b.get_body()
    if shelf_type == "stuff-thin":
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="standard", depth="standard", sides="w-pattern", back="open")
        return b.get_body()
    if shelf_type == "nuc":
        b = get_builder(hole_count)
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", b._inner_width, 4)
        b.make_tray(width="broad", depth="standard", sides="w-pattern", back="open")
        b.add_mounting_hole_to_bottom(x_pos=0, y_pos=35, base_thickness=4, hole_type="M3cs")
        b.add_mounting_hole_to_bottom(x_pos=0, y_pos=120, base_thickness=4, hole_type="M3cs")
        return b.get_body()
    if shelf_type == "usw-flex":
        b = get_builder(hole_count)
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", b._inner_width, 4)
        b.make_tray(width="standard", depth=119.5, sides="w-pattern", back="open")
        # add 2 mounting bars on the bottom plate
        sketch = cad.make_sketch()
        sketch.add_rect(8, 60, center="X", pos=[(-17.5, 42), (+17.5, 42)])
        base = cad.make_extrude("XY", sketch, b.bottom_thickness)
        sketch.cut_circle(d=3.8, pos=[(-17.5, 30 + 42), (+17.5, 30 + 42)])
        base2 = cad.make_extrude("XY", sketch, 5)
        b.get_body().add(base).add(base2)
        return b.get_body()
    if shelf_type == "flex-mini":
        b = get_builder(hole_count)
        b.side_wall_thickness = 3.8  # extra thick to have thinner tray
        b.init_values()  # re-init to apply the new thickness
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", 85, offset_y=5, size_y=19)
        b.make_tray(width="standard", depth=73.4, sides="slots", back="w-pattern")
        b.add_mounting_hole_to_side(y_pos=59, z_pos=b._height / 2, hole_type="M3-tightfit", side="both")
        b.add_mounting_hole_to_back(x_pos=-75 / 2, z_pos=b._height / 2, hole_type="M3-tightfit")
        b.add_mounting_hole_to_back(x_pos=+75 / 2, z_pos=b._height / 2, hole_type="M3-tightfit")
        return b.get_body()
    if shelf_type == "anker-powerport5":
        width = 60.6
        length = 90.8
        height = 25
        b = get_builder(hole_count)
        b.make_front(front_type="full", bottom_type="closed", beam_wall_type="ramp")
        b.cut_opening("<Y", 53, offset_y=b.bottom_thickness)
        b.make_tray(width=width + 10, depth=length + 3, sides="open", back="open")
        b.add_cage(inner_width=width, inner_depth=length, height=height, back_cutout_width=40)
        return b.get_body()
    if shelf_type == "anker-A2123":
        # 99 x 70 x 26 mm
        width = 70
        length = 99
        height = 25  # max for cage on 2 hole shelf
        b = get_builder(hole_count)
        b.make_front(front_type="full", bottom_type="closed", beam_wall_type="ramp")
        b.cut_opening("<Y", 65, offset_y=b.bottom_thickness)
        b.make_tray(width=width + 10, depth=length + 3, sides="open", back="open")
        b.add_cage(inner_width=width, inner_depth=length, height=height, back_cutout_width=50)
        return b.get_body()
    if shelf_type == "hdd35":
        width = 102.8  # 101.6 + 1.2 clearance
        screw_pos1 = 77.3  # distance from front
        screw_pos2 = screw_pos1 + 41.61
        screw_y = 7  # distance from bottom plane
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="standard", depth="standard", sides="slots", back="open")
        mount_sketch = cad.make_sketch()
        mount_sketch.add_rect((width / 2, b._inner_width / 2 + b.side_wall_thickness), 21,
                              pos=[(0, screw_pos1), (0, screw_pos2)])
        mount_sketch.chamfer("<X", (b._inner_width - width) / 2)
        mount_sketch.mirror("X")
        b.get_body().add(cad.make_extrude("XY", mount_sketch, 14))
        b.add_mounting_hole_to_side(y_pos=screw_pos1, z_pos=screw_y + b.bottom_thickness, hole_type="HDD", side="both")
        b.add_mounting_hole_to_side(y_pos=screw_pos2, z_pos=screw_y + b.bottom_thickness, hole_type="HDD", side="both")
        return b.get_body()

    raise ValueError(f"Unknown shelf type: {shelf_type}")


if __name__ == "__main__":
    # debugging/testing
    # for t in ["stuff", "stuff-thin", "nuc", "usw-flex", "flex-mini", "anker-powerport5", "anker-A2123"]:
    for t in ["hdd35"]:
        print(f"Creating {t} shelf")
        result = create_6in_shelf(t, hole_count)
        result.export_stl(f"shelf_6in_{t}.stl")
else:
    result = create_6in_shelf(shelf_type, hole_count)
    cad.show(result)  # when run in cq-cli, will return result
