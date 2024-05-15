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
                 key: str,
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
        if key in self._parts:
            print(f"Part with id: {key} already specified in exsource. Skipping!")
        self._parts[key] = part


    def save(self, output_file: str | pathlib.Path):
        """
        Save the exsource definition file.
        """
        data = {
            "exports": self._parts
        }
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(YamlCleaner.clean(data), f, sort_keys=False)
