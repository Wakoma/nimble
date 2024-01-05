# SPDX-FileCopyrightText: 2023 Jeremy Wright <wrightjmf@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadquery as cq
import cadscript

from nimble_end_plate import create as create_end
from rack_leg import make_rack_leg 
import json

single_width = 155

width = single_width
depth = single_width
stack_height = "2x3x4"
total_height = 0

for holes in stack_height.split("x"):
    total_height += int(holes) * 25

# Create parts
bottom = create_end(width, depth)
bottom = bottom.rotateAboutCenter((1, 0, 0), 0)
top = create_end(width, depth)
top = top.rotateAboutCenter((1, 0, 0), 180)
top = top.rotateAboutCenter((0, 0, 1), 180)

# Build the assembly
assy = cq.Assembly()
assy.add(bottom, name="bottom_end")
assy.add(make_rack_leg(total_height), name="leg1", loc=cq.Location((-width / 2.0 + 10, -depth / 2.0 + 10, 3)).cq())
assy.add(make_rack_leg(total_height), name="leg2", loc=cq.Location((width / 2.0 - 10, -depth / 2.0 + 10, 3)).cq())
assy.add(make_rack_leg(total_height), name="leg3", loc=cq.Location((width / 2.0 - 10, depth / 2.0 - 10, 3)).cq())
assy.add(make_rack_leg(total_height), name="leg4", loc=cq.Location((-width / 2.0 + 10, depth / 2.0 - 10, 3)).cq())
assy.add(top, name="top_end", loc=cq.Location((0, 0, total_height + 3)))

assy = assy.toCompound()

show_object(assy)
