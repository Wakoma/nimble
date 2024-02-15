
from orchestration import OrchestrationRunner


def generate_docs(config, config_hash, force_rebuild=True):
    """
    generate all models and update documentation
    """

    print("Starting build for config_hash: " + config_hash)
    runner = OrchestrationRunner(config, config_hash, force_rebuild=force_rebuild)

    print("Setting up build environment")
    runner.setup()

    print("Running orchestration")
    runner.generate_exsource_files()

    print("Running exsource make")
    runner.run_exsource()

    # todo: write gitbuilding files

    print("Creating zip file")
    runner.create_zip()

    print("Finished build for config_hash: " + config_hash)


# if main script, run generate_docs with test config
if __name__ == "__main__":
    config = {'config': {'server_1': 'Hardware_1', 'router_1': 'Hardware_2', 'switch_1': 'Hardware_9', 'charge_controller_1': 'Hardware_4'}}
    generate_docs(config, "test_config_hash")
