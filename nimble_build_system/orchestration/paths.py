"""
This module to defines the paths used by orchestration scripts
"""

import os
import logging


ABS_PATH = os.path.abspath(os.getcwd())
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
REL_MECH_DIR = os.path.join(ABS_PATH, "mechanical")

logging.info("NIMBLE ABS_PATH: %s", ABS_PATH)
logging.debug("%s\n\t\t\t\t\t%s\n\t\t\t\t\t%s", ABS_PATH, MODULE_PATH, REL_MECH_DIR)