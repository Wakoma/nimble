"""
This configuration module stores the standard rack parameters for nimble and also
the a class for generating a full cofiguration for a nimble rack `NimbleConfiguration()`.
"""


import os
from copy import deepcopy
import posixpath
import json

from cadorchestrator.configuration import Configuration
from cadorchestrator.components import (GeneratedMechanicalComponent,
                                        AssembledComponent)

from nimble_builder import RackParameters
from nimble_orchestration.shelf import Shelf
from nimble_orchestration.device import Device
from nimble_orchestration.paths import MODULE_PATH, REL_MECH_DIR

class NimbleConfiguration(Configuration):
    """
    This class represents a specific nimble configuration
    """
    _rack_params: RackParameters
    _devices: list
    _shelves: list


    def __init__(self, selected_devices_ids):

        super().__init__()

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
        self._shelves = self._generate_shelf_list
        self._assembled_components = self._generate_assembled_components_list()


    @property
    def devices(self):
        """
        Return the devices in this configuration as a list of Device objects
        """
        #Deepcopy to avoid them being edited in place
        return deepcopy(self._devices)


    @property
    def shelves(self):
        """
        Return a list of the shelves assembled in this nimble rack.

        Each object in the list is an instance of the Shelf object,
        this holds both the information on the assembled shelf, and
        on the Device the shelf is for.
        """
        return deepcopy(self._shelves)

    @property
    def total_height_in_u(self):
        """
        Return the total height of the needed rack in units
        """
        return sum(device.height_in_u for device in self._devices)

    def _generate_assembled_components_list(self):

        # collect all needed parts and their parameters

        rack_components = self._legs +  [self._baseplate, self._topplate]
        return rack_components + [i.assembled_shelf for i in self._shelves]

    @property
    def _legs(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/rack_leg.py")
        source = posixpath.normpath(source)
        beam_height = self._rack_params.beam_height(self.total_height_in_u)
        hole_pos = (self._rack_params.rack_width - self._rack_params.beam_width) / 2.0

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
                "length": beam_height
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
                    step=2,
                    color="gray82"
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
                "width": self._rack_params.rack_width,
                "depth": self._rack_params.rack_width,
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
        beam_height = self._rack_params.beam_height(self.total_height_in_u)
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
                "width": self._rack_params.rack_width,
                "depth": self._rack_params.rack_width,
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
    def _generate_shelf_list(self):
        """
        Generate aseembled components for each shelf. This function is a bit
        long and messy!
        """

        source = os.path.join(REL_MECH_DIR, "components/cadquery/tray_6in.py")
        source = posixpath.normpath(source)
        shelves = []
        z_offset = self._rack_params.bottom_tray_offet
        height_in_u = 0
        for i, device in enumerate(self._devices):
            x_pos = 0
            y_pos = -self._rack_params.rack_width / 2.0
            z_pos = z_offset + height_in_u * self._rack_params.mounting_hole_spacing
            shelf_key = device.shelf_key
            color = 'dodgerblue1' if i%2 == 0 else 'deepskyblue1'
            component = GeneratedMechanicalComponent(
                key=shelf_key,
                name=f"{device.name} shelf",
                description="A shelf for " + device.name,
                output_files=[
                    f"./printed_components/{shelf_key}.step",
                    f"./printed_components/{shelf_key}.stl",
                ],
                source_files=[source],
                parameters={
                    "height_in_u": device.height_in_u,
                    "shelf_type": device.shelf_builder_id,
                },
                application="cadquery"
            )

            assm_component = AssembledComponent(
                key=f"shelf_{i}",
                component=component,
                position = (x_pos, y_pos, z_pos),
                step=4,
                color=color
            )

            shelves.append(Shelf(assm_component, device))

            height_in_u += device.height_in_u
        return shelves

    @property
    def assembly_source_file(self):
        """
        This is a bit add hoc until we we work out how best to specify assemblies.
        Currently we just pass a cad quey file that should pass the assembly def.
        We should move away from this with classes for assemblies and sub assemblies.
        """
        source = os.path.join(REL_MECH_DIR, "assembly_renderer.py")
        source = posixpath.normpath(source)
        return source
