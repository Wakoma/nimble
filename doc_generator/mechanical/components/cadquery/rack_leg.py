import cadquery as cq
import cadscript as cad

length = 294.0
hole_spacing = 14.0
long_axis_hole_dia = 4.6
mounting_holes_dia = 3.6

def make_rack_leg(length=294.0, hole_spacing=14.0, long_axis_hole_dia=4.6, mounting_holes_dia=3.6):
    # Construct the overall shape
    leg = cad.make_box(20, 20, length)
    leg = leg.fillet("|Z", 2.0)

    # Long-axis hole for connecting multiple leg sections together
    long_axis_hole = cad.make_sketch()
    long_axis_hole.add_circle(diameter = long_axis_hole_dia)
    leg = leg.cut_extrude(">Z", long_axis_hole, -length)
    
    # Channel cutouts
    sketch = cad.make_sketch()
    sketch.add_polygon([(-2.5, -1.5), (-5, 1.5), (5, 1.5), (2.5, -1.5)])
    for angle in [0,90,180,270]:
        s = sketch.copy().move([0,10]).rotate(angle)
        leg.cut_extrude("<Z", s, -length)

    # Calculate the count of the holes in the Y direction based on the total length
    number_of_holes = int(length * ((length / hole_spacing) / length))

    # Mounting holes
    mount_hole_ptn = cad.pattern_grid(spacing_x=1.0, spacing_y=hole_spacing, count_x=1, count_y=number_of_holes)
    sketch = cad.make_sketch()
    sketch.add_circle(diameter=mounting_holes_dia, positions = mount_hole_ptn)

    leg.cut_extrude("<Y", sketch, -20.0)
    leg.cut_extrude("<X", sketch, -20.0)

    return leg

# Handle different execution environments, including ExSource-Tools
if "show_object" in globals() or __name__ == "__cqgi__":
    # CQGI should execute this whenever called
    leg = make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia)
    show_object(leg.cq())
