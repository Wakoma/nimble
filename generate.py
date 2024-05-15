#! /usr/bin/env python

"""
This script is in development. It is being developed to
create and bundle all STLs (and eventually all documentation)
for a specific nimble configuration.
"""

from nimble_orchestration.orchestration import OrchestrationRunner
from nimble_orchestration.configuration import NimbleConfiguration

def generate(selected_devices_ids):
    """
    This will eveneually generate everything needed for a specific nimble
    configuration including, STL files, renders, of assembly steps, and assembly
    documentation. Currently it only creates the rack components.
    """

    config = NimbleConfiguration(selected_devices_ids)

    print("Starting build")
    runner = OrchestrationRunner()

    print("Generating components")
    runner.generate_components(config.components)

    runner.generate_assembly(config.assembly_definition)


def generate_example_configuration():
    """
    Generate the trays and assembly model for a simple set of devices
    """
    selected_devices_ids = ['NUC10i5FNH', 'Raspberry_Pi_4B', 'Raspberry_Pi_4B']
    generate(selected_devices_ids)

if __name__ == "__main__":
    generate_example_configuration()
