#! /usr/bin/env python

"""
Run orchestration script with specified config 
"""

from nimble_orchestration.orchestration import OrchestrationRunner, NimbleConfiguration

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
    selected_devices_ids = ['NUC10i5FNH', 'RPi4', 'RPi4']
    generate(selected_devices_ids)

if __name__ == "__main__":
    generate_example_configuration()
