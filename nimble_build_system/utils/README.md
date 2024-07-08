The utilities sub-module of the nimble build system contains scripts that are needed for project specific tasks such as updating config files

## devices_json_updater.py

This converts the CSV that is downloaded from NocoDB into something that can be used by the orchestration/generation scripts. The scripts use the `devices.json` file that is in the root of this repository. This should eventually be replaced by a direct connection via the NocoDB API. This utility requires that it be passed the path to the CSV file to convert.

**Usage:**

```bash
./devices_json_updater.py /full/path/to/NocoDB/CSV/file
```

The `devices.json` file it creates is committed to the repository.

## gen_nimble_conf_options.py

This script used `devices.json` to create the configuration used by CadOrchestrator to set the configuration options that the user can select when generating a nimble.

Assuming that the `nimble_build_system` is installed using setup.py, this script is as an entry point and should be on your PATH.

Starting in the root directory of this project, run:

```bash
gen_nimble_conf_options
```

This will generate the configuration options in the file `OrchestratorConfigOptions.json`. This file is ignored by Git.
