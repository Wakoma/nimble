#!/usr/bin/env python

"""
This module is used to update the devices.json file from a CSV downloaded from nocodb.
"""

import sys
import csv
import json
import argparse

import requests

BASE_URL = "https://nocodb.wakoma.net/api/v1/db/public"
VIEW_URL = "/shared-view/a25a734f-a0d9-4e7f-976f-40723b9f22b6/rows/export/csv"


def parse_args():
    """
    Prints a usage message for this utility.
    """
    msg = ("This utility exists to update the devices.json file in the "
           "root of the repository. The orchestration and generation scripts "
           "rely on this file to generate the models and assemblies. "
           "The json file is created from a CSV file that can be pulled from "
           "our database. Alternatively a local file can be used.")
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument(
        "--url",
        metavar="https://...",
        help="Override the default API url for collecting the data"
    )
    parser.add_argument(
        "--local",
        metavar="filename.csv",
        help="Use local csv"
    )
    return parser.parse_args()


def get_remote_csv(url):
    """
    Get the CSV from the database API, and save locally for processing. If no url
    is input then a default is used.

    Return the name of the written CSV file.
    """
    if url is None:
        url = BASE_URL+VIEW_URL
    ret = requests.get(url, timeout=10)
    if ret.status_code != 200:
        raise RuntimeError("Failed to get csv data from database")
    csv_name = "networking_hardware.csv"
    with open(csv_name, 'wb') as file_obj:
        file_obj.write(ret.content)
    return csv_name


def main():
    """
    Main script to turn a CSV file into a JSON file. It does not do pretty formatting,
    it is a JSON file with no newlines.
    """

    args = parse_args()
    
    if args.local:
        if args.url:
            raise RuntimeError("Cannot set an API path and a local file. "
                               "Pick one or the other.")
        csv_path = args.local
    else:
        csv_path = get_remote_csv(args.url)

    # Keeps track of the device entries
    devices = []

    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        # Parse the entire file into rows
        devices_csv = csv.reader(csvfile, delimiter=',')

        headers = next(devices_csv)

        # Process the rows into objects with key/value pairs
        for row in devices_csv:
            # The current object being assembled

            # Generate a unique ID for each device
            device_id = row[1].replace(" ", "_")
            cur_obj = {"ID": device_id}

            # Match each row with its header
            for i, entry in enumerate(row):
                cur_obj[headers[i]] = entry

            # Save the current device
            devices.append(cur_obj)

    # Write the JSON data to file
    with open('devices.json', 'w', encoding="utf-8") as f:
        json.dump(devices, f)

if __name__ == "__main__":
    main()
