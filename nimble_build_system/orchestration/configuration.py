"""
This configuration module stores the standard rack parameters for nimble and also
the a class for generating a full cofiguration for a nimble rack `NimbleConfiguration()`.
"""
# pylint: disable=duplicate-code

import os
from copy import deepcopy
import posixpath
import logging

from cadorchestrator.components import (GeneratedMechanicalComponent,
                                        AssembledComponent,
                                        Assembly)

from nimble_build_system.cad import RackParameters
from nimble_build_system.cad.shelf import create_shelf_for
from nimble_build_system.orchestration.paths import REL_MECH_DIR

def create_assembly(config_dict):
    """Function uses device id list for nimble configuration assembly."""
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
        main_assembly.set_documentation_filename("construction.md")
        return main_assembly

    def _main_assembly_docs(self):

        broad_shelf_mds, std_shelf_mds = self._inserting_shelf_docs()

        md = RACK_ASSEMBLY_PREAMBLE

        # Only add the section about broad shelves if there are any
        if broad_shelf_mds:
            # Tweak section title if all shelves are broad.
            if std_shelf_mds:
                md += "## Add the broad shelves {pagestep}\n\n"
            else:
                md += "## Add the shelves {pagestep}\n\n"

            md += "\n".join(broad_shelf_mds)

        md += RACK_TOPPLATE_ASSEMBLY

        # Only add the section about standard shelves if there are any
        if std_shelf_mds:
            # Tweak section title if all shelves are standard.
            if broad_shelf_mds:
                md += "## Add the remaining shelves {pagestep}\n\n"
            else:
                md += "## Add the shelves {pagestep}\n\n"

            md += "\n".join(std_shelf_mds)

        md += RACK_ASSEMBLY_END

        return md

    def _inserting_shelf_docs(self):
        logging.info("-"*10)

        broad_shelf_mds = []
        std_shelf_mds = []
        for i, shelf in enumerate(self._shelves):
            md = ""
            broad = shelf.width_category == "broad"
            md_file = shelf.shelf_component.documentation_filename
            shelf_name = shelf.shelf_component.name
            shelf_link = "[assembled "+shelf_name+"]("+md_file+"){make, qty:1, cat: prev}"
            screw_link = "[M4x10mm button head screws]{qty:4, cat:mech}"
            direction = "top" if broad else "front"
            render_dir = "../build/renders"
            img_pref = f"{render_dir}/final_assembly_{shelf.width_category}_shelves"

            md += f"* Take the {shelf_link} and slide into the rack from the {direction}.\n"
            md += f"* Secure in the position shown in the image below with four {screw_link}.\n\n"
            md += f"![]({img_pref}_shelf_{i+1}_insertion_annotated.png)\n"
            md += f"![]({img_pref}_shelf_{i+1}_installed.png)\n\n"

            if broad:
                broad_shelf_mds.append(md)
            else:
                std_shelf_mds.append(md)
        return broad_shelf_mds, std_shelf_mds

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

RACK_ASSEMBLY_PREAMBLE = """---
Make:
  base plate:
    template: printing.md
    stl-file: ../build/printed_components/baseplate.stl
    stlname: baseplate.stl
    material: PLA
    weight-qty: 50g
  top plate:
    template: printing.md
    stl-file: ../build/printed_components/topplate.stl
    stlname: topplate.stl
    material: PLA
    weight-qty: 50g
  rack legs:
    template: printing.md
    stl-file: ../build/printed_components/beam.stl
    stlname: beam.stl
    material: PLA
    weight-qty: 60g
---

# Construct and populate the rack

{{BOM}}

[M4x10mm countersunk screws]: parts/Hardware.yaml#CskScrew_M4x10mm_SS
[M4x10mm button head screws]: parts/Hardware.yaml#ButtonScrew_M4x10mm_SS

## Attach the legs to the base plate {pagestep}

* Get the [base plate]{make, qty:1, cat:printed} and the four [rack legs]{make, qty:4, cat:printed} that you printed earlier.
* Get a [3mm Allen key](parts/metric_allen_keys.md){qty:1, cat:tool} ready
* Use four [M4x10mm countersunk screws]{qty:4} to attach a leg to each corner of the bottom.

![Exploded assembly of base and legs](../build/renders/final_assembly_base_and_legs_annotated.png)
![Assembly of base and legs](../build/renders/final_assembly_base_and_legs_assembled.png)

"""

RACK_TOPPLATE_ASSEMBLY = """
## Mount the top plate {pagestep}

* Take the [top plate]{make, qty:1, cat:printed} and place it on top of the rack.
* Use four [M4x10mm countersunk screws]{qty:4} to attach the shelf to the four legs of the rack

![Exploded assembly of top plate](../build/renders/final_assembly_topplate_annotated.png)
![Exploded assembly of top plate](../build/renders/final_assembly_topplate_assembled.png)
"""

RACK_ASSEMBLY_END = """

## Final set-up {pagestep}

Your rack should now look like this:
![](../build/assembly/assembly.glb)

The next steps depend on what you want to do with your rack.

- You could put it in a [Peli case](parts/PeliCalse1430.md).
- You will need to wire it. Our component database doesn't have enough information
to know how to wire any arbitrary rack. But we suggest you go to the
[Wakoma website](https://wakoma.co). Join the community, and dicuss wiring your nimble.

"""