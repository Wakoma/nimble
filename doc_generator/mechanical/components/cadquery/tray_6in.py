# SPDX-FileCopyrightText: 2024 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad
from nimble_builder import shelf_builder

# parameters to be set in exsource-def.yaml file

# shelf types
# "stuff"       - for general stuff
# "stuff-thin"  - for general stuff, thin version
# "nuc"         - for Intel NUC
shelf_type = "nuc"
hole_count = 4


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
    raise ValueError(f"Unknown shelf type: {shelf_type}")




result = create_6in_shelf(shelf_type, hole_count)
cad.show(result)  # when run in cq-cli, will return result
