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
                "Hex"
            ]


def test_png_rendering():
    """
    Tests whether or not a PNG image can be output for each render of a shelf assembly.
    """
     # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Check all of the shelf assemblies
    for cur_shelf in config._shelves:
        # Create the temporary directory if it does not exist
        temp_dir = os.path.join(Path(os.curdir).resolve().parent, "renders")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Do a sample render of the shelf assembly
        cur_shelf.generate_renders(temp_dir)

        # Check to make sure that all of the appropriate files were created
        for render_file in cur_shelf.list_render_files():
            assert os.path.isfile(os.path.join(temp_dir, render_file))


def test_final_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for each assembly step of a rack.
    """

    # Run the generate command to create the build
    import subprocess
    subprocess.run(["gen_nimble_conf_options"])
    subprocess.run(["cadorchestrator",
                    "generate",
                    '{"device-ids": ["Raspberry_Pi_4B", "NUC10i5FNH", "Raspberry_Pi_4B"]}'])

    # Load the definition file and instantiate the AssemblyRenderer object
    assembly_definition_file = "build/assembly-def.yaml"
    def_file = Path(assembly_definition_file)
    folder = def_file.resolve().parent
    os.chdir(folder)
    assembly = AssemblyRenderer(def_file.name)

    # Create the temporary directory if it does not exist
    temp_dir = os.path.join(Path(os.curdir).resolve().parent, "renders")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Generate the assembly process renders
    assembly.generate_assembly_process_renders()

    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_base_and_legs_annotated.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_base_and_legs_assembled.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_broad_shelves_shelf_2_insertion_annotated.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_broad_shelves_shelf_2_installed.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_topplate_annotated.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_topplate_assembled.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_standard_shelves_shelf_1_insertion_annotated.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_standard_shelves_shelf_1_installed.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_standard_shelves_shelf_3_insertion_annotated.png")
    )
    assert os.path.isfile(os.path.join(
        temp_dir,
        "final_assembly_standard_shelves_shelf_3_installed.png")
    )
