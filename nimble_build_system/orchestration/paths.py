"""
This module to defines the paths used by orchestration scripts
"""

import os
import logging


ABS_PATH = os.path.abspath(os.getcwd())
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
REL_MECH_DIR = os.path.join(ABS_PATH, "mechanical")
BUILD_DIR = os.path.join(ABS_PATH, "build")


logging.info("%s\n\t%s\n\t%s", ABS_PATH, MODULE_PATH, REL_MECH_DIR)
