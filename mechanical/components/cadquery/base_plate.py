# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadscript as cad
from nimble_builder.nimble_end_plate import create_end_plate
    

# parameters to be set in exsource-def.yaml file
width = 100
depth = 100
height = 3


def create(width, depth, height):
    # create end plate, turn it over and move it to the correct position
    plate = create_end_plate(width, depth, height)
    plate = plate.rotate("X", 180)
    plate = plate.move((0, 0, height))
    return plate


if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    result = create(width, depth, height)
    cad.show(result)  # when run in cq-cli, will return result
