#!/usr/bin/env python

"""
This module is used to update the devices.json file from a CSV downloaded from nocodb.
"""
import os
import json
import argparse
import requests
from dotenv import load_dotenv


load_dotenv()
SECRET_TOKEN = os.getenv("NOCODB_TOKEN")
URL = "https://nocodb.wakoma.net/api/v2/tables/md_37ewfwcrh6b36a/records?viewId=vwsq7m3dmn9wqlnu&limit=1000&shuffle=0&offset=0"
HEADERS = {"xc-token": SECRET_TOKEN}



def get_remote_json(_url, _headers):
    """
    This utility exists to update the devices.json file in the
    root of the repository. The orchestration and generation scripts
    rely on this file to generate the models and assemblies.
    The json file is created from a CSV file that can be pulled from
    our database. Alternatively a local file can be used.
    SETUP an ENV VARIABLE as NOCODB_TOKEN with VALUE of your NOCODB TOKEN)
    """
    
    response = requests.get(_url, headers=_headers, timeout=100)
    
    if response.status_code != 200:
        raise RuntimeError("Failed to get json data from database")
    json_name = "raw_devices.json"
    with open(json_name, 'wb') as file_obj:
        file_obj.write(response.content)
    return json_name


def main():
    """
    Main script to turn a CSV file into a JSON file. It does not do pretty formatting,
    it is a JSON file with no newlines.
    """

    json_path = get_remote_json(URL, HEADERS)

    # Keeps track of the device entries
    devices = []

    with open(json_path, encoding="utf-8") as jsonfile:
        # Load the entire JSON file
        data = json.load(jsonfile)

        # NocoDB v2 API response usually has a "list" field with rows
        rows = data.get("list", [])

        for row in rows:
            # Generate a unique ID (using the "Name" field as example)
            device_id = str(row.get("Hardware", "")).replace(" ", "_")

            # Start with an ID field
            cur_obj = {"ID": device_id}

            # Merge all fields from the row
            cur_obj.update(row)

            # Save the current device
            devices.append(cur_obj)

    # Write the JSON data to file
    with open("devices.json", "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=2, ensure_ascii=False)

#if __name__ == "__main__":
#    main()
try:
    main()
except RuntimeError:
    print("export NOCODB_TOKEN=?? is missing. Get a token from noco.wakoma.net")