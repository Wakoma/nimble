"""
Contains an object that represents the information of a device in the devices.json file.
"""

import re
import os
import json
from math import ceil
from nimble_build_system.orchestration.paths import MODULE_PATH


def load_device_data():
    devices_filename = os.path.join(MODULE_PATH, "devices.json")
    with open(devices_filename, encoding="utf-8") as devices_file:
        all_devices = json.load(devices_file)

    return all_devices

ALL_DEVICES = load_device_data()
ALL_DEVICE_IDS = [x['ID'] for x in ALL_DEVICES]

def find_device(this_device_id):
    if this_device_id in ALL_DEVICE_IDS:
        return ALL_DEVICES[ALL_DEVICE_IDS.index(this_device_id)]
    else:
        raise ValueError(f'No device of ID "{this_device_id}" known')


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

    def __init__(self, device_id, rack_params):

        json_node = find_device(device_id)

        self.id = json_node['ID']
        # self.name = json_node['Name']
        self.name = json_node['Hardware']
        # self.category = json_node['Category']
        self.category = json_node['Type']
        self.width = get_length_from_str(json_node['LengthMm'])
        self.depth = get_length_from_str(json_node['Depth'])
        self.height = get_length_from_str(json_node['Height'])

        try:
            self.height_in_u = int(json_node['HeightUnits'])
        except ValueError as exc:
            if self.height:
                self.height_in_u = ceil((self.height+4)/rack_params.mounting_hole_spacing)
            else:
                raise RuntimeError("Not enough information provided to generate shelf height") from exc

        self.shelf_id = json_node['ShelfId']
        self.shelf_type = json_node['Shelf']

    @property
    def shelf_key(self):
        """
        Return an key to identify the shelf.
        """
        #TODO shelf keys are not unique as the the same shelf_type generate different
        #shelves for some hardware.
        def clean_name(name):
            name = name.lower()
            name = name.replace(' ', '_')
            unsafe_char = re.findall(r'[a-zA-Z0-9-_]', name)
            for char in set(unsafe_char):
                name.replace(char, '')
            return name
        return f"shelf_h{self.height_in_u}_--{clean_name(self.shelf_type)}"

    @property
    def shelf_builder_id(self):
        """
        shelf_builder and devices.json don't use the same ids. devices.json seems
        to use similar terms but appends -6 as the shelf is 6 inch, and optionally -s
        and -t for tall and short versions.
        These should be unified later
        """
        if self.shelf_id:
            if match := re.match(r'^(.*)-6(?:-[st])?$', self.shelf_id):
                #strip of -6 and optionally -s or -t
                return match.group(1)
        return "generic"

def get_length_from_str(length):
    """
    Return the length in mm for a given string should be formatted as
    "12.345 mm"
    """
    if match := re.match(r'^([0-9]+(?:\.[0-9]+)?) ?mm$', length):
        return float(match[1])
    return None
