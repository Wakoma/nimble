"""
On loading nimble_builder the RackParameters dataclass will be available
"""
from dataclasses import dataclass
from typing import Literal

@dataclass
class RackParameters:
    """
    A class to hold the RackParameters, both fixed and derived
    """

    beam_width: float = 20.0
    nominal_rack_width: Literal["6inch", "10inch", "10inch_reduced"] = "6inch"
    mounting_screws: Literal["M4", "M6"] = "M4"

    tray_front_panel_thickness: float = 4
    tray_bottom_thickness: float = 2
    tray_side_wall_thickness: float = 2.5
    tray_back_wall_thickness: float = 2.5
    # distance between side walls of broad trays to the bounding box of the rack
    broad_tray_clearance: float = 16

    tray_depth: float = 115
    corner_fillet: float = 2
    mounting_hole_spacing: float = 14
    base_plate_thickness: float = 3
    top_plate_thickness: float = 3
    base_clearance: float = 4
    bottom_tray_offet: float = 5
    end_plate_hole_dia: float = 4.7
    end_plate_hole_countersink_dia: float = 10
    end_plate_rail_width: float = 5
    end_plate_rail_height: float = 3
    end_plate_star_width: float = 9


    @property
    def mounting_hole_clearance_diameter(self):
        """
        Return the diameter for a clearance hole for the front mounting screws.
        This is determined by the `mounting_screws` parameter.
        Clearance holes should be used in tray fronts.
        See also: mounting_hole_tap_diameter
        """
        if self.mounting_screws == "M4":
            return 4.3
        if self.mounting_screws == "M6":
            return 6.5
        raise ValueError(f"Unknown screw size {self.mounting_screws}")

    @property
    def mounting_hole_tap_diameter(self):
        """
        Return the diameter for a tapped hole for the front mounting screws.
        This is determined by the `mounting_screws` parameter.
        Clearance holes should be in the legs where the screw will tap.
        As 3D printers tend to over extrude ad the fact that the machine screws
        are tapping directly into plastic the holes are larger than standard
        metric tap holes.
        See also: mounting_hole_tap_diameter
        """
        if self.mounting_screws == "M4":
            return 3.6
        if self.mounting_screws == "M6":
            return 5.5
        raise ValueError(f"Unknown screw size {self.mounting_screws}")

    @property
    def rack_width(self):
        """
        Return the rack width in mm as determined by the nominal_rack_width.
        Options are:
            "6inch"  - 155mm - full width (front panel) of the 6 inch nimble rack
            "10inch" - 254mm - full width (front panel) of the 10 inch rack
            "10inch_reduced - 250mm - as above bu reduced to fit into a 250mm wide printer
        """
        if self.nominal_rack_width == "6inch":
            return 155
        if self.nominal_rack_width == "10inch":
            return 254
        if self.nominal_rack_width == "10inch_reduced":
            return 250
        raise ValueError(f"Unknown rack width {self.nominal_rack_width}")

    @property
    def tray_width(self):
        """
        Return derived parameter for the width of a standard tray
        """
        return self.rack_width - 2 * self.beam_width

    def beam_height(self, total_height_in_u):
        """
        Return derived parameter for the height of a beam for a rack with a given
        total height specified in units.
        """
        return self.base_clearance + total_height_in_u * self.mounting_hole_spacing

    def tray_height(self, height_in_u):
        """
        Return derived parameter for the height of a tray specified in units.
        """
        return height_in_u * self.mounting_hole_spacing
