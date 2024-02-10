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


# http://127.0.0.1:8000/wakoma/nimble/rack_leg?length=50.0&model_format=stl
@app.get("/wakoma/nimble/rack_leg")
def read_item(length: float = 294.0, hole_spacing: float = 14.0, long_axis_hole_dia: float = 4.6, mounting_holes_dia:float = 3.6, model_format: str = "stl"):
    """
    Provides access to the individual parameterized model of a rack leg.
    """
    # Check to make sure the user requested a valid model format
    if not check_model_format(model_format):
        return HTMLResponse('ERROR: Model format not supported. <a href="https://7bindustries.com/hardware/rack_leg_download.html">Try Again</a>')

    # Check to make sure the user has not set a length that is too long
    if length > 1000:
        return HTMLResponse('ERROR: Length parameter is too large. <a href="https://7bindustries.com/hardware/rack_leg_download.html">Try Again</a>')

    # Make sure that the hole spacing is valid
    if hole_spacing <= 0.0 or hole_spacing >= length or hole_spacing <= mounting_holes_dia:
         return HTMLResponse('ERROR: Invalid hole_spacing parameter. <a href="https://7bindustries.com/hardware/rack_leg_download.html">Try Again</a>')

    # Make sure that the long axis hole diameter is valid
    if long_axis_hole_dia <= 0.0 or long_axis_hole_dia >= 20.0:
        return HTMLResponse('ERROR: Invalid long_axis_hole_dia parameter. <a href="https://7bindustries.com/hardware/rack_leg_download.html">Try Again</a>')

    # Make sure that the mounting hole diameter is valid
    if mounting_holes_dia <= 0.0 or mounting_holes_dia >= 20.0:
        return HTMLResponse('ERROR: Invalid mounting_holes_dia parameter. <a href="https://7bindustries.com/hardware/rack_leg_download.html">Try Again</a>')

    import cadquery as cq
    from mechanical.components.cadquery.rack_leg import make_rack_leg

    # Generate the rack leg
    leg = make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia).cq()

    # Figure out what the file name and temporary path should be
    export_file_name = "leg_length-" + str(length) + "_hole_spacing-" + str(hole_spacing) + "_long_axis_hole_dia-" + str(long_axis_hole_dia) + "_mounting_holes_dia-" + str(mounting_holes_dia) + "." + model_format
    export_path = os.path.join(tempfile.gettempdir(), export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(leg, export_path)

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
