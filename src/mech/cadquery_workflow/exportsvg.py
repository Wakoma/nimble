
import cadquery as cq

def export_svg(part, filename):
  cq.exporters.export(part,
                      filename,
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