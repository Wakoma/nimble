
from dataclasses import dataclass

@dataclass
class RackParameters:
    """
    A class to hold the RackParameters, both fixed and derived
    """

    beam_width: float = 20.0
    single_width: float = 155
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
    def tray_width(self):
        """
        Return derived parameter for the width of a standard tray
        """
        return self.single_width - 2 * self.beam_width

    def beam_height(self, total_height_in_units):
        """
        Return derived parameter for the height of a beam for a rack with a given
        total height specified in units.
        """
        return self.base_clearance + total_height_in_units * self.mounting_hole_spacing
