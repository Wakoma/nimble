# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import cadquery as cq
import cadscript

def export_svg(part, filename):
    '''
    Export a part to SVG.
    '''

    if isinstance(part, cadscript.Body):
      part = part.cq()

    cq.exporters.export(part,
                        str(filename),
                        opt={
                            "width": 300,
                            "height": 300,
                            "marginLeft": 10,
                            "marginTop": 10,
                            "showAxes": False,
                            "projectionDir": (1, 1, 1),
                            "strokeWidth": 0.8,
                            "strokeColor": (0, 0, 0),
                            "hiddenColor": (0, 0, 255),
                            "showHidden": False,
                        },)

def export_step(part, filename):
    '''
    Export a part as STEP.
    '''

    if isinstance(part, cadscript.Body):
      part = part.cq()

    cq.exporters.export(part, str(filename), exportType="STEP")

  
def export_stl(part, filename):
    '''
    Export a part as STL.
    '''

    if isinstance(part, cadscript.Body):
      part = part.cq()

    cq.exporters.export(part, str(filename), exportType="STL")