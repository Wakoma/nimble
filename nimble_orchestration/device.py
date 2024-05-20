"""
Contains an object that represents the information of a device in the devices.json file.
"""

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
        # self.tray_type = json_node['TrayType']
        self.shelf_type = json_node['Shelf']

    @property
    def tray_id(self):
        """
        Return an identification for the shelf.
        """
        return f"tray_h{self.height_in_u}_t{self.shelf_type.lower().replace(' ', '_')}"
