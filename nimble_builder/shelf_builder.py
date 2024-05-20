

"""
Shelf_builder provides classes and methods for creating any numble shelf, with
very little code.
"""

from typing import Literal, Optional, Union
import cadscript as cad
from cadscript.interval import Interval2D, Interval1D


from nimble_builder.helpers import cut_slots, cut_w_pattern
import nimble_builder


NO_SLOTS = False  # speedup for debugging


class ShelfBuilder:
    """
    A class to build a variety of shelf types.

    On initialising the front of the shelf is made. Class methods can be used to
    add the base the cutouts and mounting.

    origin lies
        x: center of front panel
        y: back side of front panel (on the bounding box of the rack)
        z: bottom of shelf

    """

    _rack_params: nimble_builder.RackParameters
    _shelf: cad.Body
    _height_in_u: int

    def __init__(
        self,
        height_in_u: int,
        width: Union[Literal["standard", "broad"], float],
        depth: Union[Literal["standard"], float],
        front_type: Literal["full", "open", "w-pattern", "slots"],
        base_between_beam_walls: Literal["none", "front-open", "closed"] = "closed",
        beam_wall_type: Literal["none", "standard", "ramp"] = "standard",
        rack_params=None,
    ) -> None:
        """
        Initialize the shelf builder this makes the front of the shelf.
        """
        self._height_in_u = height_in_u
        self._width = width
        self._depth = depth
        self._front_type = front_type
        self._front_type = front_type

        self._beam_wall_type = beam_wall_type
        self._base_between_beam_walls = base_between_beam_walls
        if not rack_params:
            rack_params = nimble_builder.RackParameters()
        self._rack_params = rack_params
        self._make_front()

    @property
    def plate_width(self):
        """
        Derived property which is the width of the main plate (base).
        """
        # basic size

        if self._width == "standard":
            if self._rack_params.nominal_rack_width == "6inch":
                # could be a bit larger, use this for backwards compatibility
                return 115
            return self.inner_width + 2 * self.rack_params.tray_side_wall_thickness

        if self._width == "broad":
            return self._rack_params.rack_width - 2 * self.rack_params.broad_tray_clearance

        if isinstance(self._width, (float, int)) and self._width > 0:
            return self._width

        raise ValueError(f"The value {self._width} is not a valid shelf width")

    @property
    def plate_depth(self):
        """
        Derived property which is the depth of the main plate (base)
        """
        if self._depth == "standard":
            return 136

        if isinstance(self._depth, (float, int)) and self._depth > 0:
            return self._depth
        raise ValueError(f"The value {self._depth} is not a valid shelf depth")

    @property
    def rack_params(self):
        """
        Returns the RackParameters() object that configures the shelf.
        """
        return self._rack_params

    @property
    def height(self):
        """
        Derived property which is the height of the shelf.
        """
        return self._height_in_u * self._rack_params.mounting_hole_spacing

    @property
    def hole_dist_x(self):
        """
        Derived property which is the horizontal separation between the mounting holes.
        """
        return self._rack_params.rack_width - self._rack_params.beam_width

    @property
    def hole_offset_z(self):
        """
        Derived property which is the vertical ditance between the top/bottom of the shelf
        and the mounting hole.
        """
        return self._rack_params.mounting_hole_spacing / 2

    @property
    def inner_width(self):
        """
        The internal width of the tray area.
        """
        return (
            self._rack_params.rack_width
            - 2 * self._rack_params.beam_width
            - 2 * self._rack_params.tray_side_wall_thickness
        )

    @property
    def front_depth(self):
        """
        The length of the beam walls that sit behind front panel.
        """
        return self._rack_params.beam_width + 2.75

    @property
    def front_of_tray(self):
        """
        Front position of the tray.
        """
        if self._base_between_beam_walls == "none":
            return 0
        return self.front_depth

    @property
    def padding_front(self):
        """
        The space between the front panel and where slots etc can start at the tray bottom.
        """
        if self._base_between_beam_walls != "front-open":
            return self.front_depth / 4
        return self.front_depth

    def _make_front(self) -> None:
        """
        Make the front panel of the shelf. This happens on initialization.
        """
        # sketch as viewed from top

        sketch = cad.make_sketch()
        # front panel
        sketch.add_rect(
            self._rack_params.rack_width,
            (-self._rack_params.tray_front_panel_thickness, 0),
            center="X",
        )
        # wall next to the beam
        if self._beam_wall_type != "none":
            sketch.add_rect(
                (
                    self.inner_width / 2,
                    self._rack_params.rack_width / 2 - self._rack_params.beam_width,
                ),
                self.front_depth,
                center=False,
            )
        sketch.mirror("X")

        # front panel with holes
        front = cad.make_extrude("XY", sketch, self.height)
        z_positions = (self.hole_offset_z, self.height - self.hole_offset_z)

        pattern_holes = cad.pattern_rect(self.hole_dist_x, z_positions, center="X")

        front.cut_hole(
            "<Y", d=self._rack_params.mounting_hole_clearance_diameter, pos=pattern_holes
        )

        if self._beam_wall_type == "ramp":
            front.chamfer(">Y and >Z and |X", min(self.height, self._rack_params.beam_width))

        # We now have a solid front panel with short walls behind
        self._shelf = front

        self._pattern_front()
        self._add_base_between_beam_walls()

    def _pattern_front(self) -> None:
        """
        Depending on the "front_type" made cuts to pattern the front
        """

        if self._front_type == "open":
            self.cut_opening("<Y", self.inner_width, offset_y=0)

        if self._front_type == "w-pattern":
            padding_x = 0
            padding_y = 6
            cut_w_pattern(
                self._shelf, "<Y", self.inner_width, (0, self.height), padding_x, padding_y
            )

        if self._front_type == "slots":
            padding_x = 1
            padding_y = 5
            if not NO_SLOTS:
                cut_slots(
                    self._shelf, "<Y", self.inner_width, (0, self.height), padding_x, padding_y
                )

    def _add_base_between_beam_walls(self) -> None:
        if self._base_between_beam_walls == "closed":
            # a full-material base between the 2 rack legs
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(self.inner_width, (-0.1, self.front_depth), center="X")
            bottom = cad.make_extrude("XY", bottom_sketch, self._rack_params.tray_bottom_thickness)
            self._shelf.add(bottom)

        if self._base_between_beam_walls == "front-open":
            # a base with a cutout on the front side for e.g. cable handling
            bottom_sketch = cad.make_sketch()
            bottom_sketch.add_rect(
                self.inner_width, (self.front_depth - 2, self.front_depth), center="X"
            )
            bottom_sketch.add_polygon(
                [
                    (self.inner_width / 2, 0),
                    (self.inner_width / 2, self.front_depth),
                    (self.inner_width / 2 - 5, self.front_depth),
                ]
            )
            bottom_sketch.mirror("X")
            bottom = cad.make_extrude("XY", bottom_sketch, self._rack_params.tray_bottom_thickness)
            self._shelf.add(bottom)

    def make_tray(
        self,
        sides: Literal["full", "open", "w-pattern", "slots", "ramp"],
        back: Literal["full", "open", "w-pattern", "slots"],
        bottom_type: Literal["full", "slots", "slots-large"] = "slots-large",
        wall_height: Optional[float] = None,
    ) -> None:
        """
        Make the tray part of the shelf. This is most of the base (except the area between
        the beam walls) and the walls at the sides and back of the shelf.
        """

        if not wall_height:
            wall_height = self.height

        # create the base plate

        plate_sketch = cad.make_sketch()
        plate_sketch.add_rect(self.plate_width, (self.front_of_tray, self.plate_depth), center="X")
        plate = cad.make_extrude("XY", plate_sketch, self._rack_params.tray_bottom_thickness)

        if sides in ["open", "ramp"] and back == "open":
            plate.fillet(">Y and |Z", 3)

        self._shelf.add(plate)
        self._make_joining_walls(sides)
        self._pattern_tray_base(bottom_type)
        self._tray_walls(sides, back, wall_height)

    def _make_joining_walls(self, sides: Literal["full", "open", "w-pattern", "slots", "ramp"]):
        """
        Make the walls between the front walls and the tray walls. For broad trays,
        these are walls behind beams. For thin trays this connects the walls.
        """

        if sides != "open" and self._base_between_beam_walls != "none":
            if self.plate_width > self._rack_params.rack_width - 2 * self._rack_params.beam_width:
                # broad tray
                left = self.inner_width / 2
                right = self.plate_width / 2
            else:
                # thin tray
                left = self.plate_width / 2 - self._rack_params.tray_side_wall_thickness
                right = self.inner_width / 2

            if abs(left - right) > 0.5:
                extra_sketch = cad.make_sketch()
                extra_sketch.add_rect(
                    (left, right), (self._rack_params.beam_width + 0.25, self.front_of_tray)
                )
                extra_sketch.mirror("X")
                extra_walls = cad.make_extrude("XY", extra_sketch, self.height)
                self._shelf.add(extra_walls)

    def _pattern_tray_base(self, bottom_type: Literal["full", "slots", "slots-large"]):
        # add slots to base plate
        padding_x = 8
        padding_y = 8

        if bottom_type in ["slots", "slots-large"] and not NO_SLOTS:
            cut_slots(
                self._shelf,
                ">Z",
                self.plate_width,
                (self.padding_front, self.plate_depth),
                padding_x,
                padding_y,
                slot_type="large" if bottom_type == "slots-large" else "standard",
            )

    def _tray_walls(
        self,
        sides: Literal["full", "open", "w-pattern", "slots", "ramp"],
        back: Literal["full", "open", "w-pattern", "slots"],
        wall_height: float,
    ):

        dim_sides = Interval2D(
            self.plate_width / 2 - self._rack_params.tray_side_wall_thickness,
            self.plate_width / 2,
            self.front_of_tray,
            self.plate_depth,
        )
        dim_back = cad.helpers.get_dimensions_2d(
            [
                self.plate_width,
                (self.plate_depth - self._rack_params.tray_back_wall_thickness, self.plate_depth),
            ],
            center="X",
        )
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
                cut_w_pattern(
                    walls,
                    ">X",
                    dim_sides.tuple_y,
                    (0, wall_height),
                    padding_side,
                    padding_top_w,
                    cut_depth=self._rack_params.rack_width + 1,
                )
            if sides == "slots" and not NO_SLOTS:
                cut_slots(
                    walls, ">X", dim_sides.tuple_y, (0, wall_height), padding_side, padding_top
                )
            if back == "w-pattern":
                cut_w_pattern(
                    walls, ">Y", dim_back.tuple_x, (0, wall_height), padding_side, padding_top_w
                )
            if back == "slots" and not NO_SLOTS:
                cut_slots(
                    walls, ">Y", dim_back.tuple_x, (0, wall_height), padding_side, padding_top
                )

            self._shelf.add(walls)

        if sides == "ramp":
            ramp_width = self.height * 1.5
            ramp_width = min(ramp_width, self.plate_depth - self.front_of_tray)
            ramp_sketch = cad.make_sketch()
            ramp_sketch.add_polygon(
                [
                    (self.front_of_tray, 0),
                    (self.front_of_tray + ramp_width, 0),
                    (self.front_of_tray, self.height),
                ]
            )
            ramp = cad.make_extrude("YZ", ramp_sketch, dim_sides.tuple_x).mirror("X")
            self._shelf.add(ramp)

    def cut_opening(
        self,
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

    def add_mounting_hole_to_bottom(
        self,
        x_pos: float,
        y_pos: float,
        base_thickness: float,
        hole_type: Literal["M3cs", "M3-tightfit", "base-only"],
        base_diameter: float = 15,
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

    def add_mounting_hole_to_side(
        self,
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
        base = cad.make_extrude(
            "YZ",
            base_sketch,
            (
                self.plate_width / 2 - self._rack_params.tray_side_wall_thickness,
                self.plate_width / 2,
            ),
        )
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

    def add_mounting_hole_to_back(
        self,
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
        base = cad.make_extrude(
            "XZ",
            base_sketch,
            (-self.plate_depth, -(self.plate_depth - self._rack_params.tray_back_wall_thickness)),
        )
        self._shelf.add(base)
        if hole_type == "M3-tightfit":
            self._shelf.cut_hole(
                ">Y",
                d=2.9,
                pos=(-x_pos, z_pos),
                depth=self._rack_params.tray_back_wall_thickness + 1,
            )
        else:
            raise ValueError(f"Unknown hole type: {hole_type}")

    def add_cage(
        self,
        internal_width: float,
        internal_depth: float,
        internal_height: float = 0,
        rear_cutout_width: float = 0,
        add_ziptie_channels: bool = True,
    ):
        """
        Add a cage around shelf. The cage is specified by the internal space.
        The cage adds ziptie channels as default.
        """
        wall_thickness = 2.5
        offset_top = 2

        if internal_height == 0:
            internal_height = self.height
        cage_height = internal_height + self._rack_params.tray_bottom_thickness - offset_top

        # basic cage
        sketch = cad.make_sketch()
        sketch.add_rect(
            internal_width + wall_thickness * 2, internal_depth + wall_thickness, center="X"
        )
        sketch.cut_rect(internal_width, internal_depth, center="X")
        if rear_cutout_width > 0:
            sketch.cut_rect(rear_cutout_width, internal_depth + wall_thickness + 1, center="X")
        cage = cad.make_extrude("XY", sketch, cage_height)
        self._shelf.add(cage)

        if add_ziptie_channels:
            self._cable_tie_channels(internal_width, internal_depth, cage_height)

    def _cable_tie_channels(self, internal_width, internal_depth, cage_height):
        channel_width = 5
        offset_bottom = 2
        guide_width = 8
        guide_radius = 6
        ziptie_pos_y1 = max(internal_depth * 0.25, self.front_of_tray + channel_width / 2)
        ziptie_pos_y2 = internal_depth * 0.75

        sketch_channel_guide = cad.make_sketch()
        sketch_channel_guide.add_rect(
            internal_width + guide_radius * 2,
            guide_width,
            pos=[(0, ziptie_pos_y1), (0, ziptie_pos_y2)],
        )
        sketch_channel_guide.cut_rect(internal_width, 999)
        channel_guide = cad.make_extrude_z(sketch_channel_guide, cage_height)
        channel_guide.fillet(">Z and >X and |Y", guide_radius / 2)
        channel_guide.fillet(">Z and <X and |Y", guide_radius / 2)
        self._shelf.add(channel_guide)

        sketch_channels = cad.make_sketch()
        sketch_channels.add_rect(
            self._rack_params.rack_width,
            channel_width,
            pos=[(0, ziptie_pos_y1), (0, ziptie_pos_y2)],
        )
        self._shelf.cut(cad.make_extrude_z(sketch_channels, 999))

        # cable tie guides
        sketch_guides = cad.make_sketch()
        sketch_guides.add_slot(
            r=guide_radius,
            start=(0, self._rack_params.tray_bottom_thickness + guide_radius + offset_bottom),
            end=(0, cage_height - guide_radius),
        )
        sketch_guides.cut_rect((-999, 0), (0, 999))
        sketch_guides.move((internal_width / 2, 0))
        sketch_guides.mirror("X")
        self._shelf.add(
            cad.make_extrude_y(sketch_guides, guide_width, center=True).move((0, ziptie_pos_y1, 0))
        )
        self._shelf.add(
            cad.make_extrude_y(sketch_guides, guide_width, center=True).move((0, ziptie_pos_y2, 0))
        )

    def get_body(self) -> cad.Body:
        """
        Return the shelf body
        """
        return self._shelf

def ziptie_shelf(
    height_in_u: int,
    internal_width: Optional[float] = None,
    internal_depth: Optional[float] = None,
    internal_height: Optional[float] = None,
    front_cutout_width: Optional[float] = None,
    rear_cutout_width: Optional[float] = None,
    rack_params: nimble_builder.RackParameters = None,
):
    """
    Return a ziptie shelf. The height in units must be set.
    The other sizes are determined from the internal tray dimensions to
    make it simple to create a shelf for a device of known size.
    """
    if not rack_params:
        rack_params = nimble_builder.RackParameters()
    if not internal_width:
        internal_width = rack_params.tray_width - 12
    if not internal_depth:
        internal_depth = 115
    if not internal_height:
        internal_height = rack_params.tray_height(height_in_u) - 3
    if not rear_cutout_width:
        front_cutout_width = internal_width - 10
    if not rear_cutout_width:
        rear_cutout_width = internal_width - 20

    builder = ShelfBuilder(
        height_in_u,
        width=internal_width + 10,
        depth=internal_depth + 3,
        front_type="full",
        beam_wall_type="ramp",
    )
    builder.cut_opening(
        "<Y",front_cutout_width, offset_y=builder.rack_params.tray_bottom_thickness
    )
    builder.make_tray(sides="open", back="open", bottom_type="full")
    builder.add_cage(
        internal_width, internal_depth, internal_height, rear_cutout_width=internal_width - 20
    )

    return builder.get_body()
