
class Device:
    """
    Represents a device from the devices.json file

    Example node:
      {
        "ID": "NetgateSG1100",
        "Name": "Netgate SG-1100",
        "Category": "Firewall",
        "HeightInUnits": 2,
        "Width": "Standard",
        "TrayType": "Open"
      },
    """

    def __init__(self, jsonNode):
        self.id = jsonNode['ID']
        self.name = jsonNode['Name']
        self.category = jsonNode['Category']
        self.height_in_units = jsonNode['HeightInUnits']
        self.width = jsonNode['Width']
        self.tray_type = jsonNode['TrayType']

    def get_tray_id(self):
        return f"tray_h{self.height_in_units}_t{self.tray_type}"
