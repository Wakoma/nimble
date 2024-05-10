#!/usr/bin/env python

import sys
import csv
import json

def usage():
    """
    Prints a usage message for this utility.
    """
    print("This utility exists to update the devices.json file in the root of the repository.")
    print("The orchestration and generation scripts rely on this file to generate the models and assemblies.")
    print("Usage:")
    print("    ./devices_json_updater.py [path_to_nocodb_csv_file]")

def main():
    # Check to make sure the user passed a CSV path
    if len(sys.argv) != 2:
        usage()
        quit()

    # Keeps track of the device entries
    devices = []

    # Retrieve the CSV path that the user should have passed
    csv_path = sys.argv[1]

    # Allows us to assume that the first line of the file will be header data
    getting_headers = True
    headers = None

    with open(csv_path, newline='') as csvfile:
        # Parse the entire file into rows
        devices_csv = csv.reader(csvfile, delimiter=',')

        # Process the rows into objects with key/value pairs
        for row in devices_csv:
            # The current object being assembled
            cur_obj = {}

            # Handle the first line as headers
            if getting_headers:
                getting_headers = False
                headers = row
                print(headers)
            # All other rows are device data
            else:
                # Generate a unique ID for each device
                device_id = row[1].replace(" ", "_")
                cur_obj["ID"] = device_id

                # Match each row with its header
                for i, entry in enumerate(row):
                    cur_obj[headers[i]] = entry

                # Save the current device
                devices.append(cur_obj)

    # Write the JSON data to file
    with open('../devices.json', 'w') as f:
        json.dump(devices, f)

if __name__ == "__main__":
    main()