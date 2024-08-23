import pytest
import os

def test_cadorchestrator_command_line():
    """
    Test the command line interface for the cadorchestrator
    """
    import subprocess
    import os
    import shutil

    # This represents the local build directory created by the generate command
    build_dir = os.path.join(".", "build")

    # Remove the existing build directory before regenerating
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    if "PYTHONPATH" in os.environ:
        py_path = os.getcwd() + ":" + os.environ["PYTHONPATH"]
    else:
        py_path = None

    # Run the cadorchestrator with the test configuration file
    if py_path == None:
        result = subprocess.run(["cadorchestrator", "generate", "[\"NUC10i5FNH\", \"Raspberry_Pi_4B\", \"Raspberry_Pi_4B\"]"])
    else:
        result = subprocess.run(["cadorchestrator", "generate", "[\"NUC10i5FNH\", \"Raspberry_Pi_4B\", \"Raspberry_Pi_4B\"]"], env=dict(PYTHONPATH=py_path))

    # Make sure that the command ran successfully
    assert result.returncode == 0

    # Check that the correct output files were generated
    assert os.path.exists(build_dir)
    assert os.path.exists(os.path.join(".", "build", "printed_components", "shelf_h2_--rpi_shelf.step"))
    assert os.path.exists(os.path.join(".", "build", "printed_components", "shelf_h2_--rpi_shelf.stl"))
    assert os.path.exists(os.path.join(".", "build", "printed_components", "shelf_h4_--nuc_tall.step"))
    assert os.path.exists(os.path.join(".", "build", "printed_components", "shelf_h4_--nuc_tall.stl"))
