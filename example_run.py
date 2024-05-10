# Because I don't want to fill out the directory structure for relative imports right now
import sys
import os
from pathlib import Path
temp_path = Path(os.path.abspath(__file__))
append_path = temp_path.parent.parent.absolute()
sys.path.append(append_path)
print(sys.path)

from generate import generate_docs
import json
import re

# A sample, hard-coded configuration
config = json.loads('{"config": {"server_1": "Hardware_1", "router_1": "Hardware_2", "switch_1": "Hardware_9", "charge_controller_1": "Hardware_4"}}')['config']

# Construct the config hash
config_hash = "+".join([f"{key}={config[key]}" for key in sorted(config.keys())])
config_hash = re.sub(r'[^a-zA-Z0-9_+=]', '', config_hash)

print("config_hash is: " + config_hash)

# Call the generation code
generate_docs(config, config_hash)
