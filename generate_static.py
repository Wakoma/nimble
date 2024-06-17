#! /usr/bin/env python

"""
This script generates a number of STL files and also creates
as simple website to view them. This is designed to be run
via a github action to provide a list of available STLs for
direct download without them needing to be commited to the repository
"""
import os

from cadorchestrator.orchestration import OrchestrationRunner
from cadorchestrator.components import GeneratedMechanicalComponent
from nimble_orchestration.paths import BUILD_DIR, REL_MECH_DIR

def generate():
    """
    Main script function. Gets a list of printed components (legs and shelves)
    and uses the orchestration runner to build them
    """

    components = get_component_list()
    runner = OrchestrationRunner()
    runner.generate_components(components)
    output_static_site(components)

def get_component_list():
    """
    Generate the component list. This is 4 types of legs and some
    shelves
    """

    components = []

    components.append(
        generate_leg(
            length=294,
            mounting_holes_dia=3.6,
            name="Rack leg with 21 holes",
            out_file="./printed_components/beam-21holes.stl"
        )
    )
    components.append(
        generate_leg(
            length=168,
            mounting_holes_dia=3.6,
            name="Rack leg with 12 holes",
            out_file="./printed_components/beam-12holes.stl"
        )
    )

    components.append(
        generate_leg(
            length=294,
            mounting_holes_dia=5.8,
            name="Rack leg with 21 M6 holes",
            out_file="./printed_components/beam-M6-21holes.stl"
        )
    )

    components.append(
        generate_leg(
            length=168,
            mounting_holes_dia=5.8,
            name="Rack leg with 12 M6 holes",
            out_file="./printed_components/beam-M6-12holes.stl"
        )
    )

    for (shelf_type, height_in_u) in [
            ("stuff", 3),
            ("stuff-thin", 3),
            ("nuc", 3),
            ("nuc", 4),
            ("usw-flex", 3),
            ("usw-flex-mini", 2),
            ("anker-powerport5", 2),
            ("anker-a2123", 2),
            ("anker-atom3slim", 2),
            ("hdd35", 2),
            ("dual-ssd", 2),
            ("raspi", 2)]:

        components.append(generate_shelf(shelf_type, height_in_u))

    return components


def generate_leg(length, mounting_holes_dia, name, out_file):
    """
    Helper function to generate a leg. Returns a GeneratedMechanicalComponent
    object which contains the data for the leg.
    """
    source = os.path.join(REL_MECH_DIR, "components/cadquery/rack_leg.py")
    key = name.lower().replace(' ', '_')
    return GeneratedMechanicalComponent(
        key=key,
        name=name,
        description='A leg for a nimble rack',
        output_files=[out_file],
        source_files=[source],
        parameters={
            "length": length,
            "mounting_holes_dia": mounting_holes_dia
        },
        application="cadquery"
    )


def generate_shelf(shelf_type, height_in_u):
    """
    Helper function to generate a shelf/tray. Returns a GeneratedMechanicalComponent
    object which contains the data for the shelf.
    """
    out_file = f"./printed_components/shelf_6in_{shelf_type}u_{height_in_u}.stl"
    source = os.path.join(REL_MECH_DIR, "components/cadquery/tray_6in.py")
    device_name = shelf_type.replace('-', ' ')
    return GeneratedMechanicalComponent(
        key=f"{shelf_type}_{height_in_u}u",
        name=f"Tray for {device_name}",
        description=f"Tray for {device_name}, height = {height_in_u}u",
        output_files=[out_file],
        source_files=[source],
        parameters={'shelf_type': shelf_type, 'height_in_u': height_in_u},
        application="cadquery"
    )

def output_static_site(components):
    """
    Create a sumple web page (index.html) with links to all generated files
    """

    index_file = os.path.join(BUILD_DIR, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("<html>")
        f.write("""
                <head>
                <title>Nimble STLs for printing</title>
                <style>
                    body { font-family: sans-serif; }
                </style>
                </head>
                <body>
                
                <h1>
                Nimble STL files
                </h1>

                <p>
                Nimble is going through a transition towards live generation of all files and documentation
                for hardware configuration. We call this "Smart Doc". For more details on Nimble see
                <a href="https://github.com/Wakoma/nimble">https://github.com/Wakoma/nimble</a>
                </p>

                <p>
                Smart Doc" is not yet finished, but the code already generates a number of nimble components
                that may be useful to you. You can find them below.
                </p>
                
                """)

        f.write("<h3>Generated files:</h3>")
        f.write("<ul>")
        for component in components:
            f.write(f"<li><a href='{component.output_files[0]}'>{component.name}</a></li>")
        f.write("</ul>")
        f.write(
            """
            <h3>Example documentation:</h3>
            <p>
            Partially complete automatically generated documentation
            <a href="assembly-docs">is also available</a>.
            </p>
            """)

        f.write("</body></html>")

if __name__ == "__main__":
    generate()
