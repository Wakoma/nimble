import cadquery as cq
import models.cadquery.cadscript as cad

length = 294
hole_spacing = 14
long_axis_hole_dia = 4.6
mounting_holes_dia = 3.6

def make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia):
    # Construct the overall shape
    beam = cad.makeBox(20, 20, length)
    beam = beam.fillet("|Z", 2.0)

    # Long-axis hole for connecting multiple leg sections together
    long_axis_hole = cad.makeSketch()
    long_axis_hole.addCircle(long_axis_hole_dia / 2.0)
    beam = beam.cutExtrude(">Z", long_axis_hole, -length)
    
    # Channel cutouts
    sketch = cad.makeSketch()
    sketch.addPolygon([(-2.5, -1.5), (-5, 1.5), (5, 1.5), (2.5, -1.5)])
    for angle in [0,90,180,270]:
        s = sketch.copy().move([0,10]).rotate(angle)
        beam.cutExtrude("<Z", s, -length)

    # Mounting holes
    mount_hole_ptn = cad.PatternRectArray(1, 14.0, 1, 21)
    sketch = cad.makeSketch()
    sketch.addCircle(mounting_holes_dia / 2.0, positions = mount_hole_ptn)

    beam.cutExtrude("<Y", sketch, -20.0)
    beam.cutExtrude("<X", sketch, -20.0)

    return beam

# Handle different execution environments, including ExSource-Tools

if "show_object" in globals() or __name__ == "__cqgi__":
    # CQGI should execute this whenever called
    beam = make_beam(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia)
    show_object(beam.cq())