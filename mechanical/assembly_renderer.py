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

from cq_annotate.views import explode_assembly

from nimble_build_system.cad.shelf import create_shelf_for
from nimble_build_system.cad.fasteners import Screw

from nimble_build_system.cad.renderer import generate_render

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

    # pylint: disable=protected-access

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

    #pylint: disable=too-many-arguments
    def add_end_plate_mounting_screws(self,
                                       assembly,
                                       base_plate_location,
                                       base_plate_width,
                                       base_plate_height,
                                       leg_explode_z,
                                       orientation):
        """
        Adds the screws that secure the top and bottom plates to the legs.
        """
        # Handle the top plate and the bottom plate
        if orientation == "top":
            alignment_axis = "Z"
            name_prefix = "top_plate_screw_"
            z_pos = assembly.toCompound().BoundingBox().zlen - 6.0

            # Do not add the leg explode Z translation to the screw explode translation
            assembly_line_length_extension = 0.0
        else:
            alignment_axis = "-Z"
            name_prefix = "base_plate_screw_"
            z_pos = 0.0

            # Add the leg explode Z translation to the screw explode translation
            assembly_line_length_extension = leg_explode_z

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
            cur_screw = Screw(name=name_prefix + str(i),
                              position=(base_plate_location[0] + x_mult * base_plate_width / 2.0 -
                                            x_mult * 10.0,
                                        base_plate_location[1] + y_mult * base_plate_height / 2.0 -
                                            y_mult * 10.0,
                                        z_pos),
                              explode_translation=(0.0, 0.0, 45.0),
                              size="M5-0.8",
                              fastener_type="iso10642",
                              axis=alignment_axis,
                              length=10)

            # Determine the assembly line length based on the existing explode translations
            assembly_line_length = (assembly_line_length_extension +
                                        cur_screw.explode_translation[2])

            assembly.add(
                cur_screw.fastener_model,
                name=cur_screw.name,
                loc=cq.Location(cur_screw.position,
                                cur_screw.rotation[0],
                                cur_screw.rotation[1]),
                color=cq.Color("gray"),
                metadata={"explode_translation": cq.Location(cur_screw.explode_translation),
                          "assembly_line_length": (0.0, 0.0, assembly_line_length)}
            )


    def add_shelf_mounting_screws(self, assembly, shelf, base_plate_width, base_plate_height):
        """
        Adds the front screws that secure the shelves to the rack.
        """
        for j in range(4):
            # Figure out what the height of the shelf is
            shelf_height = shelf["component"].toCompound().BoundingBox().zlen

            # Offset the screws to each side of the rack
            x_mult = 1
            z_offset = 0.0
            if j in [0, 1]:
                x_mult = 1

                # Change the Z-height of the screws
                if j == 0:
                    z_offset = 0.0
                else:
                    z_offset = shelf_height - 14.0
            elif j in [2, 3]:
                x_mult = -1

                # Change the Z-height of the screws
                if j == 2:
                    z_offset = 0.0
                else:
                    z_offset = shelf_height - 14.0

            # Determine how far to explode the screws
            if shelf["width_category"] == "broad":
                explode_translation = (0.0, 0.0, 45.0)
            else:
                explode_translation = (0.0, 0.0, 100.0)

            # Create a screw with the proper location, dimensions and orientation
            cur_screw = Screw(name=shelf["name"] + "_screw_" + str(j),
                            position=(x_mult * base_plate_width / 2.0 - x_mult * 10.0,
                                        -base_plate_height / 2.0 - 4.0,
                                        shelf["location"][2] + 7.0 + z_offset),
                            explode_translation=explode_translation,
                            size="M4-0.7",
                            fastener_type="iso7380_1",
                            axis="Y",
                            length=10)
            assembly.add(
                cur_screw.fastener_model,
                name=cur_screw.name,
                loc=cq.Location(cur_screw.position,
                                cur_screw.rotation[0],
                                cur_screw.rotation[1]),
                color=cq.Color("gray"),
                metadata={"explode_translation": cq.Location(cur_screw.explode_translation),
                        "assembly_line_length": explode_translation})


    def generate_assembly_process_renders(self):
        """
        Generate renders of the assembly steps.
        """

        # Allows us to collect the assembly parts for this configuration
        assembly_parts = {
            "shelves": [],
            "legs": [],
            "top_plate": {},
            "base_plate": {},
        }

        # By default, do not explode parts
        explode_location = cq.Location((0, 0, 0))

        # Create a union of _assembly_parts and _parts
        all_parts = self._parts + self._assembly_parts

        shelf_count = 1
        leg_count = 1
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
                    explode_location = cq.Location((0, 0, 75))
                else:
                    explode_location = cq.Location((0, -45.0, 0))

                # Save the information for this shelf
                assembly_parts["shelves"].append({
                    "name": "shelf_" + str(shelf_count),
                    "component_type": "shelf",
                    "component": cq_part,
                    "width_category": shelf_obj.width_category,
                    "location": part.position,
                    "color": part.color,
                    "explode_location": explode_location
                })
                shelf_count += 1
            # We have something else like a leg or plate
            else:
                cq_part = cq.importers.importStep(part.step_file)

                # Handle the top and bottom plate explode locations differently
                if "plate" in part.name and "top" in part.name:
                    explode_location = cq.Location((0, 0, 20.0))

                    # Save this as the assembly's top plate
                    assembly_parts["top_plate"] = {
                        "name": "top_plate",
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
                        "name": "base_plate",
                        "component_type": "base_plate",
                        "component": cq_part,
                        "location": part.position,
                        "color": part.color,
                        "explode_location": explode_location
                    }
                elif "leg" in part.name:
                    explode_location = cq.Location((0, 0, 20.0))

                    assembly_parts["legs"].append({
                        "name": "leg_" + str(leg_count),
                        "component_type": "leg",
                        "component": cq_part,
                        "location": part.position,
                        "color": part.color,
                        "explode_location": explode_location
                    })
                    leg_count += 1

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

        # Add the screws that hold the base on
        leg_explode_translation = assembly_parts["legs"][0]["explode_location"].toTuple()[0][2]
        self.add_end_plate_mounting_screws(assembly,
                                            base_plate_location,
                                            base_plate_width,
                                            base_plate_height,
                                            leg_explode_translation,
                                            orientation="bottom")

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
        exploded_assembly = assembly._copy()
        explode_assembly(exploded_assembly)
        render_options["explode"] = True  # Does not do anything due to technical debt in shelf.py
        render_options["annotate"] = True

        # Exploded view of this assembly step
        render_path = Path(render_destination) / "final_assembly_step_1_annotated.png"
        generate_render(model=exploded_assembly,
                        file_path=render_path,
                        render_options=render_options)

        # Reset the annotation render options
        render_options["explode"] = False
        render_options["annotate"] = False

        # Put the top-load shelves in the assembly
        for i, shelf in enumerate(assembly_parts["shelves"]):
            # See if we have a top-loading shelf
            if shelf["width_category"] == "broad":
                # Add the shelf mounting screws to the assembly
                self.add_shelf_mounting_screws(assembly,
                                               shelf,
                                               base_plate_width,
                                               base_plate_height)

                assembly.add(
                    shelf["component"],
                    name=shelf["name"],
                    loc=cq.Location(shelf["location"]),
                    color=cq.Color(shelf["color"]),
                    metadata={"explode_translation": shelf["explode_location"]}
                )

                file_name = "final_assembly_step_2_" + shelf["name"] +"_installed.png"
                render_path = Path(render_destination) / file_name
                generate_render(model=assembly,
                            file_path=render_path,
                            render_options=render_options)

                # Set up for the exploded and annotated view
                exploded_assembly = assembly._copy()

                # Allows us to make steps where previous steps are no longer exploded
                selective_list = [shelf["name"],
                                  shelf["name"] + "_screw_0",
                                  shelf["name"] + "_screw_1",
                                  shelf["name"] + "_screw_2",
                                  shelf["name"] + "_screw_3"]
                exploded_assembly = self.selective_explode(assembly=exploded_assembly,
                                                           names_to_still_explode=selective_list)

                # Explode the assembly in preparation for the next step
                explode_assembly(exploded_assembly, depth=1)
                render_options["explode"] = True  # Does nothing due to technical debt in shelf.py
                render_options["annotate"] = True

                # Exploded view of this assembly step
                file_name = "final_assembly_step_2_" + shelf["name"] + "_insertion_annotated.png"
                render_path = Path(render_destination) / file_name
                generate_render(model=exploded_assembly,
                                file_path=render_path,
                                render_options=render_options)


        # Add the top plate
        assembly.add(
            assembly_parts["top_plate"]["component"],
            name="top_plate",
            loc=cq.Location(assembly_parts["top_plate"]["location"]),
            color=cq.Color(assembly_parts["top_plate"]["color"]),
            metadata={"explode_translation": assembly_parts["top_plate"]["explode_location"]}
        )

        # Add the screws that hold the base on
        leg_explode_translation = assembly_parts["legs"][0]["explode_location"].toTuple()[0][2]
        self.add_end_plate_mounting_screws(assembly,
                                            base_plate_location,
                                            base_plate_width,
                                            base_plate_height,
                                            leg_explode_translation,
                                            orientation="top")

        # Get set up for the exploded step
        exploded_assembly = assembly._copy()
        exploded_assembly = self.selective_explode(assembly=exploded_assembly,
                                                    names_to_still_explode=["top_plate",
                                                                            "top_plate_screw_0",
                                                                            "top_plate_screw_1",
                                                                            "top_plate_screw_2",
                                                                            "top_plate_screw_3"])
        explode_assembly(exploded_assembly, depth=1)

        # Reset the annotation render options
        render_options["explode"] = False
        render_options["annotate"] = False

        # The location to put the renders in
        render_path = Path(render_destination) / "final_assembly_step_3_assembled.png"
        generate_render(model=assembly,
                        file_path=render_path,
                        render_options=render_options)

        # Set up for the exploded and annotated view
        render_options["explode"] = True  # Does not do anything due to technical debt in shelf.py
        render_options["annotate"] = True

        # Exploded view of this assembly step
        render_path = Path(render_destination) / "final_assembly_step_3_annotated.png"
        generate_render(model=exploded_assembly,
                        file_path=render_path,
                        render_options=render_options,
                        selective_list=["top_plate",
                                        "top_plate_screw_0",
                                        "top_plate_screw_1",
                                        "top_plate_screw_2",
                                        "top_plate_screw_3"])

        # Reset the annotation render options
        render_options["explode"] = False
        render_options["annotate"] = False

        # Put the top-load shelves in the assembly
        for i, shelf in enumerate(assembly_parts["shelves"]):
            # See if we have a top-loading shelf
            if shelf["width_category"] != "broad":
                # Add the shelf mounting screws to the assembly
                self.add_shelf_mounting_screws(assembly,
                                               shelf,
                                               base_plate_width,
                                               base_plate_height)

                assembly.add(
                    shelf["component"],
                    name=shelf["name"],
                    loc=cq.Location(shelf["location"]),
                    color=cq.Color(shelf["color"]),
                    metadata={"explode_translation": shelf["explode_location"]}
                )

                # Reset the annotation render options
                render_options["explode"] = False
                render_options["annotate"] = False

                file_name = "final_assembly_step_4_" + shelf["name"] +"_installed.png"
                render_path = Path(render_destination) / file_name
                generate_render(model=assembly,
                            file_path=render_path,
                            render_options=render_options)

                # Set up for the exploded and annotated view
                exploded_assembly = assembly._copy()

                # Allows us to make steps where previous steps are no longer exploded
                selective_list = [shelf["name"],
                                  shelf["name"] + "_screw_0",
                                  shelf["name"] + "_screw_1",
                                  shelf["name"] + "_screw_2",
                                  shelf["name"] + "_screw_3"]
                exploded_assembly = self.selective_explode(assembly=exploded_assembly,
                                                           names_to_still_explode=selective_list)

                # Explode the assembly in preparation for the next step
                explode_assembly(exploded_assembly, depth=1)
                render_options["explode"] = True  # Does nothing due to technical debt in shelf.py
                render_options["annotate"] = True

                # Exploded view of this assembly step
                file_name = "final_assembly_step_4_" + shelf["name"] + "_insertion_annotated.png"
                render_path = Path(render_destination) / file_name
                generate_render(model=exploded_assembly,
                                file_path=render_path,
                                render_options=render_options,
                                selective_list=selective_list)


    def selective_explode(self, assembly=None, names_to_still_explode=None):
        """
        Allows us to do assembly steps by keeping previous exploded parts together.
        """
        # Make sure that the already-assembled parts of the rack do not explode
        for part in assembly.children:
            if part.name not in names_to_still_explode:
                part.metadata["explode_translation"] = cq.Location((0, 0, 0))

        return assembly


# Handle different execution environments, including ExSource-Tools
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    def_file = Path(assembly_definition_file)
    folder = def_file.resolve().parent
    os.chdir(folder)
    # CQGI should execute this whenever called
    assembly = AssemblyRenderer(def_file.name).generate()
    AssemblyRenderer(def_file.name).generate_assembly_process_renders()

    show_object(assembly)
