
from dataclasses import dataclass
from typing import Literal

@dataclass
class RackParameters:
    """
    A class to hold the RackParameters, both fixed and derived
    """

    beam_width: float = 20.0
    nominal_rack_width: Literal["6inch", "10inch", "10inch_reduced"] = "6inch"
    tray_depth: float = 115
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
        raise ValueError(f"Unknown rack witdth {self.nominal_rack_width}")

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

