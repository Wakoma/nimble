"""
Helper class for generating the exsource definition file.
Structure is like this:

exports:
    hull:
        name: hull
        description: >
            Main hull of the AUV, made from aluminum tubing.
        output-files:
            - ./docs/manufacturing_files/generated/hull_right_side_view.dxf
        source-files:
            - ./mech/components/auv_hull.py
        parameters:
            hull_diameter: 88.9
            hull_wall_thickness: 3.0
            hull_length: 520.0
        application: cadquery
    assembly:
        name: assembly
        description: >
            Entire AUV assembly
        output-files:
            - ./docs/images/generated/baby_auv_assembly.gltf
        source-files:
            - ./mech/baby_auv.py
        parameters:
            use_conductivity_sensor: True  # Needs to be global
            hull_length: 520.0  # mm - Needs to be global
            exploded: False
        application: cadquery
        app-options:
            - --hardwarnings
        dependencies:
            - ./mech/components/auv_hull.step
            - ./mech/components/auv_hull.step
        

"""
import pathlib
import yaml

from nimble_orchestration.yaml_cleaner import YamlCleaner


class ExsourceDefGenerator:
    """
    Generate the exsource definition file.
    """

    def __init__(self) -> None:
        self._parts = {}

    def add_part(self,
                 name: str,
                 description: str,
                 output_files: list,
                 source_files: list,
                 parameters: dict,
                 application: str,
                 dependencies: list | None = None):
        """
        Add a part to the exsource definition file.
        """
        part = {
            "name": name,
            "description": description,
            "output-files": output_files,
            "source-files": source_files,
            "parameters": parameters,
            "application": application,
            "dependencies": dependencies
        }
        if name in self._parts:
            print(f"Part named: {name} already specified in exsource. Skipping!")
        self._parts[name] = part

    def get_part_names(self) -> list:
        """
        Get a list of all part names.
        """
        return [part["name"] for part in self._parts]

    def get_part_step_file(self, part_name: str) -> str | None:
        """
        Get the step file for a part.
        """
        part = self._parts[part_name]
        outfiles = part["output-files"]
        if len(outfiles) == 1:
            return outfiles[0]
        if len(outfiles) == 0:
            raise ValueError(f"Part {part_name} has no output files.")
        for outfile in outfiles:
            if outfile.endswith(".step"):
                return outfile
        raise ValueError(f"Part {part_name} has no step file.")

    def save(self, output_file: str | pathlib.Path):
        """
        Save the exsource definition file.
        """
        data = {
            "exports": self._parts
        }
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(YamlCleaner.clean(data), f, sort_keys=False)
