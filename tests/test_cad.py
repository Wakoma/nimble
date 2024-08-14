import pytest
from nimble_build_system.cad.shelf import Shelf, RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration

def test_generating_raspberry_pi_shelf():
    """
    Tests whether or not the functionality for a Raspberry Pi shelf is working as expected.
    This tests all of the CAD related functionality related to the Raspberry Pi shelf.
    """

    # The configuration of hardware/shelves that we want to test against
    test_config = ["Raspberry_Pi_4B"]

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Make sure that each shelf can generate the proper files
    for i, shelf in enumerate(config.shelves):
        # Find the matching device for the shelf
        device = config.devices[i]

        # Generate the right type of shelf based on the name
        if "raspberry" in shelf.name.lower():
            shelf = RaspberryPiShelf(shelf, device)
            assert shelf.name == "Raspberry Pi 4B shelf"
