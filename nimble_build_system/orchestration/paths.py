"""
This module to defines the paths used by orchestration scripts
"""

import os

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
BUILD_DIR = os.path.join(MODULE_PATH, "build")
REL_MECH_DIR = os.path.relpath(os.path.join(MODULE_PATH, "mechanical"), BUILD_DIR)
