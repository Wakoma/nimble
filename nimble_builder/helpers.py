"""
A number of helper functions for CadQuery used to simplify the creation of nimble
rack components
"""
from typing import Literal
import cadscript as cad


def cut_slots(body: cad.Body,
              face: str,
              size_x: cad.DimensionDefinitionType,
              size_y: cad.DimensionDefinitionType,
              padding_x: float,
              padding_y: float,
              slot_type: Literal["standard", "large"] = "standard",
              ) -> 'cad.Body':
    """
    Cut slots into a plate
    """
    slot_width = 2.5
    slot_spacing_x = 2.5
    slot_spacing_y = 5
    max_slot_length = 30
    no_slots_limit = 20

    if slot_type == "large":
        slot_width = 5
        max_slot_length = 40

    dim = cad.helpers.get_dimensions_2d([size_x, size_y], True)

    # too small for slots in y direction, do nothing
    if dim.size_y < no_slots_limit:
        return body

    dim.shrink_x(padding_x).shrink_y(padding_y)

    # make a sketch with one or more slots in one vertical row

    pos_list_vertical = cad.pattern_distribute_stretch(
        1, dim.size_y,
        count_x=1,
        max_tile_size_y=max_slot_length,
        spacing_y=slot_spacing_y)

    slot_line = cad.make_sketch()
    slot_height = pos_list_vertical[0].size_y - slot_width
    slot_line.add_slot(width=slot_height, height=slot_width, angle=90, pos=[p.center for p in pos_list_vertical])

    # copy that sketch to cover the whole plate width

    pos_list_horizontal = cad.pattern_distribute(
        dim.tuple_x, dim.tuple_y,
        slot_width, dim.size_y,
        min_spacing_x=slot_spacing_x)

    slot_area = cad.make_sketch()
    slot_area.add_sketch(slot_line, pos=pos_list_horizontal)

    # do the cut
    body.cut_extrude(face, slot_area, -999)
    return body


def cut_w_pattern(body: cad.Body,
                  face: str,
                  size_x: cad.DimensionDefinitionType,
                  size_y: cad.DimensionDefinitionType,
                  padding_x: float,
                  padding_y: float,
                  min_spacing: float = 0,
                  cut_depth: float = 10,
                  ) -> 'cad.Body':
    """
    Cut a W-pattern into a plate
    """
    w_width = 90
    w_thickness = 15

    dim = cad.helpers.get_dimensions_2d([size_x, size_y], True)
    dim.shrink_x(padding_x).shrink_y(padding_y)
    if dim.size_x < w_width and dim.size_x > 50:
        # smaller than usual W, scale it down
        new_width = dim.size_x
        w_thickness = w_thickness * (new_width / w_width)
        w_width = new_width

    # distribute Ws in x direction
    pos_list = cad.pattern_distribute(dim.tuple_x, dim.tuple_y,
                                      w_width, dim.size_y,
                                      min_spacing_x=min_spacing)
    if not pos_list:
        return body

    sketch_w = cad.make_sketch()
    sketch_w.add_sketch(make_w(w_width, dim.size_y, w_thickness), pos=pos_list)

    # trim Ws to cutt off unwanted round parts
    cut_sketch = cad.make_sketch()
    cut_sketch.add_rect(dim.tuple_x, dim.tuple_y)
    cut_sketch.cut_sketch(sketch_w)

    # do the cut
    body.cut_extrude(face, cut_sketch, -cut_depth)
    return body


def make_w(width: float, height: float, thickness: float):
    """
    Create a sketch for a W-shaped bar
    It is sized larger than the given width and height to allow cutting
    to get rid of rounded corners
    """
    y1 = height + thickness  # offset outer points  to avoid rounding
    y0 = -thickness
    sketch = cad.make_sketch()
    sketch.add_slot(start=(-width / 2, y1), end=(-width / 4, y0), diameter=thickness)
    sketch.add_slot(start=(-width / 4, y0), end=(0, y1), diameter=thickness)
    sketch.add_slot(start=(0, y1), end=(width / 4, y0), diameter=thickness)
    sketch.add_slot(start=(width / 4, y0), end=(width / 2, y1), diameter=thickness)

    return sketch.center()
