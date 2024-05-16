"""
cq-cli script using cadscript to generate the rack legs of a nimble rack
"""

from math import floor
import cadscript as cad

import nimble_builder


# parameters to be set in exsource-def.yaml file
length = 294.0
long_axis_hole_dia = 4.6
mounting_holes_dia = 3.6


def make_rack_leg(
    length,
    long_axis_hole_dia,
    mounting_holes_dia,
    rack_params=None
    ) -> cad.Body:
    """
    Create the rack legs of given length
    """

    if not rack_params:
        rack_params = nimble_builder.RackParameters()

    # Construct the overall shape
    leg = cad.make_box(rack_params.beam_width, rack_params.beam_width, length)
    leg = leg.fillet("|Z", rack_params.corner_fillet)

    # Long-axis hole for connecting multiple leg sections together
    long_axis_hole = cad.make_sketch()
    long_axis_hole.add_circle(diameter=long_axis_hole_dia)
    leg = leg.cut_extrude(">Z", long_axis_hole, -length)

    # Calculate the count of the holes in the Y direction based on the total length
    number_of_holes = int(floor(length / rack_params.mounting_hole_spacing))

    # Mounting holes
    mount_hole_ptn = cad.pattern_grid(
        count_x=1,
        count_y=number_of_holes,
        spacing_y=rack_params.mounting_hole_spacing
    )
    sketch = cad.make_sketch()
    sketch.add_circle(diameter=mounting_holes_dia, positions=mount_hole_ptn)

    leg.cut_extrude("<Y", sketch, -rack_params.beam_width)
    leg.cut_extrude("<X", sketch, -rack_params.beam_width)

    # move the lower end of the beam to the origin
    leg.move_to_origin("Z")

    return leg

if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    print(f"Creating rack leg with length: {length}")
    result = make_rack_leg(length, long_axis_hole_dia, mounting_holes_dia)
    cad.show(result)  # when run in cq-cli, will return result
