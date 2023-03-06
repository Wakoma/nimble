# SPDX-FileCopyrightText: 2023 Jeremy Wright <wrightjmf@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadquery as cq

box = cq.Workplane().rect(1, 5).extrude(5).faces("<X").workplane(invert=False).center(0, 2).circle(1.0).cutThruAll()

show_object(box)

cq.exporters.export(box,
                    "/home/jwright/Downloads/repos/hackathon/nimble/src/mech/cadquery_workflow/autodoc_integration/autodoc_sample.svg",
                    opt={
                        "width": 300,
                        "height": 300,
                        "marginLeft": 10,
                        "marginTop": 10,
                        "showAxes": False,
                        "projectionDir": (0.5, 0.5, 0.5),
                        "strokeWidth": 0.1,
                        "strokeColor": (0, 0, 0),
                        "hiddenColor": (0, 0, 255),
                        "showHidden": False,
                    },)
