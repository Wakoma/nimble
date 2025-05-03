

"""
This module provides many different nimble shelves created using
the nimble_build_system.cad ShelfBuilder.
"""


import cadscript as cad

from nimble_build_system.cad.shelf import create_shelf_for_x

# parameters to be set in exsource-def.yaml file

# shelf types
# "generic"                 - a generic cable tie shelf
# "stuff"                   - for general stuff such as wires. No access to the front
# "stuff-thin"              - a thin version of above
# "nuc"                     - for Intel NUC
# "usw-flex"                - for Ubiquiti USW-Flex
# "usw-flex-mini"           - for Ubiquiti Flex Mini
# "anker-powerport5"        - for Anker PowerPort 5
# "anker-a2123"             - for Anker 360 Charger 60W (a2123)
# "anker-atom3slim"         - for Anker PowerPort Atom III Slim (AK-194644090180)
# "hdd35"                   - for 3.5" HDD
# "dual-ssd"                - for 2x 2.5" SSD
# "raspi"                   - for Raspberry Pi



# For development purposes if there is not a device in the devices database
# with the paramters you want set the device id to "dummy-<shelf type>-<h>u"
# for example "dummy-dual-ssd-4u"
#
# You can also pass a dictionary of device data to the `dummy_device_data`
# keyword argument of `create_shelf_for` if you need other device data to be
# set.

device_id = "dummy-raspi-2u"


def create_6in_shelf(device_id) -> cad.Body:
    """
    This is the top level function called when the script
    is called. It uses the `shelf_type` string to decide
    which of the defined shelf functions to call.
    """

    shelf_obj = create_shelf_for_x(device_id)
    return shelf_obj.generate_shelf_model()


if __name__ == "__main__" or __name__ == "__cqgi__" or "show_object" in globals():
    result = create_6in_shelf(device_id)
    cad.show(result)  # when run in cq-cli, will return result
