import pytest
from nimble_build_system.cad.shelf import RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration

def test_generating_raspberry_pi_shelf():
    """
    Tests whether or not the functionality for a Raspberry Pi shelf is working as expected.
    This tests all of the CAD related functionality related to the Raspberry Pi shelf.
    """

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(["Raspberry_Pi_4B"])
    device = config.devices[0]
    shelf = config.shelves[0]

    shelf = RaspberryPiShelf(shelf, device)

    assert shelf.name == "Raspberry Pi 4B shelf"
