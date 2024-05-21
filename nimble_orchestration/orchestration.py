"""
This orchestration moule contains the main runner class `OrchestrationRunner`.
This should be used to execute the orchestration script to generate models
and assemblies.
To generate for a sepcific nimble configuration see the `cofiguration` module
To generate from a list of components see the `components` module
"""

import os
import shutil

import exsource_tools
import exsource_tools.cli
import exsource_tools.tools

from nimble_orchestration.exsource_def_generator import ExsourceDefGenerator
from nimble_orchestration.paths import BUILD_DIR, REL_MECH_DIR, DOCS_DIR, DOCS_TMP_DIR

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
        """
        A bit of a mish mash of a method that saves the assembly definition
        file, then creates an exsource for a model of the final assembly, finally
        running exsource.
        This does not create renders of the assembly steps
        """
        # save assembly definition
        assembly_definition.save(os.path.join(BUILD_DIR, "assembly-def.yaml"))

        # add assembly to exsource
        exsource = ExsourceDefGenerator()
        exsource_path = os.path.join(BUILD_DIR, "assembly-exsource-def.yaml")
        exsource.add_part(
            key="assembly",
            name="assembly",
            description="assembly",
            output_files=[
                "./assembly/assembly.stl",
                "./assembly/assembly.step",
                "./assembly/assembly.glb",
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

    def generate_docs(self, configuration):
        """
        Run GitBuilding to generate documentation
        """
        if os.path.exists(DOCS_TMP_DIR):
            shutil.rmtree(DOCS_TMP_DIR)
        shutil.copytree(DOCS_DIR, DOCS_TMP_DIR)

        for shelf in configuration.shelves:
            filename = os.path.join(DOCS_TMP_DIR, f"{shelf.device.id}_shelf.md")
            with open(filename, 'w', encoding="utf-8") as gb_file:
                gb_file.write(shelf.md)

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
