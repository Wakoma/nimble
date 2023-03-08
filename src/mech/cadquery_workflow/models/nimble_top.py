# SPDX-FileCopyrightText: 2023 Jeremy Wright <wrightjmf@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadquery as cq

single_width = 155

width = single_width
height = single_width


def make_end_plate(width, height):
    # Make the main body
    end = cq.Workplane().rect(width, height).extrude(3)
    
    # Add the corner mounting holes
    end = end.faces("<Z").workplane().pushPoints([(width / 2.0 - 10, height / 2.0 - 10), (-width / 2.0 + 10, -height / 2.0 + 10), (width / 2.0 - 10, -height / 2.0 + 10), (-width / 2.0 + 10, height / 2.0 - 10)]).cskHole(4.7, 10.0, 60)

    end = end.faces("<Z").workplane(invert=True).text("W", 48, 3, cut=True)
    return end

top = make_end_plate(width, height)

assy = cq.Assembly()
assy.add(top)

show_object(assy)
