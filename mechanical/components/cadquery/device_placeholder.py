import cadquery as cq

def generate_placeholder(device_name, length, depth, height):
    """
    Generates a generalized placeholder object for a device.
    """

    # Save the smallest dimension for things like filleting and text
    smallest_dim = min(length, depth, height)

    # The overall shape
    placeholder = cq.Workplane().box(length, depth, height)

    # Round the edges
    placeholder = placeholder.edges().fillet(smallest_dim * 0.3)

    # Add the text of what the device is to the top
    placeholder = placeholder.faces(">Z").workplane(centerOption="CenterOfBoundBox").text(device_name, fontsize=6, distance=-smallest_dim * 0.1)

    return placeholder