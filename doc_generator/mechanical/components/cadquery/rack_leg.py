from math import floor
import cadscript as cad

length = 294
hole_spacing = 14
long_axis_hole_dia = 4.6
mounting_holes_dia = 3.6


def make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia):
    # Construct the overall shape
    beam = cad.make_box(20, 20, length)
    beam = beam.fillet("|Z", 2.0)

    # Long-axis hole for connecting multiple leg sections together
    long_axis_hole = cad.make_sketch()
    long_axis_hole.add_circle(diameter=long_axis_hole_dia)
    beam = beam.cut_extrude(">Z", long_axis_hole, -length)

    # Channel cutouts
    sketch = cad.make_sketch()
    sketch.add_polygon([(-2.5, -1.5), (-5, 1.5), (5, 1.5), (2.5, -1.5)])
    for angle in [0, 90, 180, 270]:
        s = sketch.copy().move((0, 10)).rotate(angle)
        beam.cut_extrude("<Z", s, -length)

    # Calculate the count of the holes in the Y direction based on the total length
    number_of_holes = int(floor(length / hole_spacing))

    # Mounting holes
    mount_hole_ptn = cad.pattern_grid(count_x=1, count_y=number_of_holes, spacing_y=hole_spacing)
    sketch = cad.make_sketch()
    sketch.add_circle(diameter=mounting_holes_dia, positions=mount_hole_ptn)

    beam.cut_extrude("<Y", sketch, -20.0)
    beam.cut_extrude("<X", sketch, -20.0)

    # move the lower end of the beam to the origin
    beam = beam.move((0, 0, length / 2))

    return beam


# Handle different execution environments, including ExSource-Tools
if "show_object" in globals() or __name__ == "__cqgi__":
    # CQGI should execute this whenever called
    print("Creating rack leg")
    print("Length: ", length)
    print("Hole spacing: ", hole_spacing)
    beam = make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia)
    show_object(beam.cq())