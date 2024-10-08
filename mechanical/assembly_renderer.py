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

assembly_definition_file = "assembly-def.yaml"

class PartDefinition:
    """
    Definition of a part.
    """

    name: str
    step_file: str
    position: tuple
    tags: list

    def __init__(self, definition: dict):
        self.name = definition["key"]
        self.step_file = definition["step-file"]
        # convert position from string like "(1,2,3)" to tuple
        self.position = tuple(map(float, definition["position"].strip("()").split(",")))
        self.tags = definition.get("tags", [])
        self.color = definition.get("color", "gray95")


class AssemblyRenderer:
    """
    create a cq assembly from an assembly definition file.
    """

    _parts: list[PartDefinition] = []


    def __init__(self, assembly_def_file: str):

        with open(assembly_def_file, "r", encoding="utf-8") as f:
            assembly_def = yaml.load(f, Loader=yaml.FullLoader)
            for part_def in assembly_def["assembly"]["parts"]:
                self._parts.append(PartDefinition(part_def))



    def generate(self) -> cq.Assembly:
        """
        Generate the assembly.
        """
        assembly = cq.Assembly()
        for part in self._parts:
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


# Handle different execution environments, including ExSource-Tools
if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    # CQGI should execute this whenever called
    assembly = AssemblyRenderer(assembly_definition_file).generate()
    show_object(assembly)

if __name__ == "__main__":
    # for debugging
    folder = Path(__file__).resolve().parent.parent
    os.chdir(folder)
    assembly = AssemblyRenderer(assembly_definition_file).generate()
    assembly.save("assembly.stl", "STL")
