# SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Literal, Union
import cadscript as cad

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
        sketch.add_rect(self._width, (-panel_thickness, 0), center="X")  # front panel
        sketch.add_rect((self._width / 2 - side_wall_offset, self._inner_width / 2),
                        self._front_depth, center=False)  # part that goes around beam
        sketch.cut_rect((self._width / 2 - beam_width - 0.5, self._width / 2),
                        (0, beam_width + 0.25))  # substract beam with some extra space
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
                  width: Union[Literal["thin", "broad"], float],
                  depth: Union[Literal["standard"], float],
                  sides: Literal["full", "open", "w-pattern", "slots"],
                  back: Literal["full", "open", "w-pattern", "slots"],
                  ) -> None:
        """
        Make the tray of the shelf
        """
        # basic size
        plate_width = 0 if not isinstance(width, (float, int)) else width
        if width == "thin":
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

        # add slots to base plate
        padding_x = 8
        padding_y = 5

        cut_slots(self._shelf, ">Z",
                               plate_width, (self._front_depth, plate_depth),
                               padding_x, padding_y)


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



if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    b = ShelfBuilder(vertical_hole_count=2, width="6inch")
    b.make_front(front_type="w-pattern", bottom_type="closed")
    b.make_tray(width="broad", depth="standard", sides="slots", back="slots")
    cad.show(b._shelf)
