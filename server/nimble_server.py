import os, sys
import re
import json
import tempfile
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

# Change this to the base URL of the server that is serving this app
server_base_url = "http://127.0.0.1:8000"

# Used to keep track of the configurations that are being, or have been, generated
generated_docs_urls = {}

# Allow imports from the parent directory (potential security issue)
sys.path.append(os.path.dirname(__file__) + "/..")

from generate import generate

app = FastAPI()

# Static files for the test page
app.mount("/static", StaticFiles(directory="static"), name="static")


# http://127.0.0.1:8000/wakoma/nimble/configurator
@app.get("/wakoma/nimble/configurator")
async def read_index():
    """
    Loads a sample page so that the system can be tested end-to-end.
    """

    return FileResponse('configurator.html')


def get_unique_name(config):
    """
    Allows the caller to get a unique name for a configuration.
    """

    # Concatenate all the component names together
    unique_name = "!".join(config)

    # Replace spaces with underscores
    unique_name = unique_name.replace(" ", "_")

    # Delete all non-alphanumeric characters (other than _)
    unique_name = re.sub(r'[^a-zA-Z0-9_!]', '', unique_name)

    return unique_name


# http://127.0.0.1:8000/wakoma/nimble
@app.post("/wakoma/nimble")
async def get_body(request: Request):
    """
    Allows the caller to request documentation to be generated for the
    specific configuration that they pass.
    """

    # TODO: Need to define at least a temporary data structure for this based on what the orchestration script needs to see
    req = await request.json()
    config = req['config']

    # Make sure that a config was passed
    if (len(config) == 0):
        print("Nothing to build")
        return ORJSONResponse([{"error": "Configuration must have components in it."}], status_code=500)

    print("Starting build for config:")
    print(config)

    # Create a clean, unique name for this build
    unique_name = get_unique_name(config)

    # Trigger the generation of all materials, but only if they do not already exist
    module_path = Path(__file__).resolve().parent.parent
    if not os.path.exists(module_path / "_cache_" / f"{unique_name}.zip"):
        # Call all the underlying Nimble generator code
        generate(config)

        # Create the zip file
        shutil.make_archive(str(module_path / "_cache_" / unique_name), 'zip', os.path.join(module_path, "build"))

        # Make a copy of the glTF preview file to cache it
        shutil.copyfile(str(module_path / "build" / "assembly" / "assembly.glb"), str(module_path / "_cache_" / f"{unique_name}.glb"))

        # Make a cached copy of the assembly docs so that they can be served to the user
        copy_tree(str(module_path / "build" / "assembly-docs"), str(module_path / "server" / "static" / "builds" / f"{unique_name}_assembly_docs"))

        # Make sure the new directory is served as static
        # app.mount(str(module_path / "_cache_" / f"{unique_name}-assembly-docs"), StaticFiles(directory="static"), name="static")

    # Check to make sure we have the _cache_ directory that holds the distribution files
    if not os.path.isdir(str(module_path / "_cache_")):
        os.makedirs(str(module_path / "_cache_"))

    # Save the fact that this has been generated before
    config_url = server_base_url + "/wakoma/nimble/auto-doc?config=" + unique_name

    # Let the client know where they can download the file
    return ORJSONResponse([{"redirect": config_url, "description": "Poll this URL until your documentation package is ready."}])


def check_model_format(model_format):
    """
    Checks to make sure the model_format provided by the caller is valid.
    """
    if (model_format != 'stl' and model_format != 'amf' and model_format != '3mf' and model_format != 'step' and model_format != 'stp'):
        return False
    else:
        return True


def cqgi_model_script(file_name, params):
    """
    Handle executing the model script via CQGI.
    """

    from cadquery import cqgi

    # Read and execute the rack leg script
    cq_path = os.path.join("..", "mechanical", "components", "cadquery", file_name)
    user_script = ""
    with open(cq_path) as f:
        user_script = f.read()

    # Build the object with the customized parameters and get it ready to export
    build_result = cqgi.parse(user_script).build(build_parameters=params)
    if build_result.success:
        res = build_result.results[0].shape
    else:
        return HTMLResponse(f'ERROR: There was an error executing the script: {build_result.exception}')

    return res


# http://127.0.0.1:8000/wakoma/nimble/components
@app.get("/wakoma/nimble/components")
async def get_body(request: Request):
    # Load the devices.json file
    with open('../devices.json', 'r', encoding='utf-8') as component_file:
        component_data = json.load(component_file)

    return ORJSONResponse([component_data])


# http://127.0.0.1:8000/wakoma/nimble/rack_leg?length=50.0&model_format=stl
@app.get("/wakoma/nimble/rack_leg")
def read_item(length: float = 294.0, hole_spacing: float = 14.0, long_axis_hole_dia: float = 4.6, mounting_holes_dia:float = 3.6, model_format: str = "stl"):
    """
    Provides access to the individual parameterized model of a rack leg.
    """
    # Check to make sure the user requested a valid model format
    if not check_model_format(model_format):
        return HTMLResponse(f'ERROR: Model format {model_format} is not supported. Please go back and try again.')

    # Check to make sure the user has not set a length that is too long
    if length > 1000:
        return HTMLResponse('ERROR: Length parameter is too large. Please check your parameters and try again.')

    # Make sure that the hole spacing is valid
    if hole_spacing <= 0.0 or hole_spacing >= length or hole_spacing <= mounting_holes_dia:
         return HTMLResponse('ERROR: Invalid hole_spacing parameter. Please check your parameters and try again.')

    # Make sure that the long axis hole diameter is valid
    if long_axis_hole_dia <= 0.0 or long_axis_hole_dia >= 20.0:
        return HTMLResponse('ERROR: Invalid long_axis_hole_dia parameter. Please check your parameters and try again.')

    # Make sure that the mounting hole diameter is valid
    if mounting_holes_dia <= 0.0 or mounting_holes_dia >= 20.0:
        return HTMLResponse('ERROR: Invalid mounting_holes_dia parameter. Please check your parameters and try again.')

    # Add the CadQuery model path so that all models only need to do absolute imports
    cq_path = os.path.join("..", "mechanical", "components", "cadquery")
    sys.path.append(cq_path)

    import cadquery as cq

    # Run the script with customized parameters
    leg = cqgi_model_script("rack_leg.py", {'length': length, 'hole_spacing': hole_spacing, 'long_axis_hole_dia': long_axis_hole_dia, 'mounting_holes_dia': mounting_holes_dia})

    # In case there was an error
    if (type(leg).__name__ == "HTMLResponse"):
        return leg

    # Figure out what the file name and temporary path should be
    export_file_name = "rack_leg-leg_length-" + str(length) + "_hole_spacing-" + str(hole_spacing) + "_long_axis_hole_dia-" + str(long_axis_hole_dia) + "_mounting_holes_dia-" + str(mounting_holes_dia) + "." + model_format
    export_path = os.path.join(tempfile.gettempdir(), export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(leg, export_path)

    return FileResponse(export_path, headers={'Content-Disposition': 'attachment; filename=' + export_file_name})


# http://127.0.0.1:8000/wakoma/nimble/top_plate?width=100&depth=100&height=3&model_format=stl
@app.get("/wakoma/nimble/top_plate")
def read_item(width: float = 100, depth: float = 100, height: float = 3, model_format: str = "stl"):
    # Check to make sure the user requested a valid model format
    if not check_model_format(model_format):
        return HTMLResponse(f'ERROR: Model format {model_format} is not supported. Please check your parameters and try again.')

    # Check to make sure all the model dimensions are positive
    if width < 0 or depth < 0 or height < 0:
        return HTMLResponse(f'ERROR: None of the model dimensions can be negative. Please check your parameters and try again.')

    # Add the CadQuery model path so that all models only need to do absolute imports
    cq_path = os.path.join("..", "mechanical", "components", "cadquery")
    sys.path.append(cq_path)

    import cadquery as cq

    # Run the script with customized parameters
    plate = cqgi_model_script("top_plate.py", {'width': width, 'depth': depth, 'height': height})

    # In case there was an error
    if (type(plate).__name__ == "HTMLResponse"):
        return plate

    # Figure out what the file name and temporary path should be
    export_file_name = "top_plate_width-" + str(width) + "_depth-" + str(depth) + "_height-" + str(height) + "." + model_format
    export_path = os.path.join(tempfile.gettempdir(), export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(plate, export_path)

    return FileResponse(export_path, headers={'Content-Disposition': 'attachment; filename=' + export_file_name})


# http://127.0.0.1:8000/wakoma/nimble/tray?number_of_units=2&tray_width=115&tray_depth=115&model_format=stl
@app.get("/wakoma/nimble/tray")
def read_item(number_of_units: float = 2, tray_width: float = 115, tray_depth: float = 115, model_format: str = "stl"):
    # Check to make sure the user requested a valid model format
    if not check_model_format(model_format):
        return HTMLResponse(f'ERROR: Model format {model_format} is not supported. Please check your parameters and try again.')

    # Check to make sure all the model dimensions are positive
    if number_of_units < 0 or tray_width < 0 or tray_depth < 0:
        return HTMLResponse(f'ERROR: None of the model dimensions can be negative. Please check your parameters and try again.')

    # Add the CadQuery model path so that all models only need to do absolute imports
    cq_path = os.path.join("..", "mechanical", "components", "cadquery")
    sys.path.append(cq_path)

    import cadquery as cq

    ## NOTE that tray_width and tray_depth are no longer used after moving to tray_6in.py
    # Run the script with customized parameters
    tray = cqgi_model_script("tray_6in.py", {"height_in_u": number_of_units, "shelf_type": "generic"})

    # In case there was an error
    if (type(tray).__name__ == "HTMLResponse"):
        return tray

    # Figure out what the file name and temporary path should be
    export_file_name = "tray_number_of_units-" + str(number_of_units) + "_tray_width-" + str(tray_width) + "_tray_depth-" + str(tray_depth) + "." + model_format
    export_path = os.path.join(tempfile.gettempdir(), export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(tray, export_path)

    return FileResponse(export_path, headers={'Content-Disposition': 'attachment; filename=' + export_file_name})


# http://127.0.0.1:8000/wakoma/nimble/base_plate?width=100&depth=100&height=3&model_format=stl
@app.get("/wakoma/nimble/base_plate")
def read_item(width: float = 100, depth: float = 100, height: float = 3, model_format: str = "stl"):
    # Check to make sure the user requested a valid model format
    if not check_model_format(model_format):
        return HTMLResponse(f'ERROR: Model format {model_format} is not supported. Please check your parameters and try again.')

    # Check to make sure all the model dimensions are positive
    if width < 0 or depth < 0 or height < 0:
        return HTMLResponse(f'ERROR: None of the model dimensions can be negative. Please check your parameters and try again.')

    # Add the CadQuery model path so that all models only need to do absolute imports
    cq_path = os.path.join("..", "mechanical", "components", "cadquery")
    sys.path.append(cq_path)

    import cadquery as cq

    # Run the script with customized parameters
    base_plate = cqgi_model_script("base_plate.py", {"width": width, "depth": depth, "height": height})

    # In case there was an error
    if (type(base_plate).__name__ == "HTMLResponse"):
        return base_plate

    # Figure out what the file name and temporary path should be
    export_file_name = "base_plate_width-" + str(width) + "_depth-" + str(depth) + "_height-" + str(height) + "." + model_format
    export_path = os.path.join(tempfile.gettempdir(), export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(base_plate, export_path)

    return FileResponse(export_path, headers={'Content-Disposition': 'attachment; filename=' + export_file_name})


@app.get("/wakoma/nimble/auto-doc")
def get_files(config):
    """
    Loads any auto-generated documentation files.
    """

    # Figure out what the build path is
    module_path = Path(__file__).resolve().parent.parent
    build_path = module_path  / "_cache_" / config

    # Once the build exists we can send it to the user, but before that we give them a temporary redirect
    if os.path.exists(str(build_path) + ".zip"):
        return FileResponse(str(build_path) + ".zip", headers={'Content-Disposition': 'attachment; filename=' + config + ".zip"})
    else:
        return HTMLResponse(content="<p>The File is Still Processing</p>", status_code=307)


@app.get("/wakoma/nimble/preview")
def get_preview(config):
    """
    Sends a 3D preview (glTF) file to the client.
    """

    # Figure out what the build and glb path is
    module_path = Path(__file__).resolve().parent.parent
    glb_file_name = f"{config}.glb"
    glb_path = module_path  / "_cache_" / glb_file_name

    # If the glb file exists, send it to the client
    if os.path.exists(glb_path):
        return FileResponse(str(glb_path), headers={'Content-Disposition': 'attachment; filename=' + glb_file_name})
    else:
        return HTMLResponse(content="<p>Preview is not available.</p>", status_code=500)
