import os, sys
import re
import json
import hashlib
import tempfile
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

# Change this to the base URL of the server that is serving this app
server_base_url = "http://127.0.0.1:8000"

# Used to keep track of the configurations that are being, or have been, generated
generated_docs_urls = {}

# Allow imports from the parent directory (potential security issue)
sys.path.append(os.path.dirname(__file__) + "/..")

from generate import generate_docs

app = FastAPI()

# Static files for the test page
app.mount("/static", StaticFiles(directory="static"), name="static")


# http://127.0.0.1:8000/wakoma/nimble/test_page
@app.get("/wakoma/nimble/test_page")
async def read_index():
    """
    Loads a sample page so that the system can be tested end-to-end.
    """

    return FileResponse('test_page.html')


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

    print("Starting build for config:")
    print(config)

    # Generate a hash of the configuration here to identify it
    # sort config by key, get "key=value" strings, concatenate
    config_hash = "+".join([f"{key}={config[key]}" for key in sorted(config.keys())])
    # delete all non-alphanumeric characters (other than _+=)
    config_hash = re.sub(r'[^a-zA-Z0-9_+=]', '', config_hash)
    
    print("config_hash is: " + config_hash)

    # If the build has been performed before, send the cached file to speed the system up
    module_path = Path(__file__).resolve().parent.parent
    build_path = module_path  / "build" / config_hash
    if not os.path.exists(str(build_path) + ".zip"):
        # Trigger the orchestration script
        generate_docs(config, config_hash)

    # Make sure that there is a valid config before passing it on to the orchestration script
    if config is not None and "server_1" in config.keys():
        # Save this generated config so that it can be polled
        generated_docs_urls[config_hash] = server_base_url + "/wakoma/nimble/auto-doc?config_hash=" + urllib.parse.quote(config_hash)

        return ORJSONResponse([{"redirect": generated_docs_urls[config_hash], "description": "Poll this URL until your documentation package is ready."}])
    else:
        return ORJSONResponse([{"error": "Configuration must be a valid JSON object."}])



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

    # Run the script with customized parameters
    tray = cqgi_model_script("nimble_tray.py", {"height_in_hole_unites": number_of_units, "tray_width": tray_width, "tray_depth": tray_depth})

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
def get_files(config_hash):
    """
    Loads any auto-generated documentation files.
    """

    # Figure out what the build path is
    module_path = Path(__file__).resolve().parent.parent
    build_path = module_path  / "build" / config_hash

    # Once the build exists we can send it to the user, but before that we give them a temporary redirect
    if os.path.exists(str(build_path) + ".zip"):
        return FileResponse(str(build_path) + ".zip", headers={'Content-Disposition': 'attachment; filename=' + config_hash + ".zip"})
    else:
        return HTMLResponse(content="<p>The File is Still Processing</p>", status_code=307)

@app.get("/wakoma/nimble/preview")
def get_preview(config_hash):
    """
    Sends the auto-generated glTF file back to the caller.
    """

    
