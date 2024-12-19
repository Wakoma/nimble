"""
This configuration module stores the standard rack parameters for nimble and also
the a class for generating a full cofiguration for a nimble rack `NimbleConfiguration()`.
"""


import os
from copy import deepcopy
import posixpath


from cadorchestrator.components import (GeneratedMechanicalComponent,
                                        AssembledComponent,
                                        Assembly)

from nimble_build_system.cad import RackParameters
from nimble_build_system.cad.shelf import create_shelf_for
from nimble_build_system.orchestration.paths import REL_MECH_DIR

def create_assembly(config_dict):
    selected_device_ids = config_dict['device-ids']
    config = NimbleConfiguration(selected_device_ids)
    return config.main_assembly

class NimbleConfiguration:
    """
    This class represents a specific nimble configuration
    """
    _rack_params: RackParameters
    _devices: list
    _shelves: list


    def __init__(self, selected_device_ids):

        self._rack_params = RackParameters()

        self._selected_device_ids = selected_device_ids

        self._shelves = self._generate_shelf_list(selected_device_ids)
        self._top_level_components = self._generate_assembled_components_list()

        self.main_assembly = self._generate_main_assembly()

    def _generate_main_assembly(self):

        source = os.path.join(REL_MECH_DIR, "assembly_renderer.py")
        source = posixpath.normpath(source)

        main_assembly = Assembly(
            key='nimble_rack',
            name='Nimble Rack',
            description='Assembled nimble rack',
            output_files=[
                "./assembly/assembly.glb",
            ],
            source_files=[source],
            parameters={},
            application="cadquery",
            component_data_parameter='assembly.parts'
        )

        main_assembly.set_parameter_file(
            file_id="assembly_definition_file",
            filename="assembly-def.yaml"
        )

        for assm_component in self._top_level_components:
            main_assembly.add_component(assm_component)

        main_assembly.set_documentation(self._main_assembly_docs())
        main_assembly.set_documentation_filename("insert_shelves.md")
        return main_assembly

    def _main_assembly_docs(self):
        md = "* Insert the shelves into the rack in the following order "
        md += "(from top to bottom)\n"

        for shelf in self._shelves:
            #TODO get docs from the assembly rather than the component
            # once it is set up fully
            md_file = shelf.shelf_component.documentation_filename
            shelf_name = shelf.shelf_component.name

            md += "[Assembled "+shelf_name+"]("+md_file+"){make, qty:1, cat: prev}\n"
        #TODO Here we really need to be listing the assembly steps differently if the
        # shelves are broad.
        md += "* Secure each in place with four [M4x10mm cap screws]{qty:"
        md += str(2*len(self._shelves))+", cat:mech}\n\n"
        return md

    @property
    def devices(self):
        """
        Return the devices in this configuration as a list of Device objects
        """

        return [shelf.device for shelf in self._shelves]


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
        return sum(shelf.height_in_u for shelf in self._shelves)

    def _generate_assembled_components_list(self):

        # collect all needed parts and their parameters
        return [self._rack] + [i.assembled_shelf for i in self._shelves]

    @property
    def _rack(self):
        source = os.path.join(REL_MECH_DIR, "assembly_renderer.py")
        source = posixpath.normpath(source)
        rack = Assembly(
            key='empty_rack',
            name='Empty Nimble Rack',
            description='An empty rack for a nimble',
            output_files=[
                "./assembly/rack.step",
            ],
            source_files=[source],
            parameters={},
            application="cadquery",
            component_data_parameter='assembly.parts'
        )

        rack.set_parameter_file(
            file_id="assembly_definition_file",
            filename="empty_rack-pars.yaml"
        )

        rack_components = self._legs +  [self._baseplate, self._topplate]

        for assm_component in rack_components:
            rack.add_component(assm_component)

        return AssembledComponent(
            key="empty rack",
            component=rack,
            data={"position": (0,0,0)},
            include_key=True,
            include_stepfile=True
        )

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
                    data={
                        "position": (x_pos, y_pos, self._rack_params.base_plate_thickness),
                        "color": "gray82"
                    },
                include_key=True,
                include_stepfile=True
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
            data = {'position': (0, 0, 0)},
            include_key=True,
            include_stepfile=True
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
            data = {'position': (0, 0, top_pos)},
            include_key=True,
            include_stepfile=True
        )

    def _generate_shelf_list(self, selected_device_ids):
        """
        Generate aseembled components for each shelf.
        """

        shelves = []
        z_offset = self._rack_params.bottom_tray_offet
        height_in_u = 0
        for i, device_id in enumerate(selected_device_ids):
            x_pos = 0
            y_pos = -self._rack_params.rack_width / 2.0
            z_pos = z_offset + height_in_u * self._rack_params.mounting_hole_spacing
            color = 'dodgerblue1' if i%2 == 0 else 'deepskyblue1'
            shelf = create_shelf_for(device_id=device_id,
                                     assembly_key=f"shelf_{i}",
                                     position=(x_pos, y_pos, z_pos),
                                     color=color)

            shelves.append(shelf)

            height_in_u += shelf.height_in_u

        return shelves
