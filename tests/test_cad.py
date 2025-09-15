import pytest
from nimble_build_system.cad.shelf import RaspberryPiShelf
from nimble_build_system.orchestration.configuration import NimbleConfiguration

def test_shelf_generation():
    """
    Tests whether or not the functionality for a Raspberry Pi shelf is working as expected.
    This tests all of the CAD related functionality related to the Raspberry Pi shelf.
    """

    # This is a list of the shelf models that have potential red flags.
    # In the cases where the depth seems small compared to the device, it
    # seems to be related to the generic/zip-tie shelf. This needs more
    # investigation.
    broken_shelves = []
    broken_shelves.append("mANTBox_2_12s")  # Shelf depth seems very small compared to the device
    broken_shelves.append("mANTBox_ax_15s")  # Missing height in units
    broken_shelves.append("NetBox_5_ax")  # Missing height in units
    broken_shelves.append("OmniTIK_5")  # Shelf depth seems very small compared to the device
    broken_shelves.append("OmniTIK_5_ac")  # Shelf depth seems very small compared to the device
    broken_shelves.append("OmniTIK_5_PoE_ac")  # Shelf depth seems very small compared to the device
    broken_shelves.append("AC_Lite")  # Missing device dimensions
    broken_shelves.append("AC_Mesh_Pro")  # Shelf depth seems very small compared to the device
    broken_shelves.append("AC_Pro")  # Missing device dimensions
    broken_shelves.append("U6_Lite")  # Missing device dimensions
    broken_shelves.append("U6_Long_Range")  # Missing device dimensions
    broken_shelves.append("U6_Mesh")  # Missing device dimensions
    broken_shelves.append("U6_Pro")  # Missing device dimensions
    broken_shelves.append("U6+")  # Missing device dimensions
    broken_shelves.append("UniFi_AC_Mesh")  # Shelf depth seems very small compared to the device
    broken_shelves.append("hAP_ac")  # Shelf depth seems smaller than the device
    broken_shelves.append("hAP_lite")  # Missing device dimensions
    broken_shelves.append("RB951Ui-2HnD")  # Shelf depth seems smaller than the device
    broken_shelves.append("Hex_PoE")  # Shelf depth seems smaller than the device
    broken_shelves.append("L009UiGS-RM")  # Missing height in units
    broken_shelves.append("RB4011iGS+RM")  # Shelf depth seems smaller than the device
    broken_shelves.append("RB5009UG+S+IN")  # Missing height in units
    broken_shelves.append("RB5009UPr+S+IN")  # Missing height in units
    broken_shelves.append("EQ12_N100")  # Missing height in units
    broken_shelves.append("SEi10_1035G7")  # Shelf depth seems smaller than the device
    broken_shelves.append("SEi12_i7-12650H")  # Missing height in units
    broken_shelves.append("SER5_PRO_5700U")  # Missing height in units
    broken_shelves.append("Gigabyte_Brix_GB-BEi5-1240_(rev._1.0)")  # Shelf depth seems smaller than the device
    broken_shelves.append("Gigabyte_Brix_GB-BRi5-10210(E)")  # Shelf depth seems smaller than the device
    broken_shelves.append("Gigabyte_Brix_GB-BRi5H-10210(E)")  # Shelf depth seems smaller than the device
    broken_shelves.append("Gigabyte_Brix_GB-BRi5HS-1335")  # Shelf depth seems smaller than the device
    broken_shelves.append("Gigabyte_Brix_GB-BSi5-1135G7_(rev._1.0)")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCenter_M700")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCentre_M70q")  # Missing height in units
    broken_shelves.append("ThinkCentre_M70s")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCentre_M75s")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCentre_M80s")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCentre_M90q")  # Shelf depth seems smaller than the device
    broken_shelves.append("ThinkCentre_M90s") # Shelf depth seems smaller than the device
    broken_shelves.append("CRS106-1C-5S")  # Shelf depth seems smaller than the device
    broken_shelves.append("CRS112-8G-4S-IN")  # Shelf depth seems smaller than the device
    broken_shelves.append("CRS112-8P-4S-IN")  # Shelf depth seems smaller than the device
    broken_shelves.append("CRS305-1G-4S+IN")  # Shelf depth is the same as the device depth, which seems too tight
    broken_shelves.append("CRS310-1G-5S-4S+IN")  # Shelf depth seems smaller than the device
    broken_shelves.append("CRS310-8G+2S+IN")  # Shelf depth seems smaller than the device
    broken_shelves.append("CSS610-8G-2S+IN")  # Shelf depth seems smaller than the device
    broken_shelves.append("RB260GS")  # Shelf depth seems smaller than the device
    broken_shelves.append("RB260GSP")  # Shelf depth seems smaller than the device
    broken_shelves.append("Enterprise_8_PoE")  # Shelf depth seems smaller than the device
    broken_shelves.append("Lite_16_PoE")  # Shelf depth seems smaller than the device
    broken_shelves.append("Pro_8_PoE")  # Shelf depth seems smaller than the device
    broken_shelves.append("UniFi_8_PoE_(Gen1)") 
    broken_shelves.append("SEi12_i5-12450H")
    broken_shelves.append("SER5_MAX_5800H")

    # The configuration of hardware/shelves that we want to test against
    test_config = ["Raspberry_Pi_4B",
                   "Raspberry_Pi_5",
                   "hAP",
                   "hAP_ac_lite",
                   "Hex",
                   "hEX_PoE_lite",
                   "hEX_S",
                   "NUC10FNK",
                   "NUC10i5FNH",
                   "NUC8I5BEH",
                   "NUC8i5BEK",
                   "Unifi_Flex_Mini",
                   "Unifi_Switch_Flex"
                ]

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Make sure that each shelf can generate the proper files
    for i, shelf in enumerate(config._shelves):
        # Find the matching device for the shelf
        device = shelf.device

        # Instantiate the shelf object and check to make sure it has a valid name
        shelf = RaspberryPiShelf(device,
                                 assembly_key=f"shelf_{i}",
                                 position=(1.0, 0.0, 12.0),
                                 color='deepskyblue1',
                                 rack_params=config._rack_params)
        assert shelf.name.lower().startswith(test_config[i].lower().split("_")[0])

        # Check that the device model was generated with the proper dimensions per the configuration
        device_model = shelf.generate_device_model()

        # Account for the custom model model for the Raspberry Pi 4B
        if "raspberry" in device.name.lower():
            assert device.width == pytest.approx(85.0, 0.001)
            assert device.depth == pytest.approx(56.0, 0.001)
            assert device.height == pytest.approx(17.0, 0.001)
        else:
            x_size = device_model.val().BoundingBox().xmax - device_model.val().BoundingBox().xmin
            y_size = device_model.val().BoundingBox().ymax - device_model.val().BoundingBox().ymin
            z_size = device_model.val().BoundingBox().zmax - device_model.val().BoundingBox().zmin
            assert x_size == pytest.approx(config.devices[i].width, 0.001)
            assert y_size == pytest.approx(config.devices[i].depth, 0.001)
            assert z_size == pytest.approx(config.devices[i].height, 0.001)

        # Make sure the shelf model is valid and has generally the correct dimensions
        shelf_model = shelf.generate_shelf_model().cq()
        x_size = shelf_model.val().BoundingBox().xmax - shelf_model.val().BoundingBox().xmin
        y_size = shelf_model.val().BoundingBox().ymax - shelf_model.val().BoundingBox().ymin
        z_size = shelf_model.val().BoundingBox().zmax - shelf_model.val().BoundingBox().zmin

        assert shelf_model.val().isValid()
        assert x_size > config.devices[i].width
        assert y_size > config.devices[i].depth
        assert z_size > config.devices[i].height


def test_shelf_assembly_generation():
    """
    Tests whether or not the assembly is valid and all the components are present and in the correct
    locations and orientations.
    """

    # The configuration of hardware/shelves that we want to test against
    test_config = ["Raspberry_Pi_4B"]

    # Load the needed information to generate a Shelf object
    config = NimbleConfiguration(test_config)

    # Get the only shelf that we should have to deal with
    rpi_shelf = config._shelves[0]

    assert rpi_shelf != None

    # Test the generated CAD assembly
    assy = rpi_shelf.generate_assembly_model(rpi_shelf.renders["assembled"]["render_options"])

    # Make sure the assembly has the number of children we expect
    assert len(assy.children) == 6

    # Make sure that the assembly has no parts that are interfering with each other
    intersection_part = assy.objects["shelf"].shapes[0]
    intersection_part = intersection_part.intersect(assy.objects["device"].shapes[0])
    assert intersection_part.Volume() == pytest.approx(0.0, 0.001)

    # Test exploded assembly
    exploded_assy = rpi_shelf.generate_assembly_model(
                                    rpi_shelf.renders["annotated"]["render_options"])

    # Make sure the assembly has the number of children we expect
    assert len(assy.children) == 6
