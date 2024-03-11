import pathlib


class YamlCleaner:
    """
    Clean up data before writing to yaml file.
    """
    @classmethod
    def clean(cls, data: dict) -> dict:
        # iterate over entries
        keys_to_delete = []
        for key, value in data.items():
            # remove empty entries
            if value is None:
                keys_to_delete.append(key)
            else:
                data[key] = cls.clean_object(value)
        # delete empty entries
        for key in keys_to_delete:
            del data[key]   
        return data

    @classmethod
    def clean_object(cls, obj: object) -> object:
        # clean up lists
        if isinstance(obj, list):
            return [cls.clean_object(x) for x in obj]
        # clean up dicts
        if isinstance(obj, dict):
            return cls.clean(obj)
        if isinstance(obj, tuple):
            # convert to string like "(1,2,3)"
            return str(obj)
        if isinstance(obj, pathlib.Path):
            # convert to string
            return str(obj)
        return obj