The files in this directory may not be directly imported within the codebase, but are needed anyway. Some may be applications that are run manually by a user, for instance `devices_json_updater.py`.

### devices_json_updater.py

This converts the CSV that is downloaded from NocoDB into something that can be used by the orchastration/generation scripts. The scripts use the `devices.json` file that is in the root of this repository. This should eventually be replaced by a direct connection via the NocoDB API. This utility requires that it be passed the path to the CSV file to convert.

**Usage:**

```bash
./devices_json_updater.py /full/path/to/NocoDB/CSV/file
```
