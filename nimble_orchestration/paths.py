"""
This module to defines the paths used by orchestration scripts
"""

import os

MODULE_PATH = os.path.normpath(os.path.join(os.path.split(__file__)[0], '..'))
BUILD_DIR = os.path.join(MODULE_PATH, "build")
REL_MECH_DIR = os.path.relpath(os.path.join(MODULE_PATH, "mechanical"), BUILD_DIR)
DOCS_DIR = os.path.join(MODULE_PATH, "documentation")
DOCS_TMP_DIR = os.path.join(MODULE_PATH, "_gb_temp_")
