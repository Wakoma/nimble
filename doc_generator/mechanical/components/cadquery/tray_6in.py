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
# "usw-flex-mini"           - for Ubiquiti Flex Mini
# "anker-powerport5"        - for Anker PowerPort 5
# "anker-A2123"             - for Anker 360 Charger 60W
# "hdd35"                   - for 3.5" HDD
# "dual-ssd"                - for 2x 2.5" SSD
# "raspi"                   - for Raspberry Pi
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
    if shelf_type == "usw-flex-mini":
        b = get_builder(hole_count)
        b.side_wall_thickness = 3.8  # extra thick to have thinner tray
        b.init_values()  # re-init to apply the new thickness
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", 85, offset_y=5, size_y=19)
        b.make_tray(width="standard", depth=73.4, sides="slots", back="slots")
        b.cut_opening(">Y", 30, offset_y=b.bottom_thickness, depth=10)
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
    if shelf_type == "dual-ssd":
        width = 70
        screw_pos1 = 12.5  # distance from front
        screw_pos2 = screw_pos1 + 76
        screw_y1 = 6.6  # distance from bottom plane
        screw_y2 = screw_y1 + 11.1
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="none", beam_wall_type="none")
        b.make_tray(width=width + 2 * b.side_wall_thickness, depth=111, sides="slots", back="open")
        for (x, y) in [(screw_pos1, screw_y2),
                       (screw_pos2, screw_y2),
                       (screw_pos1, screw_y1),
                       (screw_pos2, screw_y1)]:
            b.add_mounting_hole_to_side(y_pos=x, z_pos=y + b.bottom_thickness,
                                        hole_type="M3-tightfit", side="both", base_diameter=11)
        return b.get_body()
    if shelf_type == "raspi":
        screw_dist_x = 49
        screw_dist_y = 58
        dist_to_front = 23.5
        offset_x = -13
        b = get_builder(hole_count)
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", (-15, 39.5), size_y=(6, 25))
        b.cut_opening("<Y", (-41.5, -25.5), size_y=(6, 22))
        b.make_tray(width="standard", depth=111, sides="ramp", back="open")
        for (x, y) in [(offset_x, dist_to_front),
                       (offset_x + screw_dist_x, dist_to_front),
                       (offset_x, dist_to_front + screw_dist_y),
                       (offset_x + screw_dist_x, dist_to_front + screw_dist_y)]:
            b.add_mounting_hole_to_bottom(x_pos=x, y_pos=y, hole_type="base-only",
                                          base_thickness=b.bottom_thickness, base_diameter=20)
            b.add_mounting_hole_to_bottom(x_pos=x, y_pos=y, hole_type="M3-tightfit",
                                          base_thickness=5.5, base_diameter=7)
        return b.get_body()

    raise ValueError(f"Unknown shelf type: {shelf_type}")


def create_and_save_all():
    for (t, c) in [
            ("stuff", 3), ("stuff-thin", 3), ("nuc", 3), ("nuc", 4),
            ("usw-flex", 3), ("usw-flex-mini", 2), ("anker-powerport5", 2), ("anker-A2123", 2),
            ("hdd35", 2), ("dual-ssd", 2), ("raspi", 2)]:
        print(f"Creating {t} shelf")
        result = create_6in_shelf(t, c)
        result.export_stl(f"shelf_6in_{c}u_{t}.stl")


if __name__ == "__main__":
    # debugging/testing
    # create_and_save_all()
    create_6in_shelf("raspi", 2).export_stl("out.stl")
else:
    result = create_6in_shelf(shelf_type, hole_count)
    cad.show(result)  # when run in cq-cli, will return result
