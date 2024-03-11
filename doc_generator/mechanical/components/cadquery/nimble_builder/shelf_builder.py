# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Literal, Optional, Union
import cadscript as cad
from cadscript.interval import Interval2D, Interval1D


from .helpers import cut_slots, cut_w_pattern



# standard sizes for the shelf
beam_width = 20             # width and depth of the beams that the front panels are attached to
width_6in = 155             # full width (front panel) of the 6 inch nimble rack
width_10in = 254            # full width (front panel) of the 10 inch rack
width_10in_reduced = 250    # front panel width for 10 inch rack, reduced to fit into a 250mm wide printer

# standard distances between the holes in the front panels (6 inch nimble rack)
hole_dist_y = 14

no_slots = False  # speedup for debugging


class ShelfBuilder:
    """
    A class to build a variety of shelf types

    origin lies
        x: center of front panel
        y: back side of front panel (on the bounding box of the rack)
        z: bottom of shelf

    """
    hole_diameter = 3.8         # diameter of the holes in the front panels for rack mounting
    panel_thickness = 4         # thickness of the front panels
    bottom_thickness = 2        # thickness of the lower plate of the shelf
    side_wall_thickness = 2.5   # thickness of the side walls of the shelf
    back_wall_thickness = 2.5   # thickness of the back wall of the shelf
    side_wall_offset = 16       # distance between side walls to the bouding box of the rack

    _shelf: cad.Body
    _vertical_hole_count: int
    _width_type: Literal["6inch", "10inch", "10inch_reduced"]
    _width: float
    _height: float
    _inner_width: float  # inside walls between the beams

    _hole_dist_x: float
    _hole_offset_y: float



    def __init__(self,
                 vertical_hole_count: int,
                 width: Literal["6inch", "10inch", "10inch_reduced"],
                 ) -> None:
        """
        Initialize the shelf builder
        """
        self._vertical_hole_count = vertical_hole_count
        self._width_type = width
        self._width = width_6in if width == "6inch" else width_10in if width == "10inch" else width_10in_reduced
        self.init_values()

    def init_values(self):
        self._height = self._vertical_hole_count * hole_dist_y
        self._hole_dist_x = self._width - beam_width
        self._hole_offset_y = hole_dist_y / 2
        self._inner_width = self._width - 2 * beam_width - 2 * self.side_wall_thickness
        self._front_depth = beam_width + 2.75  # the size of the front panel part in y direction
        self._padding_front = self._front_depth  # the space between the front panel and where slots etc can start at the try bottom

    def make_front(self,
                   front_type: Literal["full", "open", "w-pattern", "slots"],
                   bottom_type: Literal["none", "front-open", "closed"],
                   beam_wall_type: Literal["none", "standard", "ramp"] = "standard"
                   ) -> None:
        """
        Make the front panel of the shelf
        """
        # sketch as viewed from top

        sketch = cad.make_sketch()
        # front panel
        sketch.add_rect(self._width, (-self.panel_thickness, 0), center="X")
        # wall next to the beam
        if beam_wall_type != "none":
            sketch.add_rect((self._inner_width / 2, self._width / 2 - beam_width),
                            self._front_depth, center=False)
        sketch.mirror("X")

        # front panel with holes
        front = cad.make_extrude("XY", sketch, self._height)
        pattern_holes = cad.pattern_rect(self._hole_dist_x, (self._hole_offset_y, self._height - self._hole_offset_y), center="X")
        front.cut_hole("<Y", d=self.hole_diameter, pos=pattern_holes)

        if beam_wall_type == "ramp":
            front.chamfer(">Y and >Z and |X", min(self._height, beam_width))

        self._shelf = front

        # front types

        if front_type == "open":
            self.cut_opening("<Y", self._inner_width, offset_y=0)

        if front_type == "w-pattern":
            padding_x = 0
            padding_y = 6
            cut_w_pattern(self._shelf, "<Y", self._inner_width, (0, self._height), padding_x, padding_y)

        if front_type == "slots":
            padding_x = 1
            padding_y = 5
            if not no_slots:
                cut_slots(self._shelf, "<Y", self._inner_width, (0, self._height), padding_x, padding_y)

        # bottom types: how the lower, horizontal part of the front panel looks like
        if bottom_type == "none":
            # do nothing
            self._front_depth = 0
            self._padding_front *= 0.25  # can be smaller in this case

        if bottom_type == "closed":
            # a full-material base between the 2 rack legs
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(self._inner_width, (-0.1, self._front_depth), center="X")
            bottom = cad.make_extrude("XY", bottom_sketch, self.bottom_thickness)
            self._shelf.add(bottom)
            self._padding_front *= 0.25  # can be smaller in this case

        if bottom_type == "front-open":
            # a base with a cutout on the front side for e.g. cable handling
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(self._inner_width, (self._front_depth - 2, self._front_depth), center="X")
            bottom_sketch.add_polygon([(self._inner_width / 2, 0),
                                       (self._inner_width / 2, self._front_depth),
                                       (self._inner_width / 2 - 5, self._front_depth),
                                       ])
            bottom_sketch.mirror("X")
            bottom = cad.make_extrude("XY", bottom_sketch, self.bottom_thickness)
            self._shelf.add(bottom)

    def make_tray(self,
                  width: Union[Literal["standard", "broad"], float],
                  depth: Union[Literal["standard"], float],
                  sides: Literal["full", "open", "w-pattern", "slots", "ramp"],
                  back: Literal["full", "open", "w-pattern", "slots"],
                  bottom_type: Literal["full", "slots", "slots-large"] = "slots-large",
                  wall_height: Optional[float] = None,
                  padding_front: Optional[float] = None,
                  ) -> None:
        """
        Make the tray of the shelf
        """
        # basic size
        plate_width = 0 if not isinstance(width, (float, int)) else width
        if width == "standard":
            if self._width_type == "6inch":
                plate_width = 115  # could be a bit larger, use this for backwards compatibility
            else:
                plate_width = self._inner_width + 2 * self.side_wall_thickness
        elif width == "broad":
            plate_width = self._width - 2 * self.side_wall_offset
        if not isinstance(plate_width, (float, int)) and plate_width <= 0:
            raise ValueError("Invalid width")
        self.plate_width = plate_width

        plate_depth = 0 if not isinstance(depth, (float, int)) else depth
        if depth == "standard":
            plate_depth = 136
        if not isinstance(plate_depth, float) and plate_depth <= 0:
            raise ValueError("Invalid depth")
        self.plate_depth = plate_depth

        # base plate

        plate_sketch = cad.make_sketch()
        plate_sketch.add_rect(plate_width, (self._front_depth, plate_depth), center="X")
        plate = cad.make_extrude("XY", plate_sketch, self.bottom_thickness)

        if sides in ["open", "ramp"] and back == "open":
            plate.fillet(">Y and |Z", 3)

        self._shelf.add(plate)

        # for broad trays, add walls behind beams
        # for thin trays connect the walls

        if sides != "open" and self._front_depth > 0:
            if plate_width > self._width - 2 * beam_width:
                # broad tray
                left = self._inner_width / 2
                right = plate_width / 2
            else:
                # thin tray
                left = plate_width / 2 - self.side_wall_thickness
                right = self._inner_width / 2

            if abs(left - right) > 0.5:
                extra_sketch = cad.make_sketch()
                extra_sketch.add_rect((left, right),
                                      (beam_width + 0.25, self._front_depth))
                extra_sketch.mirror("X")
                extra_walls = cad.make_extrude("XY", extra_sketch, self._height)
                self._shelf.add(extra_walls)

        # add slots to base plate
        padding_x = 8
        padding_y = 8
        space_at_front = self._padding_front if padding_front is None else padding_front

        if not no_slots:
            if bottom_type in ["slots", "slots-large"]:
                cut_slots(self._shelf, ">Z",
                          plate_width, (space_at_front, plate_depth),
                          padding_x, padding_y,
                          slot_type="large" if bottom_type == "slots-large" else "standard"
                          )

        # add side walls and back wall

        wall_height = self._height if wall_height is None else wall_height
        dim_sides = Interval2D(plate_width / 2 - self.side_wall_thickness, plate_width / 2, self._front_depth, plate_depth)
        dim_back = cad.helpers.get_dimensions_2d([plate_width, (plate_depth - self.back_wall_thickness, plate_depth)], center="X")
        have_walls = False
        wall_sketch = cad.make_sketch()
        if sides not in ["open", "ramp"]:
            wall_sketch.add_rect(dim_sides.tuple_x, dim_sides.tuple_y)
            wall_sketch.mirror("X")
            have_walls = True
        if back != "open":
            wall_sketch.add_rect(dim_back.tuple_x, dim_back.tuple_y)
            have_walls = True


        padding_side = 8
        padding_top = 5
        padding_top_w = 6
        if have_walls:
            walls = cad.make_extrude("XY", wall_sketch, wall_height)
            if sides == "w-pattern":
                cut_w_pattern(walls, ">X", dim_sides.tuple_y, (0, wall_height), padding_side, padding_top_w, cut_depth=self._width + 1)
            if sides == "slots" and not no_slots:
                cut_slots(walls, ">X", dim_sides.tuple_y, (0, wall_height), padding_side, padding_top)
            if back == "w-pattern":
                cut_w_pattern(walls, ">Y", dim_back.tuple_x, (0, wall_height), padding_side, padding_top_w)
            if back == "slots" and not no_slots:
                cut_slots(walls, ">Y", dim_back.tuple_x, (0, wall_height), padding_side, padding_top)

            self._shelf.add(walls)

        if sides == "ramp":
            ramp_width = self._height * 1.5
            ramp_width = min(ramp_width, plate_depth - self._front_depth)
            ramp_sketch = cad.make_sketch()
            ramp_sketch.add_polygon([(self._front_depth, 0),
                                     (self._front_depth + ramp_width, 0),
                                     (self._front_depth, self._height)
                                     ])
            ramp = cad.make_extrude("YZ", ramp_sketch, dim_sides.tuple_x).mirror("X")
            self._shelf.add(ramp)


    def cut_opening(self,
                    face: str,
                    size_x: cad.DimensionDefinitionType,
                    offset_y: float = 0,
                    size_y: Optional[cad.DimensionDefinitionType] = None,
                    depth: float = 999,
                    ) -> None:
        """
        Cut an opening into a plate
        """
        sketch = cad.make_sketch()
        if size_y is not None:
            dim_y = cad.helpers.get_dimension(size_y, center=False)
            dim_y.move(offset_y)
        else:
            dim_y = Interval1D(offset_y, 999)
        sketch.add_rect(size_x, dim_y.tuple, center="X")
        self._shelf.cut_extrude(face, sketch, -depth)

    def add_mounting_hole_to_bottom(self,
                                    x_pos: float,
                                    y_pos: float,
                                    base_thickness: float,
                                    hole_type: Literal["M3cs", "M3-tightfit", "base-only"],
                                    base_diameter: float = 15
                                    ) -> None:
        """
        Add a mounting hole to the shelf
        """
        base = cad.make_cylinder(d=base_diameter, h=base_thickness, center="base")
        base.move((x_pos, y_pos, 0.0))
        self._shelf.add(base)
        if hole_type == "M3cs":
            self._shelf.cut_hole("<Z", d=3.2, countersink_angle=90, d2=6, pos=(x_pos, -y_pos))
        elif hole_type == "M3-tightfit":
            self._shelf.cut_hole("<Z", d=2.9, pos=(x_pos, -y_pos))
        elif hole_type == "base-only":
            pass
        else:
            raise ValueError(f"Unknown hole type: {hole_type}")

    def add_mounting_hole_to_side(self,
                                  y_pos: float,
                                  z_pos: float,
                                  hole_type: Literal["M3-tightfit", "HDD"],
                                  side: Literal["left", "right", "both"],
                                  base_diameter: float = 8,
                                  ) -> None:
        """
        Add a mounting hole to the shelf
        """
        base_sketch = cad.make_sketch()
        base_sketch.add_circle(diameter=base_diameter, pos=(y_pos, z_pos))
        base_sketch.add_rect(base_diameter, (0, z_pos), center="X", pos=(y_pos, 0))
        base = cad.make_extrude("YZ", base_sketch, (self.plate_width / 2 - self.side_wall_thickness, self.plate_width / 2))
        if side == "both":
            base.mirror("X")
        else:
            raise ValueError(f"not yet implemented: {side}")
        self._shelf.add(base)
        if hole_type == "M3-tightfit":
            self._shelf.cut_hole(">X", d=2.9, pos=(y_pos, z_pos))
        elif hole_type == "HDD":
            self._shelf.cut_hole(">X", d=2.72, pos=(y_pos, z_pos))
        else:
            raise ValueError(f"Unknown hole type: {hole_type}")

    def add_mounting_hole_to_back(self,
                                  x_pos: float,
                                  z_pos: float,
                                  hole_type: Literal["M3-tightfit"],
                                  ) -> None:
        """
        Add a mounting hole to the shelf
        """
        base_diameter = 8
        base_sketch = cad.make_sketch()
        base_sketch.add_circle(diameter=base_diameter, pos=(x_pos, z_pos))
        base_sketch.add_rect(base_diameter, (0, z_pos), center="X", pos=(x_pos, 0))
        base = cad.make_extrude("XZ", base_sketch, (-self.plate_depth, -(self.plate_depth - self.back_wall_thickness)))
        self._shelf.add(base)
        if hole_type == "M3-tightfit":
            self._shelf.cut_hole(">Y", d=2.9, pos=(-x_pos, z_pos), depth=self.back_wall_thickness + 1)
        else:
            raise ValueError(f"Unknown hole type: {hole_type}")

    def add_cage(self,
                 inner_width: float,
                 inner_depth: float,
                 height: float = 0,
                 back_cutout_width: float = 0,
                 add_ziptie_channels: bool = True,
                 ):
        wall_thickness = 2.5
        offset_top = 2
        offset_bottom = 2
        channel_width = 5
        guide_width = 8
        guide_radius = 6
        ziptie_pos_y1 = inner_depth * 0.25
        ziptie_pos_y1 = max(ziptie_pos_y1, self._front_depth + channel_width / 2)
        ziptie_pos_y2 = inner_depth * 0.75
        if height == 0:
            height = self._height
        cage_height = height + self.bottom_thickness - offset_top

        # basic cage
        sketch = cad.make_sketch()
        sketch.add_rect(inner_width + wall_thickness * 2, inner_depth + wall_thickness, center="X")
        sketch.cut_rect(inner_width, inner_depth, center="X")
        if back_cutout_width > 0:
            sketch.cut_rect(back_cutout_width, inner_depth + wall_thickness + 1, center="X")
        cage = cad.make_extrude("XY", sketch, cage_height)
        self._shelf.add(cage)


        # cable tie channels

        if not add_ziptie_channels:
            return

        sketch_channel_guide = cad.make_sketch()
        sketch_channel_guide.add_rect(inner_width + guide_radius * 2, guide_width,
                                      pos=[(0, ziptie_pos_y1), (0, ziptie_pos_y2)])
        sketch_channel_guide.cut_rect(inner_width, 999)
        channel_guide = cad.make_extrude_z(sketch_channel_guide, cage_height)
        channel_guide.fillet(">Z and >X and |Y", guide_radius / 2)
        channel_guide.fillet(">Z and <X and |Y", guide_radius / 2)
        self._shelf.add(channel_guide)

        sketch_channels = cad.make_sketch()
        sketch_channels.add_rect(self._width, channel_width,
                                 pos=[(0, ziptie_pos_y1), (0, ziptie_pos_y2)])
        self._shelf.cut(cad.make_extrude_z(sketch_channels, 999))


        # cable tie guides
        sketch_guides = cad.make_sketch()
        sketch_guides.add_slot(r=guide_radius,
                               start=(0, self.bottom_thickness + guide_radius + offset_bottom),
                               end=(0, cage_height - guide_radius))
        sketch_guides.cut_rect((-999, 0), (0, 999))
        sketch_guides.move((inner_width / 2, 0))
        sketch_guides.mirror("X")
        self._shelf.add(cad.make_extrude_y(sketch_guides, guide_width, center=True).move((0, ziptie_pos_y1, 0)))
        self._shelf.add(cad.make_extrude_y(sketch_guides, guide_width, center=True).move((0, ziptie_pos_y2, 0)))




    def get_body(self) -> cad.Body:
        """
        Return the shelf body
        """
        return self._shelf


# for development and debugging
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    b = ShelfBuilder(vertical_hole_count=3, width="10inch")
    b.make_front(front_type="slots", bottom_type="closed")
    b.make_tray(width="standard", depth=80, sides="ramp", back="open")
    cad.show(b._shelf)
