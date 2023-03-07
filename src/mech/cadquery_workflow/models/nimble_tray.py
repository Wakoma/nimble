import cadquery as cq
import math


class Params:
  def __init__(self):
    # Default length unit is mm.
    self.tray_width = 155
    self.tray_depth = 155
    self.leg_width = 20
    self.height_in_hole_unites = 2
    self.wall_thickness = 4
    self.hole_distance = 14  # Distance between the holes
    self.hole_diameter = 3.6

  @property
  def inner_width(self):
    return self.tray_width - self.wall_thickness * 2

  @property
  def inner_depth(self):
    return self.tray_depth - self.wall_thickness * 2

  @property
  def tray_height(self):
    return self.height_in_hole_unites * self.hole_distance

  @property
  def inner_height(self):
    return self.tray_height - self.wall_thickness

  @staticmethod
  def build_for_inner_dims(width, height, depth):
    p = Params()
    p.tray_width = width + 2 * p.wall_thickness
    p.tray_depth = depth + 2 * p.wall_thickness
    # Convert hole into number of holes.
    nh = math.ceil(height / p.hole_distance)
    # The number of holes must be at least two
    p.height_in_hole_unites = max(nh, 2)
    return p

def _create_part(params):
  tray = cq.Workplane("XY").box(params.tray_width, params.tray_depth, params.tray_height, centered=False)
  tray = tray.faces(">Z").workplane().moveTo(params.wall_thickness, params.wall_thickness).rect(params.inner_width,
                                                                                                params.inner_depth,
                                                                                                centered=False).cutBlind(
    -params.inner_height)

  wings = cq.Workplane("XY").moveTo(-params.leg_width, 0).box(params.tray_width + params.leg_width * 2,
                                                              params.wall_thickness, params.tray_height,
                                                              centered=False)
  # Add holes
  wings = wings.faces(">Y").workplane().moveTo(params.leg_width / 2, params.hole_distance / 2).circle(
    params.hole_diameter / 2).cutThruAll()
  wings = wings.faces(">Y").workplane().moveTo(params.leg_width / 2,
                                               params.tray_height - params.hole_distance / 2).circle(
    params.hole_diameter / 2).cutThruAll()
  wings = wings.faces(">Y").workplane().moveTo(-params.tray_width - params.leg_width / 2,
                                               params.hole_distance / 2).circle(params.hole_diameter / 2).cutThruAll()
  wings = wings.faces(">Y").workplane().moveTo(-params.tray_width - params.leg_width / 2,
                                               params.tray_height - params.hole_distance / 2).circle(
    params.hole_diameter / 2).cutThruAll()
  result = tray.union(wings)
  result = result.faces(">Y").workplane().moveTo(-params.tray_width / 2, -params.tray_height / 2).rect(
    params.inner_width - params.wall_thickness, params.inner_height - params.wall_thickness).cutThruAll()

  return result


def create(height_in_units):
  params = Params()
  params.height_in_hole_unites = height_in_units
  return _create_part(params)
