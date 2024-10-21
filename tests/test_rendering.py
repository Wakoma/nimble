import tempfile
import os
import pytest
import cadquery as cq
from nimble_build_system.cad.shelf import RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration


# The configuration of hardware/shelves that we want to test against
test_config = ["Raspberry_Pi_4B",
                "NUC8I5BEH",
                "Unifi_Flex_Mini",
                "Unifi_Switch_Flex",
                "Hex",
                # "Western_Digital_Red_HDD"
                # "Western_Digital_Blue_SSD"
            ]


def test_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for an entire assembly.
    """

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Get the only shelf that we should have to deal with
    cur_shelf = config.shelves[0]

    # Test the generated CAD assembly
    shelf_assy = cur_shelf.generate_assembly_model()

    # Set up a temporary path to export the image to
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "assembly_render_test.png")

    # Do a sample render of the shelf assembly
    cur_shelf.get_render(shelf_assy,
                         file_path=temp_path)

    assert os.path.isfile(temp_path)


def test_annotated_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for an entire assembly with
    annotations (i.e. assembly lines).
    """

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Get the only shelf that we should have to deal with
    cur_shelf = config.shelves[0]

    # Test the generated CAD assembly
    shelf_assy = cur_shelf.generate_assembly_model(explode=True)

    # Set up a temporary path to export the image to
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "assembly_render_test_exploded.png")

    # Do a sample render of the shelf assembly
    cur_shelf.get_render(shelf_assy,
                         file_path=temp_path,
                         annotate=True)

    assert os.path.isfile(temp_path)
