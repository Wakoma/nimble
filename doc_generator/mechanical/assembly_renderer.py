"""
cadquery module that takes an assembly-def.yaml file and generate an assembly from it.

The assembly-def.yaml file is a yaml file that contains a list of parts and their positions in the assembly.
Example file:
assembly:
  parts:
  - name: baseplate
    step-file: ./step/baseplate.step
    position: (0, 0, 0)
    assembly-step: '1'
  - name: rack_leg1
    step-file: ./step/beam.step
    position: (-67.5, -67.5, 3)
    assembly-step: '2'

"""
# parameters
# can be set in exsource-def.yaml file
assembly_definition_file = "assembly-def.yaml"

import os
from pathlib import Path
import cadquery as cq
import yaml


class PartDefinition:
    """
    Definition of a part.
    """

    name: str
    step_file: str
    position: tuple
    assembly_step: str
    tags: list

    def __init__(self, definition: dict):
        self.name = definition["name"]
        self.step_file = definition["step-file"]
        # convert position from string like "(1,2,3)" to tuple
        self.position = tuple(map(float, definition["position"].strip("()").split(",")))
        self.assembly_step = definition["assembly-step"]
        self.tags = definition.get("tags", [])


class AssemblyRederer:
    """
    create a cq assembly from an assembly definition file.
    """

    _parts: list[PartDefinition] = []


    def __init__(self, assembly_def_file: str):

        with open(assembly_def_file, "r") as f:
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
            assembly.add(cq_part, name=part.name, loc=cq.Location(part.position))

        return assembly


# Handle different execution environments, including ExSource-Tools
if "show_object" in globals() or __name__ == "__cqgi__":
    # CQGI should execute this whenever called
    assembly = AssemblyRederer(assembly_definition_file).generate()
    show_object(assembly)

if __name__ == "__main__":
    # for debugging
    folder = (Path(__file__).resolve().parent.parent)
    os.chdir(folder)
    assembly = AssemblyRederer("assembly-def.yaml").generate()
    assembly.save("assembly.stl", "STL")
