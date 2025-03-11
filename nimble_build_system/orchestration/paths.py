"""
This module to defines the paths used by orchestration scripts
"""

import os
import logging


ABS_PATH = os.path.abspath(os.getcwd())
logging.info(f"Path: {ABS_PATH}")
# MODULE_PATH = ABS_PATH
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
# BUILD_DIR = os.path.join(MODULE_PATH, "build")
#REL_MECH_DIR = os.path.relpath(os.path.join(MODULE_PATH, "mechanical"), BUILD_DIR)
REL_MECH_DIR = os.path.join(ABS_PATH, "mechanical")
logging.info(f"Path: {os.path.abspath(os.getcwd())}")
# logging.info(f"{MODULE_PATH}")
# logging.info(f"{BUILD_DIR}")
logging.info(f"{REL_MECH_DIR}")