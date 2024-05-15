"""
This configuration module stores the standard rack parameters for nimble and also
the a class for generating a full cofiguration for a nimble rack `NimbleConfiguration()`.
"""


import os
from dataclasses import dataclass
from copy import deepcopy
import posixpath
import json

from nimble_orchestration.assembly_def_generator import AssemblyDefGenerator
from nimble_orchestration.components import GeneratedMechanicalComponent, AssembledComponent
from nimble_orchestration.device import Device
from nimble_orchestration.paths import MODULE_PATH, REL_MECH_DIR


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

class NimbleConfiguration:
    """
    This class represents a specific nimble configuration
    """
    _rack_params: RackParameters
    _devices: list
    _components: list
    _assembled_components: list

    def __init__(self, selected_devices_ids):

        self._rack_params = RackParameters()
        devices_filename = os.path.join(MODULE_PATH, "devices.json")

        # read devices file, select apprpriate entries

        selected_devices = []
        with open(devices_filename, encoding="utf-8") as devices_file:
            all_devices = json.load(devices_file)
            def find_device(device_id):
                return next((x for x in all_devices if x['ID'] == device_id), None)
            selected_devices = [Device(find_device(x)) for x in selected_devices_ids]

        self._devices = deepcopy(selected_devices)
        self._assembled_components = self._generate_assembled_components_list()
        self._components = []
        for assembled_component in self._assembled_components:
            component = assembled_component.component
            if component not in self._components:
                self._components.append(component)


    @property
    def devices(self):
        """
        Return the devices in this configuration as a list of Device objects
        """
        #Deepcopy to avoid them being edited in place
        return deepcopy(self._devices)

    @property
    def components(self):
        """
        Return a list of the mechanical components used in this nimble configuration.
        There is only one per each type of object, to see all objects for assembly see
        `assembled_components()`

        Each object in the list is and instance of GeneratedMechanicalComponent
        """
        return deepcopy(self._components)

    @property
    def assembled_components(self):
        """
        Return a list of the components assembled in this nimble rack.

        Each object in the list is and instance of AssembledComponent, giving information
        such as the position and the assembly step. To just see the list of componet types
        see `components()`
        """
        return deepcopy(self._assembled_components)

    @property
    def total_height_in_units(self):
        """
        Return the total height of the needed rack in units
        """
        return sum(device.height_in_units for device in self._devices)

    def _generate_assembled_components_list(self):

        # collect all needed parts and their parameters

        rack_components = self._legs +  [self._baseplate, self._topplate]
        return rack_components + self._trays

    @property
    def _legs(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/rack_leg.py")
        source = posixpath.normpath(source)
        beam_height = self._rack_params.beam_height(self.total_height_in_units)
        hole_pos = (self._rack_params.single_width - self._rack_params.beam_width) / 2.0

        component =  GeneratedMechanicalComponent(
            key="rack_leg",
            name="Rack leg",
            description="One of the 4 legs of the printed rack",
            output_files=[
                "./printed_components/beam.step",
                "./printed_components/beam.stl",
            ],
            source_files=[source],
            parameters={
                "length": beam_height,
                "hole_spacing": self._rack_params.mounting_hole_spacing,
            },
            application="cadquery"
        )

        # 4 rack legs
        legs = [
            ("rack_leg1", -hole_pos, -hole_pos),
            ("rack_leg2", hole_pos, -hole_pos),
            ("rack_leg3", hole_pos, hole_pos),
            ("rack_leg4", -hole_pos, hole_pos)
        ]

        assembled_legs = []
        for key, x_pos, y_pos in legs:
            assembled_legs.append(
                AssembledComponent(
                    key=key,
                    component=component,
                    position = (x_pos, y_pos, self._rack_params.base_plate_thickness),
                    step=2
            )
        )
        return assembled_legs

    @property
    def _baseplate(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/base_plate.py")
        source = posixpath.normpath(source)
        component = GeneratedMechanicalComponent(
            key="baseplate",
            name="Baseplate",
            description="The base plate of the rack",
            output_files=[
                "./printed_components/baseplate.step",
                "./printed_components/baseplate.stl",
            ],
            source_files=[source],
            parameters={
                "width": self._rack_params.single_width,
                "depth": self._rack_params.single_width,
            },
            application="cadquery"
        )
        return AssembledComponent(
            key="baseplate",
            component=component,
            position = (0, 0, 0),
            step=1
        )


    @property
    def _topplate(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/top_plate.py")
        source = posixpath.normpath(source)
        beam_height = self._rack_params.beam_height(self.total_height_in_units)
        top_pos = beam_height + self._rack_params.base_plate_thickness
        component =  GeneratedMechanicalComponent(
            key="topplate",
            name="Top plate",
            description="3D printed top plate",
            output_files=[
                "./printed_components/topplate.step",
                "./printed_components/topplate.stl",
            ],
            source_files=[source],
            parameters={
                "width": self._rack_params.single_width,
                "depth": self._rack_params.single_width,
            },
            application="cadquery"
        )

        return AssembledComponent(
            key="topplate",
            component=component,
            position = (0, 0, top_pos),
            step=3
        )

    @property
    def _trays(self):
        """
        Generate aseembled components for each tray. This function is a bit
        long and messy!
        """

        source = os.path.join(REL_MECH_DIR, "components/cadquery/nimble_tray.py")
        source = posixpath.normpath(source)
        trays = []
        z_offset = self._rack_params.bottom_tray_offet
        height_in_u = 0
        for i, device in enumerate(self._devices):
            x_pos = -self._rack_params.tray_width / 2.0
            y_pos = -self._rack_params.single_width / 2.0 - 4
            z_pos = z_offset + height_in_u * self._rack_params.mounting_hole_spacing
            tray_id = device.tray_id

            component = GeneratedMechanicalComponent(
                key=tray_id,
                name=f"{device.name} tray",
                description="A tray for " + device.name,
                output_files=[
                    f"./printed_components/{tray_id}.step",
                    f"./printed_components/{tray_id}.stl",
                ],
                source_files=[source],
                parameters={
                    "height_in_hole_unites": device.height_in_units,
                    "tray_width": self._rack_params.tray_width,
                    "tray_depth": self._rack_params.tray_depth,
                },
                application="cadquery"
            )

            trays.append(
                AssembledComponent(
                    key=f"tray_{i}",
                    component=component,
                    position = (x_pos, y_pos, z_pos),
                    step=4
                )
            )

            height_in_u += device.height_in_units
        return trays

    @property
    def assembly_definition(self):
        """
        Create an assembly defition. This is a simple object reprenting a file
        that is output. The file only contains the name, step-file, position, and
        assembly step. It is sufficent for creating the final rack, but too
        simplistic for generating assembly renders
        """

        assembly = AssemblyDefGenerator()

        for assembled_component in self.assembled_components:
            assembly.add_part(
                name=assembled_component.key,
                step_file=assembled_component.component.step_representation,
                position=assembled_component.position,
                assembly_step=str(assembled_component.step)
            )

        return assembly
