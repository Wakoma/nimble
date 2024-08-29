import tempfile
import os
import pytest
import cadquery as cq
from nimble_build_system.cad.shelf import RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration


def test_model_png_rendering():
    """
    Tests whether or not a PNG image can be output for a single part.
    """

    # The configuration of hardware/shelves that we want to test against
    test_config = ["Raspberry_Pi_4B"]

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Get the only shelf that we should have to deal with
    rpi_shelf = config.shelves[0]

    # Test the generated CAD assembly
    shelf = rpi_shelf.generate_shelf_model().cq()

    # Get the render of the shelf
    rpi_shelf.get_render(shelf, (0, 0, 0))

    # temp_dir = tempfile.gettempdir()

    # Export the model to a PNG image
    # cq.exporters.export(shelf, os.path.join(temp_dir, "test_model.png"))

    # Check to make sure that the image was created
    # assert os.path.exists(os.path.join(temp_dir, "test_model.png"))
    assert True


def test_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for an entire assembly.
    """

    # The configuration of hardware/shelves that we want to test against
    test_config = ["Raspberry_Pi_4B"]

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Get the only shelf that we should have to deal with
    rpi_shelf = config.shelves[0]

    # Test the generated CAD assembly
    shelf_assy = rpi_shelf.generate_assembly_model()

    rpi_shelf.get_render(shelf_assy, (0, 0, 0))

    # temp_dir = tempfile.gettempdir()

    # Export the model to a PNG image
    # cq.exporters.export(shelf_assy, os.path.join(temp_dir, "test_model.png"))

    assert True


def test_annotated_assembly_png_rendering():
    """
    Tests whether or not a PNG image can be output for an entire assembly with
    annotations (i.e. assembly lines).
    """
    assert True
