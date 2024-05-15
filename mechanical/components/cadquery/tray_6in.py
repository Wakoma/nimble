# SPDX-FileCopyrightText: 2024 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import typing
import cadscript as cad
import nimble_builder
from nimble_builder import shelf_builder

# parameters to be set in exsource-def.yaml file

# shelf types
# "generic"                 - a generic cable tie shelf
# "stuff"                   - for general stuff such as wires. No access to the front
# "stuff-thin"              - a thin version of above
# "nuc"                     - for Intel NUC
# "usw-flex"                - for Ubiquiti USW-Flex
# "usw-flex-mini"           - for Ubiquiti Flex Mini
# "anker-powerport5"        - for Anker PowerPort 5
# "anker-a2123"             - for Anker 360 Charger 60W (a2123)
# "anker-atom3slim"         - for Anker PowerPort Atom III Slim (AK-194644090180)
# "hdd35"                   - for 3.5" HDD
# "dual-ssd"                - for 2x 2.5" SSD
# "raspi"                   - for Raspberry Pi

shelf_type = "generic"
height_in_u = 2

def get_builder(height_in_u, rack_params=None) -> shelf_builder.ShelfBuilder:
    if not rack_params:
        rack_params = nimble_builder.RackParameters()
    shelf = shelf_builder.ShelfBuilder(height_in_u, rack_params=rack_params)
    return shelf


def create_6in_shelf(shelf_type, height_in_u) -> cad.Body:
    if shelf_type == "generic":
        return create_ziptie_shelf(height_in_u)
    if shelf_type == "stuff":
        b = get_builder(height_in_u)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="broad", depth="standard", sides="w-pattern", back="open")
        return b.get_body()
    if shelf_type == "stuff-thin":
        b = get_builder(height_in_u)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="standard", depth="standard", sides="w-pattern", back="open")
        return b.get_body()
    if shelf_type == "nuc":
        b = get_builder(height_in_u)
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", b._inner_width, 4)
        b.make_tray(width="broad", depth="standard", sides="w-pattern", back="open")
        b.add_mounting_hole_to_bottom(x_pos=0, y_pos=35, base_thickness=4, hole_type="M3cs")
        b.add_mounting_hole_to_bottom(x_pos=0, y_pos=120, base_thickness=4, hole_type="M3cs")
        return b.get_body()
    if shelf_type == "usw-flex":
        b = get_builder(height_in_u)
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
        b = get_builder(height_in_u)
        b.side_wall_thickness = 3.8  # extra thick to have thinner tray
        b.make_front(front_type="full", bottom_type="closed")
        b.cut_opening("<Y", 85, offset_y=5, size_y=19)
        b.make_tray(width="standard", depth=73.4, sides="slots", back="slots")
        b.cut_opening(">Y", 30, offset_y=b.bottom_thickness, depth=10)
        b.add_mounting_hole_to_side(y_pos=59, z_pos=b._height / 2, hole_type="M3-tightfit", side="both")
        b.add_mounting_hole_to_back(x_pos=-75 / 2, z_pos=b._height / 2, hole_type="M3-tightfit")
        b.add_mounting_hole_to_back(x_pos=+75 / 2, z_pos=b._height / 2, hole_type="M3-tightfit")
        return b.get_body()
    if shelf_type == "anker-powerport5":
        return create_ziptie_shelf(height_in_u,
                                   internal_width=56,
                                   internal_depth=90.8,
                                   internal_height=25,
                                   front_cutout_width=53)

    if shelf_type == "anker-atom3slim":
        return create_ziptie_shelf(height_in_u,
                                   internal_width=86.5,
                                   internal_depth=90,
                                   internal_height=20,
                                   front_cutout_width=71)
    if shelf_type == "anker-a2123":
        # 99 x 70 x 26 mm
        # use height = 25, max for cage on 2 hole shelf
        return create_ziptie_shelf(height_in_u,
                                   internal_width=70,
                                   internal_depth=99,
                                   internal_height=25,
                                   front_cutout_width=65)
    if shelf_type == "hdd35":
        width = 102.8  # 101.6 + 1.2 clearance
        screw_pos1 = 77.3  # distance from front
        screw_pos2 = screw_pos1 + 41.61
        screw_y = 7  # distance from bottom plane
        b = get_builder(height_in_u)
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
        b = get_builder(height_in_u)
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
        b = get_builder(height_in_u)
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


def create_ziptie_shelf(
        height_in_u: int,
        internal_width: typing.Optional[float]=None,
        internal_depth: typing.Optional[float]=None,
        internal_height: typing.Optional[float]=None,
        front_cutout_width: typing.Optional[float]=None,
        rear_cutout_width: typing.Optional[float]=None,
        rack_params: nimble_builder.RackParameters = None
):

    if not rack_params:
        rack_params = nimble_builder.RackParameters()
    if not internal_width:
        internal_width = rack_params.tray_width - 12
    if not internal_depth:
        internal_depth = 115
    if not internal_height:
        internal_height = rack_params.tray_height(height_in_u) - 3
    if not rear_cutout_width:
        front_cutout_width = internal_width - 10
    if not rear_cutout_width:
        rear_cutout_width = internal_width - 20


    b = get_builder(height_in_u)
    b.make_front(front_type="full", bottom_type="closed", beam_wall_type="ramp")
    b.cut_opening("<Y", front_cutout_width, offset_y=b.bottom_thickness)
    b.make_tray(width=internal_width+10, depth=internal_depth+3, sides="open", back="open", bottom_type="full")
    b.add_cage(internal_width, internal_depth, internal_height, rear_cutout_width=internal_width-20)

    return b.get_body()


if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    
    result = create_6in_shelf(shelf_type, height_in_u = 2)
    cad.show(result)  # when run in cq-cli, will return result
