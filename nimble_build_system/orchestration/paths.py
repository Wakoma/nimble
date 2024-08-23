"""
This module to defines the paths used by orchestration scripts
"""

import os
from pathlib import Path

# MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
MODULE_PATH = Path(__file__).parent.parent.parent
BUILD_DIR = os.path.join(MODULE_PATH, "build")
REL_MECH_DIR = os.path.relpath(os.path.join(MODULE_PATH, "mechanical"), BUILD_DIR)
