
from nimble_orchestration.yaml_cleaner import YamlCleaner

import yaml
import pathlib


class AssemblyDefGenerator:
    """
    Generate the assembly definition file.
    """

    def __init__(self):
        self._parts = []


    def add_part(self, name: str, step_file: str, position, assembly_step: str | None = None):
        """
        Add a part to the assembly definition file.
        """
        part = {
            "name": name,
            "step-file": step_file,
            "position": position,
            "assembly-step": assembly_step
        }
        self._parts.append(part)

    def get_step_files(self) -> list:
        """
        Get a list of all step files.
        """
        return [part["step-file"] for part in self._parts]

    def save(self, output_file: str | pathlib.Path):
        """
        Save the assembly definition file.
        """
        data = {
            "assembly": {
                "parts": self._parts
            }
        }
        with open(output_file, "w") as f:
            yaml.dump(YamlCleaner.clean(data), f, sort_keys=False)
