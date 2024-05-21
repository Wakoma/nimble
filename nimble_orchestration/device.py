"""
Contains an object that represents the information of a device in the devices.json file.
"""

import re

class Device:
    """
    Represents a subset of the information for a device from the devices.json file

    Example node:
      {
        "ID": "mantbox_2_12smantbox_2_12s",
        "Type": "Access Point",
        "Hardware": "mANTBox 2 12s",
        "Brand": "MikroTik",
        "Model": "mANTBox 2 12s",
        "Shelf": "No shelf needed",
        "Rack": "None",
        "ShelfId": "",
        "HeightUnits": "",
        "LengthMm": "140.00 mm",
        "Depth": "348.00 mm",
        "Height": "82.00 mm",
        "PoEIn": "Passive PoE",
        "PoEOut": "",
        "WattageMax": "11.0 W",
        "EstCostUsd": "$125.00",
        "ProductWebsiteUsd": "https://mikrotik.com/product/mantbox_2_12s",
        "ProductWebsiteEur": "",
        "RAM": "",
        "Field19": "",
        "PoEInInputVoltage": "10-28 V",
        "Voltage": "",
        "Amperage": "",
        "WRTVersion": "",
        "OpenWRTLink": "",
        "Comments": ""
      }
    """

    def __init__(self, json_node):
        self.id = json_node['ID']
        # self.name = json_node['Name']
        self.name = json_node['Hardware']
        # self.category = json_node['Category']
        self.category = json_node['Type']
        self.height_in_u = int(json_node['HeightUnits'])
        # self.width = json_node['Width']
        self.width = json_node['LengthMm']
        self.depth = json_node['Depth']
        self.shelf_id = json_node['ShelfId']
        self.shelf_type = json_node['Shelf']

    @property
    def shelf_key(self):
        """
        Return an key to identify the shelf.
        """
        return f"shelf_h{self.height_in_u}_t{self.shelf_type.lower().replace(' ', '_')}"

    @property
    def shelf_builder_id(self):
        """
        shelf_builder and devices.json don't key use the same ids. devices.json seems
        to use similar terms but appends -6 as the shelf is 6 inch, and optionally -s
        and -t for tall and short versions.
        These should be unified later
        """
        if self.shelf_id:
            if match := re.match(r'^(.*)-6(?:-[st])?$', self.shelf_id):
                #strip of -6 and optionally -s or -t
                return match.group(1)
        return "generic"
