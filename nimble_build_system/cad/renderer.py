"""
Helper module to render a CadQuery model to a PNG image file.
"""

#pylint: disable=too-few-public-methods
#pylint: disable=unused-import

import cadquery as cq
import cadquery_png_plugin.plugin  # This activates the PNG plugin for CadQuery
from cq_annotate.callouts import add_assembly_lines

def generate_render(model=None,
                    image_format="png",
                    file_path=None,
                    render_options=None,
                    selective_list=None):
    """
    Generates a render of an assembly.

        parameters:
            model (cadquery.Assembly): The assembly to render
            image_format (str): The format of the image to render (png, svg, gltf, etc)
            file_path (str): The path to save the rendered image to
            render_options (dict): A dictionary of options to pass to the render function for
                                   things like which view to render,etc

        returns:
            None
    """

    # Check to see if we are dealing with a single part or an assembly
    if isinstance(model, cq.Assembly):
        # Handle assembly annotation
        if render_options["annotate"]:
            add_assembly_lines(model, selective_list=selective_list)

        # Handle the varioius image formats separately
        if image_format == "png":
            model.exportPNG(options=render_options, file_path=file_path)
        else:
            print("Unknown image format")
