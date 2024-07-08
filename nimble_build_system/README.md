The nimble build system is a python module containing custom functionality for building the nimble hardware.

This is divided into three sub-packages:

* `cad` - This containts any helper functions for building the Nimble CAD models. This does not contain the scripts for generating specific CAD models and assemblies. These are held in the `mechanical` directory of the repository.
* `orchestration` - This contains code for the Nimble project's interaction with [CadOrchestrator](https://gitlab.com/gitbuilding/cadorchestrator)
* `utils` - This contains scripts assorted utility scripts, for example for updating the json configuration files.
