import tempfile
import os
from pathlib import Path
import pytest
import cadquery as cq
from nimble_build_system.cad.shelf import RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration
from mechanical.assembly_renderer import AssemblyRenderer


# The configuration of hardware/shelves that we want to test against
test_config = ["Raspberry_Pi_4B",
                "NUC8I5BEH",
                "Unifi_Flex_Mini",
                "Unifi_Switch_Flex",
                "Hex",
                "Western_Digital_Red_HDD",
                "Western_Digital_Blue_SSD"
            ]


def test_png_rendering():
    """
    Tests whether or not a PNG image can be output for each render of a shelf assembly.
    """
     # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Check all of the shelf assemblies
    for cur_shelf in config._shelves:

        # Set up a temporary path to export the image to that we can upload artifacts from
        temp_dir = "./renders"

        # Do a sample render of the shelf assembly
        cur_shelf.generate_renders(temp_dir)

        # Check to make sure that all of the appropriate files were created
        for render_file in cur_shelf.list_render_files():
            assert os.path.isfile(os.path.join(temp_dir, render_file))


def test_final_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for each assembly step of a rack.
    """
    # Load the definition file and instantiate the AssemblyRenderer object
    assembly_definition_file = "build/assembly-def.yaml"
    def_file = Path(assembly_definition_file)
    folder = def_file.resolve().parent
    os.chdir(folder)
    assembly = AssemblyRenderer(def_file.name)

    # Generate the assembly process renders
    assembly.generate_assembly_process_renders()
