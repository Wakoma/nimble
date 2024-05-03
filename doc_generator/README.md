<!--
SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>

SPDX-License-Identifier: CERN-OHL-S-2.0
-->

# nimble smart-doc

This is the base directory for the "smart-doc" project which aims to have a automated workflow creating assembly instructions for custom Nimble setups.

This is work in progress. Here are some links on where to find further information:

* Jeremy did a blog post about this: [First Nimble Project Update](https://7bindustries.com/blog/nimble_project_1.html)
* This project is funded by  NLnet Foundation! See their announcemnt [here](https://nlnet.nl/project/HardwareManuals/).
* Github [project plan](https://github.com/orgs/Wakoma/projects/7)
* See this [pull request](https://github.com/Wakoma/nimble/pull/23) to follow along current implementation status

# Output

Currently this branch triggers the creation of STLs built using our workflow.

See lastest version here: https://wakoma.github.io/nimble/


# Orchestration script

The orchestration script is the central component of the workflow.

* It is passed in a nimble configuration
* It triggers building 3d models in STL and STEP format from CadQuery/CadScript code
* It triggers rendering of diagrams/views of these models and assemblies including them (also done with Cadquery functionality)
* It triggers creation of assembly manuals using GitBuilding

## Python modules

(Please note that this is all work in progress)

* generate.py runs the orchestration script with a specified nimble config 
* generate_static.py generates a bunch of STL files to show case the possiblilties of the nimble cadquery code. This is temporarily used to build github pages available at https://wakoma.github.io/nimble/
* orchestrations.py implements the OrchestrationRunner class, used by generate.py and generate_static.py

## Dependencies

Run the following in a Python virtual environment to install the dependencies.

```
pip install -r requirements.txt
```

## Usage

generate.py currently can be run without arguments to create 3d models for an example configuration.
This later will be enhanced with the possibility to pass in configurations using devices from a database of supported equipment.

There is also a python based web server back end that use the orchestration script. Please refer to the server sub folder for details.