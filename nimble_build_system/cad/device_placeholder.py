"""
This module provides a function to generate a placeholder object for a device. Given the dimensions
of a device, this function will create a placeholder object that can be used to represent the
device in an assembly. The function will also try to imprint the name of the device on the resulting
model.
"""
import cadquery as cq


def generate_generic(device_name, width, depth, height, smallest_dim):
    """
    Generates a generic placeholder object for a device.
    """

    # The overall shape
    placeholder = cq.Workplane().box(width, depth, height)

    # Round the edges
    placeholder = placeholder.edges().fillet(smallest_dim * 0.3)

    # Add the text of what the device is to the top
    placeholder = (placeholder.faces(">Z")
                    .workplane(centerOption="CenterOfBoundBox")
                    .text(device_name.replace(" shelf", ""),
                          fontsize=6,
                          distance=-smallest_dim * 0.1))

    return placeholder


def generate_raspberry_pi_4b(device_name):
    """
    Generates a placeholder object for a Raspberry Pi 4B device.
    """

    pcb_width = 56.0  # The width of the Raspberry Pi 4B circuit board in mm
    pcb_depth = 85.0  # The depth of the Raspberry Pi 4B circuit board in mm
    pcb_thickness = 1.3  # The thickness of the Raspberry Pi 4B circuit board in mm

    # The shape of the circuit board
    placeholder = cq.Workplane().box(pcb_width, pcb_depth, pcb_thickness)
    placeholder = placeholder.edges("|Z").fillet(3.0)

    # The mounting holes in the circuit board
    placeholder = (placeholder.faces(">Z")
                    .workplane(centerOption="CenterOfBoundBox")
                    .pushPoints([
                        (pcb_width / 2.0 - 3.5, pcb_depth / 2.0 - 3.5),
                        (-pcb_width / 2.0 + 3.5, pcb_depth / 2.0 - 3.5),
                        (pcb_width / 2.0 - 3.5, pcb_depth / 2.0 - 61.5),
                        (-pcb_width / 2.0 + 3.5, pcb_depth / 2.0 - 61.5)
                    ])
                    .hole(2.75))

    # Add the Ethernet port to the placeholder
    placeholder = (placeholder.faces(">Z")
                    .workplane(centerOption="CenterOfBoundBox")
                    .pushPoints([
                        (-pcb_width / 2.0 + 10.25, -pcb_depth / 2.0 + 21.25 / 2.0 - 2.0),
                    ])
                    .rect(16.0, 21.25)
                    .extrude(13.75))


    # Add the USB ports to the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .pushPoints([
                        (-pcb_width / 2.0 + 29.0, -pcb_depth / 2.0 + 17.15 / 2.0 - 2.0),
                        (-pcb_width / 2.0 + 47.0, -pcb_depth / 2.0 + 17.15 / 2.0 - 2.0),
                    ])
                    .rect(15.15, 17.15)
                    .extrude(15.75))

    # Add the audio port to the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .pushPoints([
                        (-pcb_width / 2.0 + 14.7 / 2.0 - 2.25, pcb_depth / 2.0 - 53.5),
                    ])
                    .rect(14.7, 7.0)
                    .extrude(6.0))

    # Add the HDMI port to the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .pushPoints([
                        (-pcb_width / 2.0 + 11.0 / 2.0 - 1.25, pcb_depth / 2.0 - 32.0),
                    ])
                    .rect(11.0, 15.0)
                    .extrude(6.0))

    # Add the power port to the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .pushPoints([
                        (-pcb_width / 2.0 + 5.65 / 2.0 - 1.25, pcb_depth / 2.0 - 10.6),
                    ])
                    .rect(5.65, 8.0)
                    .extrude(2.5))

    # Add the I/O header to the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .pushPoints([
                        (pcb_width / 2.0 - 5.15 / 2.0 - 1.25, pcb_depth / 2.0 - 32.5),
                    ])
                    .rect(5.15, 50.75)
                    .extrude(8.75))

    # Add the text of what the device is to the top
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox", offset=pcb_thickness, invert=True)
                    .text(device_name.replace(" shelf", ""),
                          fontsize=6,
                          distance=-pcb_thickness + 0.1))

    # Add the SD card socket to the bottom of the placeholder
    placeholder = (placeholder.faces("<Z")
                    .workplane(centerOption="CenterOfBoundBox")
                    .pushPoints([
                        (0.0, -pcb_depth / 2.0 + 11.4 / 2.0 + 1.70),
                    ])
                    .rect(12.0, 11.4)
                    .extrude(1.75))

    return placeholder


def generate_placeholder(device_name, width, depth, height):
    """
    Generates a generalized placeholder object for a device.
    """

    # Save the smallest dimension for things like filleting and text
    smallest_dim = min(width, depth, height)

    # Sometimes there will be a non-generic placeholder that we can use
    if "raspberry" in device_name.lower() and "4b" in device_name.lower():
        # The overall shape
        placeholder = generate_raspberry_pi_4b(device_name)
    else:
        # The overall shape
        placeholder = generate_generic(device_name, width, depth, height, smallest_dim)

    return placeholder
