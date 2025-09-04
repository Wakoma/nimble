#!/usr/bin/env python

"""
This module is used to generate config options for CadOrchestrator using devices.json
"""

import os
import sys
import json
import re

def usage():
    """
    Prints a usage message for this utility.
    """
    print("This utility exists to generate config options for CadOrchestrator")
    print("using devices.json")
    print("Usage:")
    print("    gen_nimble_conf_options")

def main():
    """
    Main script to turn a CSV file into a JSON file. It does not do pretty formatting,
    it is a JSON file with no newlines.
    """

    if not os.path.exists('devices.json'):
        print("Error. devices.json not found")
        sys.exit(1)
    # Write the JSON data to file
    with open('devices.json', 'r', encoding="utf-8") as dev_file:
        devices = json.load(dev_file)

    access_points = []
    routers = []
    servers = []
    switches = []
    for device in devices:

        if not device['qc_pass']:
            # If a device specification has not passed the overall checklist:
            # 3D Renering: True
            # Documentation: True
            # Testing: True
            # Approved by code-team: True
            # Then the device will not be taking for nimble cadorchestrator.
            continue

        if not shelf_available(device):
            #If a shelf cannot be made for this item then skip it
            continue
        
        # Added If statement filtering only '6 in' Rack label items, 
        # fixing big boxes with render issues."                                                                                                                             
        if device['Rack'] != '6 in':
            # This avois placing Racks different by '6 in' in the devices.json
            continue

        item = {'value': device['ID'],
                'name': device['Brand']+" "+device['Hardware']}
        if device['Type'] in ["Access Point", "Router + AP"]:
            access_points.append(item)
        elif device['Type'] in ["Router", "Router + AP"]:
            routers.append(item)
        elif device['Type'] == "Server":
            servers.append(item)
        elif device['Type'] == "Switch":
            switches.append(item)

    conf_dict = {
        "options": [{
            "response-key": "device-ids",
            "option-type": "list",
            "item-name": "Shelf",
            "add-options": [
                {
                    "display-name": "Access Point",
                    "id": "accesspoint",
                    "items": access_points
                },
                {
                    "display-name": "Router",
                    "id": "router",
                    "items": routers
                },
                {
                    "display-name": "Server",
                    "id": "server",
                    "items": servers
                },
                {
                    "display-name": "Switch",
                    "id": "switch",
                    "items": switches
                }
            ]
        }
    ]}

    with open('OrchestratorConfigOptions.json', 'w', encoding="utf-8") as conf_file:
        json.dump(conf_dict, conf_file)


def shelf_available(device):
    """
    Return True if a shelf can be made for this device if not return False.
    """

    #If the HeightUnit is specified, return True if it is an integer. False if specified
    # but not understood
    if device['HeightUnits']:
        try:
            int(device['HeightUnits'])
        except ValueError:
            print(f"Warning: Invalid data in HeightUnits feild for {device['ID']}")
            return False
        return True

    # If HeightUnits is not set then check if Height is set and is a numerical value in mm
    if device['Height']:
        if re.match(r'^[0-9]+(?:\.[0-9]+)? ?mm$', device['Height']):
            return True
        print(f"Warning: Invalid data in Height feild for {device['ID']}: ({device['Height']})")
        return False

    # Neither Height or HeightUnits set. No shelf can be made.
    return False

if __name__ == "__main__":
    main()
