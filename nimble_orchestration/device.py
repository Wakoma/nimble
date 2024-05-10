
class Device:
    """
    Represents a device from the devices.json file

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

    def __init__(self, jsonNode):
        self.id = jsonNode['ID']
        # self.name = jsonNode['Name']
        self.name = jsonNode['Hardware']
        # self.category = jsonNode['Category']
        self.category = jsonNode['Type']
        self.height_in_units = int(jsonNode['HeightUnits'])
        # self.width = jsonNode['Width']
        self.width = jsonNode['LengthMm']
        self.depth = jsonNode['Depth']
        self.shelf_id = jsonNode['ShelfId']
        # self.tray_type = jsonNode['TrayType']
        self.shelf_type = jsonNode['Shelf']

    def get_tray_id(self):
        return f"tray_h{self.height_in_units}_t{self.shelf_type.lower().replace(' ', '_')}"