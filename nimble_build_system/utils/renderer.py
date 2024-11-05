import cadquery as cq
import cadquery_png_plugin.plugin  # This activates the PNG plugin for CadQuery
from cq_annotate.callouts import add_assembly_lines

def generate_render(model=None, image_format="png", file_path=None, render_options=None):
    """
    Generates a render of an assembly.

        parameters:
            model (cadquery): The model to render, can be either a single part or an assembly
            camera_pos (tuple): The position of the camera when capturing the render
            annotate (bool): Whether or not to annotate the render using cq-annotate
            image_format (str): The format of the image to render (png, svg, gltf, etc)

        returns:
            render_path (str): The path to the rendered image
    """

    # TODO - Return a bitmap buffer instead of a file path

    # Check to see if we are dealing with a single part or an assembly
    if isinstance(model, cq.Assembly):
        # Handle assembly annotation
        if render_options["annotate"]:
            add_assembly_lines(model)

        # Handle the varioius image formats separately
        if image_format == "png":
            model.exportPNG(options=render_options, file_path=file_path)
        else:
            print("Unknown image format")
