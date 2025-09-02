"""
This module to defines the paths used by orchestration scripts
"""

import os
import logging


ABS_PATH = os.path.abspath(os.getcwd())
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
REL_MECH_DIR = os.path.join(ABS_PATH, "mechanical")
BUILD_DIR = os.path.join(MODULE_PATH, "build")


logging.info(f"{ABS_PATH}\n\t\t\t\t\t{MODULE_PATH}\n\t\t\t\t\t{REL_MECH_DIR}")