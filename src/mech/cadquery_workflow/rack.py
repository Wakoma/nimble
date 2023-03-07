# Create Part for a Nimble Rack
# Ruslan Krenzler, 2023-03-06
import math

import cadquery as cq


class RackParams:
    def __init__(self):
        # Default length unit is mm.
        self.rack_width = 155
        self.rack_depth = 155
        self.leg_width = 20
        self.height_in_holes = 2
        self.wall_thickness = 4
        self.hole_distance = 14  # Distance between the holes
        self.hole_diameter = 3.6

    @property
    def inner_width(self):
        return self.rack_width - self.wall_thickness * 2

    @property
    def inner_depth(self):
        return self.rack_depth - self.wall_thickness * 2

    @property
    def rack_height(self):
        return self.height_in_holes * self.hole_distance

    @property
    def inner_height(self):
        return self.rack_height - self.wall_thickness

    @staticmethod
    def build_for_inner_dims(width, height, depth):
        p = RackParams()
        p.rack_width = width + 2 * p.wall_thickness
        p.rack_depth = depth + 2 * p.wall_thickness
        # Convert hole into number of holes.
        nh = math.ceil(height / p.hole_distance)
        # The number of holes must be at least two
        p.height_in_holes = max(nh, 2)
        return p


def create_part(params):
    rack = cq.Workplane("XY").box(params.rack_width, params.rack_depth, params.rack_height, centered=False)
    # Cut inner space for some device.
    # rack=rack.faces(">Z").workplane().moveTo(0,0).rect(params.inner_width, params.inner_depth).cutBlind(params.inner_height)# does not work  # current point is the center of the circle, at (0, 0)
    rack = rack.faces(">Z").workplane().moveTo(params.wall_thickness, params.wall_thickness).rect(params.inner_width,
                                                                                                  params.inner_depth,
                                                                                                  centered=False).cutBlind(
        -params.inner_height)

    # rack = cq.Workplane("XY").box(params.rack_width, params.rack_depth, params.rack_height, centered=False)  # current point is the center of the circle, at (0, 0)
    wings = cq.Workplane("XY").moveTo(-params.leg_width, 0).box(params.rack_width + params.leg_width * 2,
                                                                params.wall_thickness, params.rack_height,
                                                                centered=False)
    # Add holes
    wings = wings.faces(">Y").workplane().moveTo(params.leg_width / 2, params.hole_distance / 2).circle(
        params.hole_diameter / 2).cutThruAll()
    wings = wings.faces(">Y").workplane().moveTo(params.leg_width / 2,
                                                 params.rack_height - params.hole_distance / 2).circle(
        params.hole_diameter / 2).cutThruAll()
    wings = wings.faces(">Y").workplane().moveTo(-params.rack_width - params.leg_width / 2,
                                                 params.hole_distance / 2).circle(params.hole_diameter / 2).cutThruAll()
    wings = wings.faces(">Y").workplane().moveTo(-params.rack_width - params.leg_width / 2,
                                                 params.rack_height - params.hole_distance / 2).circle(
        params.hole_diameter / 2).cutThruAll()
    result = rack.union(wings)
    result = result.faces(">Y").workplane().moveTo(-params.rack_width/2, -params.rack_height/2).rect(params.inner_width-params.wall_thickness, params.inner_height-params.wall_thickness).cutThruAll()

    return result


def main():
    # Test rack builder.
    params_1 = RackParams.build_for_inner_dims(width=100, height=20, depth=80)
    part_1 = create_part(params_1)

    params_2 = RackParams.build_for_inner_dims(width=100, height=25, depth=80)
    part_2 = create_part(params_2)

    params_3 = RackParams.build_for_inner_dims(width=100, height=30, depth=80)
    part_3 = create_part(params_3)

    assy = cq.Assembly()
    assy.add(
        part_1,
        loc=cq.Location((0, 0, 0)),
        name="rack 1",
        color=cq.Color("green"),
    )

    assy.add(
        part_2,
        loc=cq.Location((0, 0, params_1.rack_height)),
        name="rack 2",
        color=cq.Color("yellow"),
    )

    assy.add(
        part_3,
        loc=cq.Location((0, 0, params_1.rack_height + params_2.rack_height)),
        name="rack 3",
        color=cq.Color("red"),
    )

    assy.save("racks.step")
    return assy

# Comment the two lines below out if you use cq-editor.
#assy = main()
#show_object(assy)

if __name__ == "__main__":
    main()
