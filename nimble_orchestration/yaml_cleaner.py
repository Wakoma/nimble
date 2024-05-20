"""
A module containting functions to clean up dictionaries before writing to yaml file.
"""

import pathlib


def clean(data: dict) -> dict:
    """
    Clean the input dictionary (recursively). Removing any keys where the value is
    none, changing pathlib.Path to strings and converting tuples to strings.

    The input is a single dictionary, the output is a cleaned dictionary.
    """
    # iterate over entries
    keys_to_delete = []
    for key, value in data.items():
        # remove empty entries
        if value is None:
            keys_to_delete.append(key)
        else:
            data[key] = _clean_object(value)
    # delete empty entries
    for key in keys_to_delete:
        del data[key]
    return data


def _clean_object(obj: object) -> object:
    # clean up lists
    if isinstance(obj, list):
        return [_clean_object(x) for x in obj]
    # clean up dicts
    if isinstance(obj, dict):
        return clean(obj)
    if isinstance(obj, tuple):
        # convert to string like "(1,2,3)"
        return str(obj)
    if isinstance(obj, pathlib.Path):
        # convert to string
        return str(obj)
    return obj
