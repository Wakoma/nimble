from math import e, floor
import cadscript as cad

if __name__ == "__cqgi__":
    import nimble_builder
else:
    from . import nimble_builder


# parameters to be set in exsource-def.yaml file
length = 294.0
hole_spacing = 14.0
long_axis_hole_dia = 4.6
mounting_holes_dia = 3.6


def make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia) -> cad.Body:
    # Construct the overall shape
    leg = cad.make_box(nimble_builder.beam_width, nimble_builder.beam_width, length)
    leg = leg.fillet("|Z", nimble_builder.corner_fillet)

    # Long-axis hole for connecting multiple leg sections together
    long_axis_hole = cad.make_sketch()
    long_axis_hole.add_circle(diameter=long_axis_hole_dia)
    leg = leg.cut_extrude(">Z", long_axis_hole, -length)

    # Calculate the count of the holes in the Y direction based on the total length
    number_of_holes = int(floor(length / hole_spacing))

    # Mounting holes
    mount_hole_ptn = cad.pattern_grid(count_x=1, count_y=number_of_holes, spacing_y=hole_spacing)
    sketch = cad.make_sketch()
    sketch.add_circle(diameter=mounting_holes_dia, positions=mount_hole_ptn)

    leg.cut_extrude("<Y", sketch, -nimble_builder.beam_width)
    leg.cut_extrude("<X", sketch, -nimble_builder.beam_width)

    # move the lower end of the beam to the origin
    leg.move_to_origin("Z")

    return leg


if __name__ == "__cqgi__":
    print(f"Creating rack leg with length: {length}, hole spacing: {hole_spacing}")
    result = make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia)
    cad.show(result)  # when run in cq-cli, will return result
