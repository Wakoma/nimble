# SPDX-FileCopyrightText: 2024 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad
from nimble_builder import shelf_builder

# parameters to be set in exsource-def.yaml file

# shelf types
# "stuff"       - for general stuff
# "stuff-thin"  - for general stuff, thin version
shelf_type = "stuff"
hole_count = 3


def get_builder(hole_count) -> shelf_builder.ShelfBuilder:
    shelf = shelf_builder.ShelfBuilder(hole_count, width="6inch")
    return shelf


def create_6in_shelf(shelf_type, hole_count) -> cad.Body:
    if shelf_type == "stuff":
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="broad", depth="standard", sides="slots", back="open")
        return b.get_body()
    if shelf_type == "stuff-thin":
        b = get_builder(hole_count)
        b.make_front(front_type="w-pattern", bottom_type="closed")
        b.make_tray(width="standard", depth="standard", sides="slots", back="open")
        return b.get_body()
    raise ValueError(f"Unknown shelf type: {shelf_type}")




result = create_6in_shelf(shelf_type, hole_count)
cad.show(result)  # when run in cq-cli, will return result
