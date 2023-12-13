import os, sys
import json
import hashlib

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

# Allow imports from the parent directory (potential security issue)
sys.path.append(os.path.dirname(__file__) + "/..")

# TODO: Andreas to fix this
from generate_dummy import generate_docs

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
    config = await request.json()

    # Generate a hash of the configuration here to identify it
    m = hashlib.sha256()
    m.update(json.dumps(config, sort_keys=True).encode('utf-8'))
    config_hash = "hash_" + str(m.digest()).replace("\\", "_").replace("b'", "").replace("'", "")

    # TODO: Andreas to fix this
    # Trigger the orchestration script
    generate_docs(config, config_hash)

    # Make sure that there is a valid config before passing it on to the orchestration script
    if config is not None and "config" in config.keys() and "server_1" in config["config"].keys():
        return ORJSONResponse([{"redirect": "/wakoma/nimble/auto-doc/" + config_hash, "description": "Poll this URL until your documentation package is ready."}])
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
    from models.cadquery.rack_leg import make_rack_leg

    # Generate the rack leg
    leg = make_rack_leg(length, hole_spacing, long_axis_hole_dia, mounting_holes_dia).cq()

    # Figure out what the file name and temporary path should be
    export_file_name = "leg_length-" + str(length) + "_hole_spacing-" + str(hole_spacing) + "_long_axis_hole_dia-" + str(long_axis_hole_dia) + "_mounting_holes_dia-" + str(mounting_holes_dia) + "." + model_format
    export_path = os.path.join("/tmp", export_file_name)

    # If the leg does not already exist, export it to a temporary file
    if not os.path.exists(export_path):
        cq.exporters.export(leg, export_path)

    return FileResponse(export_path, headers={'Content-Disposition': 'attachment; filename=' + export_file_name})
