"""
Orchestration script using exsource.
This is a module used by generate.py and generate_static.py
"""

import os
import posixpath
import json
from copy import copy, deepcopy
from dataclasses import dataclass
import exsource_tools
import exsource_tools.cli
import exsource_tools.tools

from nimble_orchestration.device import Device
from nimble_orchestration.exsource_def_generator import ExsourceDefGenerator
from nimble_orchestration.assembly_def_generator import AssemblyDefGenerator

MODULE_PATH = os.path.normpath(os.path.join(os.path.split(__file__)[0], '..'))
BUILD_DIR = os.path.join(MODULE_PATH, "build")
REL_MECH_DIR = os.path.relpath(os.path.join(MODULE_PATH, "mechanical"), BUILD_DIR)


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

class MechanicalComponent:
    """
    This is a generic class for any mechanical component. If it is a generic
    component rather than a generated one then use this class, for generated
    components use the child-class GeneratedMechanicalComponent
    """

    def __init__(self, name: str, description:str, output_files: list) -> None:
        self._name = name
        self._description = description
        self._output_files = output_files

    @property
    def name(self):
        """Return the name of the component"""
        return self._name

    @property
    def description(self):
        """Return the description of the component"""
        return self._description

    @property
    def output_files(self):
        """Return a copy of the list of output CAD files that represent the component"""
        return copy(self._output_files)

    @property
    def step_representation(self):
        """
        Return the path to the STEP file that represents this part. Return None
        if not defined
        """
        for output_file in self.output_files:
            if output_file.lower().endswith(('stp','step')):
                return output_file
        return None

class GeneratedMechanicalComponent(MechanicalComponent):

    def __init__(
        self,
        name: str,
        description: str,
        output_files: list,
        source_files: list,
        parameters: dict,
        application: str
    ) -> None:

        super().__init__(name, description, output_files)
        self._source_files = source_files
        self._parameters = parameters
        self._application = application

    @property
    def source_files(self):
        """Return a copy of the list of the input CAD files that represent the component"""
        return copy(self._source_files)

    @property
    def parameters(self):
        """Return the parameters associated with generating this mechancial component"""
        return deepcopy(self._parameters)

    @property
    def application(self):
        """Return the name of the application used to process the input CAD files"""
        return self._application

    @property
    def as_exsource_dict(self):
        """Return this object as a dictionary of the part information for exsource"""
        return {
            "name": self.name,
            "description": self.description,
            "output_files": self.output_files,
            "source_files": self.source_files,
            "parameters": self.parameters,
            "application": self.application
        }

class NimbleConfiguration:
    """
    This class represents a specific nimble configuration
    """
    _rack_params: RackParameters
    _devices: list
    _components: list

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
        self._components = self._generate_components_list()

        # calculate assembly dimensions

    @property
    def devices(self):
        """
        Return the devices in this configuration as a list of Device objects
        """
        #Deepcopy to avoid them being edited in place
        return deepcopy(self._devices)

    @property
    def total_height_in_units(self):
        """
        Return the total height of the needed rack in units
        """
        return sum([device.height_in_units for device in self._devices])

    def _generate_components_list(self):

        # collect all needed parts and their parameters

        rack_components = [self.leg, self.baseplate, self.topplate]
        return rack_components + self.trays

    @property
    def components(self):
        """
        Return a list of dictionaries. Each dictionary has the exsource data
        for a single component in the rack.

        At a future point these dictionaries should be object.
        """
        return deepcopy(self._components)

    def get_component(self, name):
        for component in self.components:
            if component.name == name:
                return component
        return None

    @property
    def leg(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/rack_leg.py")
        source = posixpath.normpath(source)
        beam_height = self._rack_params.beam_height(self.total_height_in_units)

        return GeneratedMechanicalComponent(
            name="rack_leg",
            description="3D printed rack leg",
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

    @property
    def baseplate(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/base_plate.py")
        source = posixpath.normpath(source)
        return GeneratedMechanicalComponent(
            name="baseplate",
            description="3D printed base plate",
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

    @property
    def topplate(self):
        source = os.path.join(REL_MECH_DIR, "components/cadquery/top_plate.py")
        source = posixpath.normpath(source)
        return GeneratedMechanicalComponent(
            name="topplate",
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

    @property
    def trays(self):
        # set of needed trays
        source = os.path.join(REL_MECH_DIR, "components/cadquery/nimble_tray.py")
        source = posixpath.normpath(source)
        trays = []
        for device in self._devices:
            tray_id = device.get_tray_id()
            trays.append(GeneratedMechanicalComponent(
                name=tray_id,
                description="tray for " + device.name,
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
            ))
        return trays

    @property
    def assembly_definition(self):

        #TODO Create and "assembled_component" class which knows which mechanical
        # component it is using to remove the string based matching.

        assembly = AssemblyDefGenerator()
        self._register_rack_assembly(assembly)
        self._register_trays_assembly(assembly)
        return assembly

    def _register_rack_assembly(self, assembly):

        # base plate
        assembly.add_part(
            name="baseplate",
            step_file=self.get_component("baseplate").step_representation,
            position=(0, 0, 0),
            assembly_step="1"
        )

        hole_pos = (self._rack_params.single_width - self._rack_params.beam_width) / 2.0
        # 4 rack legs
        legs = [
            ("rack_leg1", -hole_pos, -hole_pos),
            ("rack_leg2", hole_pos, -hole_pos),
            ("rack_leg3", hole_pos, hole_pos),
            ("rack_leg4", -hole_pos, hole_pos)
        ]

        for name, x_pos, y_pos in legs:
            assembly.add_part(
                name=name,
                step_file=self.get_component("rack_leg").step_representation,
                position=(x_pos, y_pos, self._rack_params.base_plate_thickness),
                assembly_step="2"
            )

        # top plate
        beam_height = self._rack_params.beam_height(self.total_height_in_units)
        top_pos = beam_height + self._rack_params.base_plate_thickness
        assembly.add_part(
            name="topplate",
            step_file=self.get_component("topplate").step_representation,
            position=(0, 0, top_pos),
            assembly_step="3"
        )
        # todo roatation
        #    topplate = topplate.rotateAboutCenter((1, 0, 0), 180)
        #    topplate = topplate.rotateAboutCenter((0, 0, 1), 180)


    def _register_trays_assembly(self, assembly):
        """
        Register all of the trays into the assembly defintion
        """
        x_pos = -self._rack_params.tray_width / 2.0
        y_pos = -self._rack_params.single_width / 2.0 - 4
        z_pos = self._rack_params.bottom_tray_offet
        for (index, device) in enumerate(self.devices):
            assembly.add_part(
                name=f"tray_{index}",
                step_file=self.get_component(device.get_tray_id()).step_representation,
                position=(x_pos, y_pos, z_pos),
                assembly_step="4"
            )
            z_pos += device.height_in_units * self._rack_params.mounting_hole_spacing


class OrchestrationRunner:
    """
    This class is used to generate all the files needed to build and document
    any nimble configuration
    This includes:
    Preparing the build environment,
    generating the components
    generating assembly renders
    generate gitbuilding files
    """


    def __init__(self) -> None:
        """
        Set up build environment.
        """
        if not os.path.exists(BUILD_DIR):
            os.makedirs(BUILD_DIR)

    def generate_components(self, components):
        """
        generate the rack components
        """
        exsource = ExsourceDefGenerator()
        exsource_path = os.path.join(BUILD_DIR, "component-exsource-def.yaml")
        for component in components:
            exsource.add_part(**component.as_exsource_dict)
        exsource.save(exsource_path)
        self._run_exsource(exsource_path)


    def generate_assembly(self, assembly_definition):
        # save assembly definition
        assembly_definition.save(os.path.join(BUILD_DIR, "assembly-def.yaml"))

        # add assembly to exsource
        exsource = ExsourceDefGenerator()
        exsource_path = os.path.join(BUILD_DIR, "assembly-exsource-def.yaml")
        exsource.add_part(
            name="assembly",
            description="assembly",
            output_files=[
                "./assembly/assembly.stl",
                # "./step/assembly.step",
                "./assembly/assembly.gltf",
            ],
            source_files=[os.path.join(REL_MECH_DIR, "assembly_renderer.py")],
            parameters={
                "assembly_definition_file": "assembly-def.yaml",
            },
            application="cadquery",
            dependencies=assembly_definition.get_step_files()
        )

        # save exsource definition
        exsource.save(exsource_path)
        self._run_exsource(exsource_path)


    def _run_exsource(self, exsource_path):

        cur_dir = os.getcwd()
        # change into self._build_dir
        exsource_dir, exsource_filename = os.path.split(exsource_path)
        os.chdir(exsource_dir)

        # run exsource-make
        exsource_def = exsource_tools.cli.load_exsource_file(exsource_filename)
        processor = exsource_tools.tools.ExSourceProcessor(exsource_def, None, None)
        processor.make()
        os.chdir(cur_dir)
