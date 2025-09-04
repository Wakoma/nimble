"""
Contains an object that represents the information of a device in the devices.json file.
"""

import re
import os
import json
from math import ceil
from nimble_build_system.orchestration.paths import MODULE_PATH


def load_device_data():
    """Function reads and returns list of all devices in devices.json file"""
    devices_filename = os.path.join(MODULE_PATH,"devices.json")
    with open(devices_filename, encoding="utf-8") as devices_file:
        all_devices = json.load(devices_file)

    return all_devices

ALL_DEVICES = load_device_data()
ALL_DEVICE_IDS = [x['ID'] for x in ALL_DEVICES]

def find_device(this_device_id):
    """Function returns device index for device ID in ALL_DEVICES list."""
    if this_device_id in ALL_DEVICE_IDS:
        return ALL_DEVICES[ALL_DEVICE_IDS.index(this_device_id)]

    raise ValueError(f'No device of ID "{this_device_id}" known')


class Device: # pylint: disable=too-many-instance-attributes
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

    def __init__(self, device_id, rack_params, dummy=False, dummy_data:dict|None=None):

        self.dummy = dummy
        if not dummy:
            device_dict = find_device(device_id)
        else:
            device_dict = generate_dummy_device_dict(device_id, dummy_data)

        self.id = device_dict['ID']
        # self.name = device_dict['Name']
        self.name = device_dict['Hardware']
        # self.category = device_dict['Category']
        self.category = device_dict['Type']
        self.width = get_length_from_str(device_dict['LengthMm'])
        self.depth = get_length_from_str(device_dict['Depth'])
        self.height = get_length_from_str(device_dict['Height'])

        try:
            self.height_in_u = int(device_dict['HeightUnits'])
        except ValueError as exc:
            if self.height:
                self.height_in_u = ceil((self.height+4)/rack_params.mounting_hole_spacing)
            else:
                raise RuntimeError("Not enough information provided to generate shelf height")\
                    from exc

        self.shelf_id = device_dict['ShelfId']
        self.shelf_type = device_dict['Shelf']

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
            unsafe_char = re.findall(r'[^a-zA-Z0-9-_]', name)
            for char in set(unsafe_char):
                name = name.replace(char, '')
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

def generate_dummy_device_dict(device_id:str, dummy_data:dict|None=None):
    """
    Create a dummy database record from a device id. If id is in the pattern
    `dummy-<type>-<h>u` then the shelf type and height in u are set from this.
    All device dictionary items that are used in the Device class can be set
    by entering the desired key and value in the dummy_data parameter
    """
    if dummy_data is None:
        dummy_data = {}

    device_dict = {'ID': device_id}

    if match := re.match(r'^dummy-(.+)-([0-9])+u$', device_id):
        default_shelf_id = match[1]+'-6'
        default_height_in_u = match[2]
    else:
        print(f"dummy device string `{device_id}` doesn't match pattern "
              "`dummy-<type>-<h>u` shelf type and height in u may not have "
              "been set as intended")
        default_shelf_id = "generic"
        default_height_in_u = "2"

    device_dict['Hardware'] = dummy_data.get('Hardware', "Dummy")
    device_dict['Type'] = dummy_data.get('Type', "Dummy")
    device_dict['LengthMm'] = dummy_data.get('LengthMm', "100mm")
    device_dict['Depth'] = dummy_data.get('Depth', "100mm")
    device_dict['Height'] = dummy_data.get('Height', "30mm")
    device_dict['Shelf'] = dummy_data.get('Shelf', "Dummy")
    device_dict['HeightUnits'] = dummy_data.get('HeightUnits', default_height_in_u)
    device_dict['ShelfId'] = dummy_data.get('ShelfId', default_shelf_id )
    return device_dict
