"""
cadquery module that takes an assembly-def.yaml file and generate an assembly from it.

The assembly-def.yaml file is a yaml file that contains a list of parts and their
positions in the assembly.
Example file:
assembly:
  parts:
  - name: baseplate
    step-file: ./step/baseplate.step
    position: (0, 0, 0)
  - name: rack_leg1
    step-file: ./step/beam.step
    position: (-67.5, -67.5, 3)

"""

import os
from pathlib import Path
import cadquery as cq
import yaml

from nimble_build_system.cad.shelf import create_shelf_for
from nimble_build_system.cad.fasteners import Screw

from nimble_build_system.cad.renderer import generate_render
from cq_annotate.views import explode_assembly

assembly_definition_file = "../build/assembly-def.yaml"
rack_parts_definition_file = "../build/empty_rack-pars.yaml"
render_destination = os.path.join(os.getcwd(), "renders")

class PartDefinition:
    """
    Definition of a part.
    """

    # This is pretty much a glorified dataclass
    # pylint: disable=too-few-public-methods

    name: str
    step_file: str
    position: tuple
    tags: list

    def __init__(self, definition: dict):
        self.name = definition["key"]
        self.step_file = definition.get("step-file", None)
        # convert position from string like "(1,2,3)" to tuple
        self.position = tuple(map(float, definition["position"].strip("()").split(",")))
        self.tags = definition.get("tags", [])
        self.color = definition.get("color", "gray95")
        self.device = definition.get("device", None)
        assert self.device or self.step_file, "No device or step file set."


class AssemblyRenderer:
    """
    create a cq assembly from an assembly definition file.
    """

    _parts: list[PartDefinition] = []
    _assembly_parts: list[PartDefinition] = []


    def __init__(self, assembly_def_file: str):

        with open(assembly_def_file, "r", encoding="utf-8") as f:
            assembly_def = yaml.load(f, Loader=yaml.FullLoader)
            for part_def in assembly_def["assembly"]["parts"]:
                self._parts.append(PartDefinition(part_def))

        # Load the rack parts definition file
        # Check to see if the _assembly_parts list is empty
        if len(self._assembly_parts) == 0:
            with open(rack_parts_definition_file, "r", encoding="utf-8") as f:
                rack_parts_def = yaml.load(f, Loader=yaml.FullLoader)
                for part_def in rack_parts_def["assembly"]["parts"]:
                    self._assembly_parts.append(PartDefinition(part_def))



    def generate(self) -> cq.Assembly:
        """
        Generate the assembly.
        """
        # Make sure that the render destination exists
        os.makedirs(render_destination, exist_ok=True)

        assembly = cq.Assembly()
        for part in self._parts:
            if part.device:
                # This is a shelf and we load it directly rather than from an STEP.
                shelf_obj = create_shelf_for(part.device)

                # Create the shelf that will go in the assembly
                cq_part = shelf_obj.generate_assembly_model(
                                        shelf_obj.renders["assembled"]["render_options"])

                # Generate all render pngs for this shelf
                shelf_obj.generate_renders(base_path=render_destination)
            else:
                cq_part = cq.importers.importStep(part.step_file)
            for tag in part.tags:
                cq_part = cq_part.tag(tag)
            #Pylint appears to be confused by the multimethod __init__ used by cq.Location

            assembly.add(
                cq_part,
                name=part.name,
                loc=cq.Location(part.position), #pylint: disable=no-value-for-parameter
                color=cq.Color(part.color)
            )

        return assembly


    def generate_assembly_process_renders(self):
        """
        Generate renders of the assembly steps.
        """

        # Allows us to collect the assembly parts for this configuration
        assembly_parts = {
            "shelves": [],
            "legs": [],
            "top_plate": None,
            "base_plate": None,
        }

        # By default, do not explode parts
        explode_location = cq.Location((0, 0, 0))

        # Create a union of _assembly_parts and _parts
        all_parts = self._parts + self._assembly_parts

        for part in all_parts:
            # See if we have a shelf
            if part.device:
                # This is a shelf and we load it directly rather than from an STEP.
                shelf_obj = create_shelf_for(part.device)

                # Create the shelf that will go in the assembly
                cq_part = shelf_obj.generate_assembly_model(
                                        shelf_obj.renders["assembled"]["render_options"])

                # Make sure the shelves slide out of the rack when exploded
                if shelf_obj.width_category == "broad":
                    explode_location = cq.Location((0, 0, 75.0))
                else:
                    explode_location = cq.Location((0, -75.0, 0))

                # Save the information for this shelf
                assembly_parts["shelves"].append({
                    "component_type": "shelf",
                    "component": cq_part,
                    "width_category": shelf_obj.width_category,
                    "location": part.position,
                    "color": part.color,
                    "explode_location": explode_location
                })
            # We have something else like a leg or plate
            else:
                cq_part = cq.importers.importStep(part.step_file)

                # Handle the top and bottom plate explode locations differently
                if "plate" in part.name and "top" in part.name:
                    explode_location = cq.Location((0, 0, 100.0))

                    # Save this as the assembly's top plate
                    assembly_parts["top_plate"] = {
                        "component_type": "top_plate",
                        "component": cq_part,
                        "location": part.position,
                        "color": part.color,
                        "explode_location": explode_location
                    }
                elif "plate" in part.name and "base" in part.name:
                    explode_location = cq.Location((0, 0, 0.0))

                    # Save this as the assembly's base plate
                    assembly_parts["base_plate"] = {
                        "component_type": "base_plate",
                        "component": cq_part,
                        "location": part.position,
                        "color": part.color,
                        "explode_location": explode_location
                    }
                elif "leg" in part.name:
                    explode_location = cq.Location((0, 0, 20.0))

                    assembly_parts["legs"].append({
                        "component_type": "leg",
                        "component": cq_part,
                        "location": part.position,
                        "color": part.color,
                        "explode_location": explode_location
                    })

        # Build the assembly in the order we need to explode it
        assembly = cq.Assembly()

        # Add the base plate
        assembly.add(
            assembly_parts["base_plate"]["component"],
            name="base_plate",
            loc=cq.Location(assembly_parts["base_plate"]["location"]),
            color=cq.Color(assembly_parts["base_plate"]["color"]),
            metadata={"explode_translation": assembly_parts["base_plate"]["explode_location"]}
        )

        # Add the legs
        for i, leg in enumerate(assembly_parts["legs"]):
            assembly.add(
                leg["component"],
                name=leg["component_type"] + "_" + str(i),
                loc=cq.Location(leg["location"]),
                color=cq.Color(leg["color"]),
                metadata={"explode_translation": leg["explode_location"]}
            )

        # Add screws based on the base plate location
        base_plate_location = assembly_parts["base_plate"]["location"]

        # Find the outside bounds of the base plate so we can use it to position screws
        base_plate_bounds = assembly_parts["base_plate"]["component"].val().BoundingBox()
        base_plate_width = base_plate_bounds.xlen
        base_plate_height = base_plate_bounds.ylen

        for i in range(4):
            # Allows us to put one in each corner of the base plate without repeating boiler plate
            if i == 0:
                x_mult = 1
                y_mult = 1
            elif i == 1:
                x_mult = -1
                y_mult = 1
            elif i == 2:
                x_mult = 1
                y_mult = -1
            else:
                x_mult = -1
                y_mult = -1

            # Create a screw with the proper location, dimensions and orientation
            cur_screw = Screw(name="screw_" + str(i),
                              position=(base_plate_location[0] + x_mult * base_plate_width / 2.0 -
                                            x_mult * 10.0,
                                        base_plate_location[1] + y_mult * base_plate_height / 2.0 -
                                            y_mult * 10.0,
                                        0),
                              explode_translation=(0.0, 0.0, 45.0),
                              size="M5-0.8",
                              fastener_type="iso10642",
                              axis="-Z",
                              length=10)

            assembly.add(
                cur_screw.fastener_model,
                name="screw_" + str(i),
                loc=cq.Location(cur_screw.position,
                                cur_screw.rotation[0],
                                cur_screw.rotation[1]),
                color=cq.Color("gray"),
                metadata={"explode_translation": cq.Location(cur_screw.explode_translation)}
            )

        # The render options for the PNG
        render_options = {"color_theme": "default",
                          "view": "front-top-right",
                          "zoom": 1.0,
                          "add_device_offset": False,
                          "add_fastener_length": False,
                          "annotate": False,
                          "explode": False}

        # The location to put the renders in
        render_path = Path(render_destination) / "final_assembly_step_1_assembled.png"
        generate_render(model=assembly,
                        file_path=render_path,
                        render_options=render_options)

        # Set up for the exploded and annotated view
        explode_assembly(assembly)
        # render_options["explode"] = True
        render_options["annotate"] = True

        # Exploded view of this assembly step
        render_path = Path(render_destination) / "final_assembly_step_1_annotated.png"
        generate_render(model=assembly,
                        file_path=render_path,
                        render_options=render_options)


# Handle different execution environments, including ExSource-Tools
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    def_file = Path(assembly_definition_file)
    folder = def_file.resolve().parent
    os.chdir(folder)
    # CQGI should execute this whenever called
    assembly = AssemblyRenderer(def_file.name).generate()
    AssemblyRenderer(def_file.name).generate_assembly_process_renders()

    show_object(assembly)
