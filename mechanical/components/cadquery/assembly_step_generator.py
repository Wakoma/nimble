import cadquery as cq
from tray_6in import create_6in_shelf
from cq_warehouse.fastener import SocketHeadCapScrew
from device_placeholder import generate_placeholder

def generate_assembly_step(device_id, json_config, exploded=True, annotated=True):
    """
    Generates an assembly showing the assembly step between a device
    and a shelf, generated solely based on the device ID.
    """

    # Extract the device dimension information from the JSON object
    length = float(json_config["LengthMm"].split(" ")[0])
    depth = float(json_config["Depth"].split(" ")[0])
    height = float(json_config["Height"].split(" ")[0])
    height_in_units = int(json_config["HeightUnits"])

    # Clean up shelf IDs that do not match the database
    shelf_id = json_config["ShelfId"]
    if shelf_id.startswith("raspi"):
        shelf_id = "raspi"

    # Generate the placeholder device so that the step can be built dynamically
    device = generate_placeholder(device_id, length, depth, height)

    # Generate the shelf for the given device
    shelf = create_6in_shelf(shelf_id, height_in_units).cq()

    # Generate an assembly with the device and shelf correctly positioned
    assy = cq.Assembly()
    assy.add(shelf, name="shelf", color=cq.Color(0.996, 0.867, 0.0, 1.0))
    assy.add(device, name="device", color=cq.Color(0.565, 0.698, 0.278, 1.0))

    # Set up constraints that will keep the device in the correct relationship to the shelf
    assy.constrain("shelf", "Fixed")
    assy.constrain("device@faces@>X", "shelf@faces@<Y[-2]", "Axis")
    assy.constrain("device@faces@<Z", "shelf@faces@<Z[-3]", "Plane")
    assy.solve()

    from cadquery.vis import show
    show(assy)


def main():
    """
    Allows a user to run this as a command line utility.
    Needs to be run from the root of the repository for
    the JSON file to be found.
    """

    import json

    # The device that the assembly step should be generated for 
    device_id = "Raspberry_Pi_4B"

    # Import and process the devices.json file
    with open('devices.json') as json_file:
        json_string = json_file.read()
        devices_json = json.loads(json_string)

        for cur_device in devices_json:
            if cur_device["ID"] == device_id:
                device = cur_device

    # Call the code that generates the CAD models and assembly for the step
    generate_assembly_step(device_id, device)


if __name__ == "__main__":
    main()
