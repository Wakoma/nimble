# SPDX-FileCopyrightText: 2024 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This module provides many different nimble shelves created using
the nimble_builder ShelfBuilder.
"""

import cadscript as cad
import nimble_builder
from nimble_builder.shelf_builder import ShelfBuilder, ziptie_shelf

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

shelf_type = "stuff-thin"
height_in_u = 2


def create_6in_shelf(shelf_type, height_in_u) -> cad.Body:
    """
    This is the tip level function called when the script
    is called. It used the shelf-type string to decide
    which of the defined shelf functions to call.
    """

    # Dictionary of with key as shelf type and value as tuple
    # of (function, keyword-arguments)
    shelf_functions = {
        "generic": (generic_shelf, {}),
        "stuff": (stuff_shelf, {}),
        "stuff-thin": (stuff_shelf, {"thin":True}),
        "nuc": (nuc_shelf, {}),
        "usw-flex": (usw_flex_shelf, {}),
        "usw-flex-mini": (usw_flex_mini_shelf, {}),
        "anker-powerport5": (anker_shelf, {
            "internal_width": 56,
            "internal_depth": 90.8,
            "internal_height": 25,
            "front_cutout_width": 53
        }),
        "anker-a2123": (anker_shelf, {
            "internal_width": 86.5,
            "internal_depth": 90,
            "internal_height": 20,
            "front_cutout_width": 71
        }),
        "anker-atom3slim": (anker_shelf, {
            "internal_width": 70,
            "internal_depth": 99,
            #should be 26 high but this height create interference of the shelf
            "internal_height": 25,
            "front_cutout_width": 65
        }),
        "hdd35": (hdd35_shelf, {}),
        "dual-ssd": (dual_ssd_shelf, {}),
        "raspi": (raspi_shelf, {})
    }

    if shelf_type in shelf_functions:
        shelf_func = shelf_functions[shelf_type][0]
        kwargs = shelf_functions[shelf_type][1]
        return shelf_func(height_in_u, **kwargs)
    raise ValueError(f"Unknown shelf type: {shelf_type}")

def generic_shelf(height_in_u) -> cad.Body:
    """
    A generic cable tie shelf
    """
    return ziptie_shelf(height_in_u)

def stuff_shelf(height_in_u, thin=False) -> cad.Body:
    """
    A shelf for general stuff such as wires. No access to the front
    """
    width = "broad" if not thin else "standard"
    builder = ShelfBuilder(
        height_in_u, width=width, depth="standard", front_type="w-pattern"
    )
    builder.make_tray(sides="w-pattern", back="open")
    return builder.get_body()

def nuc_shelf(height_in_u) -> cad.Body:
    """
    A shelf for an Intel NUC
    """
    builder = ShelfBuilder(
        height_in_u, width="broad", depth="standard", front_type="full"
    )
    builder.cut_opening("<Y", builder.inner_width, 4)
    builder.make_tray(sides="w-pattern", back="open")
    builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=35, base_thickness=4, hole_type="M3cs")
    builder.add_mounting_hole_to_bottom(x_pos=0, y_pos=120, base_thickness=4, hole_type="M3cs")
    return builder.get_body()

def usw_flex_shelf(height_in_u) -> cad.Body:
    """
    A shelf for a Ubiquiti USW-Flex
    """
    builder = ShelfBuilder(
        height_in_u, width="standard", depth=119.5, front_type="full"
    )
    builder.cut_opening("<Y", builder.inner_width, 4)
    builder.make_tray(sides="w-pattern", back="open")
    # add 2 mounting bars on the bottom plate
    sketch = cad.make_sketch()
    sketch.add_rect(8, 60, center="X", pos=[(-17.5, 42), (+17.5, 42)])
    base = cad.make_extrude("XY", sketch, builder.rack_params.tray_bottom_thickness)
    sketch.cut_circle(d=3.8, pos=[(-17.5, 30 + 42), (+17.5, 30 + 42)])
    base2 = cad.make_extrude("XY", sketch, 5)
    builder.get_body().add(base).add(base2)
    return builder.get_body()

def usw_flex_mini_shelf(height_in_u) -> cad.Body:
    """
    A shelf for a for Ubiquiti Flex Mini
    """
    rack_params = nimble_builder.RackParameters(tray_side_wall_thickness=3.8)
    builder = ShelfBuilder(
        height_in_u, width="standard", depth=73.4, front_type="full", rack_params=rack_params
    )
    builder.cut_opening("<Y", 85, offset_y=5, size_y=19)
    builder.make_tray(sides="slots", back="slots")
    builder.cut_opening(">Y", 30, offset_y=builder.rack_params.tray_bottom_thickness, depth=10)
    builder.add_mounting_hole_to_side(
        y_pos=59, z_pos=builder.height / 2, hole_type="M3-tightfit", side="both"
    )
    builder.add_mounting_hole_to_back(
        x_pos=-75 / 2, z_pos=builder.height / 2, hole_type="M3-tightfit"
    )
    builder.add_mounting_hole_to_back(
        x_pos=+75 / 2, z_pos=builder.height / 2, hole_type="M3-tightfit"
    )
    return builder.get_body()

def anker_shelf(
    height_in_u,
    internal_width,
    internal_depth,
    internal_height,
    front_cutout_width
    ) -> cad.Body:
    """
    A shelf for an Anker PowerPort 5, Anker 360 Charger 60W (a2123),  or Anker PowerPort Atom
    III Slim (AK-194644090180)
    """
    return ziptie_shelf(
        height_in_u,
        internal_width=internal_width,
        internal_depth=internal_depth,
        internal_height=internal_height,
        front_cutout_width=front_cutout_width
    )

def hdd35_shelf(height_in_u) -> cad.Body:
    """
    A shelf for an 3.5" HDD
    """
    width = 102.8  # 101.6 + 1.2 clearance
    screw_pos1 = 77.3  # distance from front
    screw_pos2 = screw_pos1 + 41.61
    screw_y = 7  # distance from bottom plane
    builder = ShelfBuilder(
        height_in_u, width="standard", depth="standard", front_type="w-pattern"
    )
    builder.make_tray(sides="slots", back="open")
    mount_sketch = cad.make_sketch()
    mount_sketch.add_rect(
        (width / 2, builder.inner_width / 2 + builder.rack_params.tray_side_wall_thickness),
        21,
        pos=[(0, screw_pos1), (0, screw_pos2)],
    )
    mount_sketch.chamfer("<X", (builder.inner_width - width) / 2)
    mount_sketch.mirror("X")
    builder.get_body().add(cad.make_extrude("XY", mount_sketch, 14))
    builder.add_mounting_hole_to_side(
        y_pos=screw_pos1,
        z_pos=screw_y + builder.rack_params.tray_bottom_thickness,
        hole_type="HDD",
        side="both",
    )
    builder.add_mounting_hole_to_side(
        y_pos=screw_pos2,
        z_pos=screw_y + builder.rack_params.tray_bottom_thickness,
        hole_type="HDD",
        side="both",
    )
    return builder.get_body()

def dual_ssd_shelf(height_in_u) -> cad.Body:
    """
    A shelf for atwo 2.5" SSDs
    """
    rack_params = nimble_builder.RackParameters()
    width = 70
    screw_pos1 = 12.5  # distance from front
    screw_pos2 = screw_pos1 + 76
    screw_y1 = 6.6  # distance from bottom plane
    screw_y2 = screw_y1 + 11.1
    builder = ShelfBuilder(
        height_in_u,
        width=width + 2 * rack_params.tray_side_wall_thickness,
        depth=111,
        front_type="w-pattern",
        base_between_beam_walls="none",
        beam_wall_type="none",
    )
    builder.make_tray(sides="slots", back="open")
    for x, y in [
        (screw_pos1, screw_y2),
        (screw_pos2, screw_y2),
        (screw_pos1, screw_y1),
        (screw_pos2, screw_y1),
    ]:
        builder.add_mounting_hole_to_side(
            y_pos=x,
            z_pos=y + rack_params.tray_bottom_thickness,
            hole_type="M3-tightfit",
            side="both",
            base_diameter=11,
        )
    return builder.get_body()

def raspi_shelf(height_in_u) -> cad.Body:
    """
    A shelf for a Raspberry Pi
    """
    screw_dist_x = 49
    screw_dist_y = 58
    dist_to_front = 23.5
    offset_x = -13
    builder = ShelfBuilder(height_in_u, width="standard", depth=111, front_type="full")
    builder.cut_opening("<Y", (-15, 39.5), size_y=(6, 25))
    builder.cut_opening("<Y", (-41.5, -25.5), size_y=(6, 22))
    builder.make_tray(sides="ramp", back="open")
    for x, y in [
        (offset_x, dist_to_front),
        (offset_x + screw_dist_x, dist_to_front),
        (offset_x, dist_to_front + screw_dist_y),
        (offset_x + screw_dist_x, dist_to_front + screw_dist_y),
    ]:
        builder.add_mounting_hole_to_bottom(
            x_pos=x,
            y_pos=y,
            hole_type="base-only",
            base_thickness=builder.rack_params.tray_bottom_thickness,
            base_diameter=20,
        )
        builder.add_mounting_hole_to_bottom(
            x_pos=x, y_pos=y, hole_type="M3-tightfit", base_thickness=5.5, base_diameter=7
        )
    return builder.get_body()


if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    result = create_6in_shelf(shelf_type, height_in_u)
    cad.show(result)  # when run in cq-cli, will return result
