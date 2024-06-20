#!/usr/bin/env python

"""
This module is used to generate config options for CadOrchestrator using devices.json
"""

import os
import sys
import json

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
        item = {'value': device['ID'],
                'name': device['Brand']+" "+device['Hardware']}
        if device['Type'] == "Access Point":
            access_points.append(item)
        elif device['Type'].startswith("Router"):
            routers.append(item)
        elif device['Type'] == "Server":
            servers.append(item)
        elif device['Type'] == "Switch":
            switches.append(item)

    conf_dict = {
        "options": [{
            "option-type": "list",
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

if __name__ == "__main__":
    main()
