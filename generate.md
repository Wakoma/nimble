<!--
SPDX-FileCopyrightText: 2023 Andreas Kahler <mail@andreaskahler.com>

SPDX-License-Identifier: CERN-OHL-S-2.0
-->

# Automatic generation of configured Nimble hardware

## Overview

Nimble hardware models are generated using Python. For CAD we used [CadQuery](https://cadquery.readthedocs.io/en/latest/intro.html). CadQuery scripts can be found in the `mechanical` directory, with individual components in the `mechanical/components/cadquery` directory. Our CadQuery scripts also use the `nimble-builder` module of helper functions.

Our preferred way to generate the models needed for a nimble configuration is via our orchestration module `nimble-orchestration`. This can be used to generate trays for networking components, nimble-rack components, and a final CAD assembly. The orchestration system uses [cq-cli](https://github.com/CadQuery/cq-cli) to execute CadQuery scripts, and [ExSource Tools](https://gitlab.com/gitbuilding/exsource-tools) to manage the process of turning scripts into useable models. The orchestration script will eventually use [GitBuilding](https://gitbuilding.io) to generate assembly manuals.


## Installation

You must have [Python 3.8](https://www.python.org/about/gettingstarted/) or higher installed on your system and also have pip installed. We recommend that you use a [Python virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for interacting with nimble.

Clone or download this repository to your computer

Open a terminal (for example PowerShell in Windows) and navigate to this repository

Run:

    pip install -e .

*Note, if pip doesn't work depending on your system is configured you man need to replace `pip` with `pipx`, `pip3`, or `python -m pip`.*

*Also note: The `-e` is optional. It allows you to adjust the code in `nimble-builder` or `nimble-orchestration` without having to run the installation again.*


## Running the code

As the code is very much a work in progress we do not have detailed documentation of how to run it for custom configurations.

For now the best way to run the code is with the two scripts in this repository.

### Generate static

The script `generate-static.py` is used to create a number of example components for a Nimble rack. The script is not trying to support any specific configuration, but is instead being developed to provide a static library interface for which a large number of Nimble components can be downloaded.

To run this script, run the following command:

    python generate_static.py

This should create the `build` directory. Inside this the `printed_components` directory should contain a number of `stl` files that can be 3D printed.

The script also creates a simple web-page with an index of all of the files. The final link to the "Partially complete automatically generated documentation" will be broken unless you also run `generate.py` (see below).

It also creates a number of files that are used by the orchestration script.

If you don't want to run this locally you can see a [hosted version of the output](https://wakoma.github.io/nimble/).


### Generate configuration

The script `generate.py` is our test-bed script for generating a complete set of information for a nimble configuration.

Currently the configuration is just a list of the networking components which are hard coded. At a future date it should be possible to pass a configuration and other parameters to this script.

To run this script, run the following command:

    python generate.py

This should create the `build` directory. Inside this the `printed_components` directory should contain a number of `step` files that can be 3D printed (you may need to convert them to `stl` files first).

The script also creates an `stl` and a `gltf` of the final assembled rack. **Don't print this, it is not going to print properly as one piece!**

It also creates a number of files that are used by the orchestration script.

At a later date this script will be improved to create a directory (and associated zip-file of each configuration).
