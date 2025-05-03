#! /usr/bin/env python

"""
This script generates a number of STL files and also creates
as simple website to view them. This is designed to be run
via a github action to provide a list of available STLs for
direct download without them needing to be committed to the repository
"""
import os
import json

from cadorchestrator.generate import generate_components

from nimble_build_system.orchestration.paths import BUILD_DIR

from nimble_build_system.cad.shelf import create_shelf_for_x

def generate():
    """
    Main script function. Gets a list of printed components (legs and shelves)
    and uses the orchestration runner to build them
    """

    components = get_component_list()
    generate_components(components)
    output_static_site(components)

def get_component_list():
    """
    Generate the component list. This is 4 types of legs and some
    shelves
    """

    component_list = []

    #Loop through the options dictionary that the web ui uses for config options
    with open('OrchestratorConfigOptions.json', encoding="utf-8") as config_options_file:
        conf_options = json.load(config_options_file)

        for device_category_dict in conf_options['options'][0]['add-options']:
            for device in device_category_dict['items']:
                device_id = device['value']
                shelf = create_shelf_for_x(device_id)
                component_list.append(shelf.shelf_component)
    #return a list of GeneratedMechanicalComponent objects
    return component_list


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
                Nimble downloads
                </h1>

                <h2>Auto-generated documentation:</h3>
                <p>
                We are working on a system to automatically generate documentation for any
                nimble configuration. This is an example of the <a href="assembly-docs">
                automatically generated documentation</a> for a specific configuration.
                </p>

                <h2>Shelf STL files:</h3>
                <p>
                While we work on builing the nimble configurator you can download all
                nimble shelves from the list below
                </p>
                """)

        f.write("")
        f.write("<ul>")
        for component in components:
            f.write(f"<li><a href='{component.stl_representation}'>{component.name}</a></li>")
        f.write("</ul>")

        f.write("</body></html>")

if __name__ == "__main__":
    generate()
