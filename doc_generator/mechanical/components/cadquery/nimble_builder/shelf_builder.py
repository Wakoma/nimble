# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Literal, Optional, Union
import cadscript as cad
from cadscript.interval import Interval2D

from helpers import cut_slots, cut_w_pattern


hole_diameter = 3.8         # diameter of the holes in the front panels for rack mounting
panel_thickness = 4         # thickness of the front panels
bottom_thickness = 2        # thickness of the lower plate of the shelf
beam_width = 20             # width and depth of the beams that the front panels are attached to
side_wall_thickness = 3.5   # thickness of the side walls of the shelf
side_wall_offset = 16       # distance between side walls to the bouding box of the rack

# standard sizes for the shelf
width_6in = 155
width_10in = 254
width_10in_reduced = 250

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

    _shelf: cad.Body
    _vertical_hole_count: int
    _width_type: Literal["6inch", "10inch", "10inch_reduced"]
    _width: float
    _height: float
    _inner_width: float

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
        self._height = self._vertical_hole_count * hole_dist_y
        self._hole_dist_x = self._width - beam_width
        self._hole_offset_y = hole_dist_y / 2
        self._inner_width = self._width - 2 * beam_width - 2 * side_wall_thickness
        self._front_depth = beam_width + 2.75  # the size of the front panel part in y direction

    def make_front(self,
                   front_type: Literal["full", "open", "w-pattern", "slots"],
                   bottom_type: Literal["none", "front-open", "closed"]) -> None:
        """
        Make the front panel of the shelf
        """
        # sketch as viewed from top

        sketch = cad.make_sketch()
        # front panel
        sketch.add_rect(self._width, (-panel_thickness, 0), center="X")
        # wall next to the beam
        sketch.add_rect((self._inner_width / 2, self._width / 2 - beam_width - 0.5),
                        self._front_depth, center=False)
        sketch.mirror("X")

        # front panel with holes
        front = cad.make_extrude("XY", sketch, self._height)
        pattern_holes = cad.pattern_rect(self._hole_dist_x, (self._hole_offset_y, self._height - self._hole_offset_y), center="X")
        front.cut_hole("<Y", d=hole_diameter, pos=pattern_holes)

        self._shelf = front

        # front types

        if front_type == "open":
            self.cut_opening("<Y", self._inner_width, offset_y=0)

        if front_type == "w-pattern":
            padding_x = 0
            padding_y = 4
            cut_w_pattern(self._shelf, "<Y", self._inner_width, (0, self._height), padding_x, padding_y)

        if front_type == "slots":
            padding_x = 1
            padding_y = 5
            if not no_slots:
                cut_slots(self._shelf, "<Y", self._inner_width, (0, self._height), padding_x, padding_y)

        # bottom types: how the lower, horizontal part of the front panel looks like
        if bottom_type == "none":
            # nothing
            pass

        if bottom_type == "closed":
            # a full-material base between the 2 rack legs
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(self._inner_width, (-0.1, self._front_depth), center="X")
            bottom = cad.make_extrude("XY", bottom_sketch, bottom_thickness)
            self._shelf.add(bottom)

        if bottom_type == "front-open":
            # a base with a cutout on the front side for e.g. cable handling
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(self._inner_width, (self._front_depth - 2, self._front_depth), center="X")
            bottom_sketch.add_polygon([(self._inner_width / 2, 0),
                                       (self._inner_width / 2, self._front_depth),
                                       (self._inner_width / 2 - 5, self._front_depth),
                                       ])
            bottom_sketch.mirror("X")
            bottom = cad.make_extrude("XY", bottom_sketch, bottom_thickness)
            self._shelf.add(bottom)

    def make_tray(self,
                  width: Union[Literal["standard", "broad"], float],
                  depth: Union[Literal["standard"], float],
                  sides: Literal["full", "open", "w-pattern", "slots", "ramp"],
                  back: Literal["full", "open", "w-pattern", "slots"],
                  wall_height: Optional[float] = None,
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
                plate_width = self._inner_width + 2 * side_wall_thickness
        elif width == "broad":
            plate_width = self._width - 2 * side_wall_offset
        if not isinstance(plate_width, (float, int)) and plate_width <= 0:
            raise ValueError("Invalid width")

        plate_depth = 0 if not isinstance(depth, (float, int)) else depth
        if depth == "standard":
            plate_depth = 136
        if not isinstance(plate_depth, float) and plate_depth <= 0:
            raise ValueError("Invalid depth")

        # base plate

        plate_sketch = cad.make_sketch()
        plate_sketch.add_rect(plate_width, (self._front_depth, plate_depth), center="X")
        plate = cad.make_extrude("XY", plate_sketch, bottom_thickness)
        self._shelf.add(plate)

        # for broad trays, add walls behind beams
        # for thin trays connect the walls

        if plate_width > self._width - 2 * beam_width:
            # broad tray
            left = self._inner_width / 2
            right = plate_width / 2
        else:
            # thin tray
            left = plate_width / 2 - side_wall_thickness
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
        padding_y = 5

        if not no_slots:
            cut_slots(self._shelf, ">Z",
                      plate_width, (self._front_depth, plate_depth),
                      padding_x, padding_y)

        # add side walls and back wall

        wall_height = self._height if wall_height is None else wall_height
        dim_sides = Interval2D(plate_width / 2 - side_wall_thickness, plate_width / 2, self._front_depth, plate_depth)
        dim_back = cad.helpers.get_dimensions_2d([plate_width, (plate_depth - side_wall_thickness, plate_depth)], center="X")
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
        if have_walls:
            walls = cad.make_extrude("XY", wall_sketch, wall_height)
            if sides == "w-pattern":
                cut_w_pattern(walls, ">X", dim_sides.tuple_y, (0, wall_height), padding_side, padding_top, cut_depth=self._width + 1)
            if sides == "slots" and not no_slots:
                cut_slots(walls, ">X", dim_sides.tuple_y, (0, wall_height), padding_side, padding_top)
            if back == "w-pattern":
                cut_w_pattern(walls, ">Y", dim_back.tuple_x, (0, wall_height), padding_side, padding_top)
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
                    offset_y: float = 0
                    ) -> None:
        """
        Cut an opening into a plate
        """
        sketch = cad.make_sketch()
        sketch.add_rect(size_x, (offset_y, 999), center="X")
        self._shelf.cut_extrude(face, sketch, -999)



# for development and debugging
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    b = ShelfBuilder(vertical_hole_count=3, width="10inch")
    b.make_front(front_type="slots", bottom_type="closed")
    b.make_tray(width="standard", depth=80, sides="ramp", back="open")
    cad.show(b._shelf)
