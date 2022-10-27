"""Contains functionality for reading, processing and validating seacharts configuration settings"""
import yaml
from cerberus import Validator

from . import files
from . import paths as path


class ENCConfig:
    settings = None
    _schema = None

<<<<<<< HEAD
    def __init__(self, config_file_name: str = path.config, **kwargs):
=======
    def __init__(self, config_file_name: str = path.config):
>>>>>>> def759c266485e5c09fe06424fdc5b9bb3813001

        self._schema = self.read_yaml_into_dict(path.config_schema)

        self.parse(config_file_name)

<<<<<<< HEAD
        self.override(**kwargs)

    @property
    def settings(self):
        return self.settings

    def validate(self, settings: dict) -> None:
        if not settings:
            raise ValueError("Empty settings!")

        if not self._schema:
            raise ValueError("Empty schema!")

        validator = Validator(self._schema)
        res = validator.validate(settings)

=======
    @property
    def settings(self):
        return self.settings

    def validate(self, settings: dict) -> None:
        if not settings:
            raise ValueError("Empty settings!")

        if not self._schema:
            raise ValueError("Empty schema!")

        validator = Validator(self._schema)
        res = validator.validate(settings)

>>>>>>> def759c266485e5c09fe06424fdc5b9bb3813001
        if res is not True:
            raise ValueError(f"Cerberus: {validator.errors}")


    def parse(self, file_name=path.config) -> None:

        self.settings = read_yaml_into_dict(file_name)
        self.validate(self.settings)

        if any(d < 0 for d in self.settings['enc']['depths']):
            raise ValueError(
                "Depth bins should be non-negative."
            )
        self.settings['enc']['depths'].sort()

        for file_name in self.settings['enc']['files']:
            files.verify_directory_exists(file_name)

<<<<<<< HEAD
    def override(self, **kwargs) -> None:
        new_settings = self.settings

        for key, new_val in kwargs.items():
            for section, value in self._schema.items():
                for key, sub_val in self._schema.items():

=======
    def validate_runtime_provided_settings(self, defaults, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in defaults.items():
>>>>>>> def759c266485e5c09fe06424fdc5b9bb3813001



def read_yaml_into_dict(file_name=path.config) -> dict:
    with open(file_name, encoding='utf-8') as config_file:
        output_dict = yaml.safe_load(config_file)
    return output_dict


def parse_key(key, defaults):
    """Returns default config parameter value for a given key, if it exists.

    Args:
        key (str): Key (parameter name) to parse
        defaults (dict): Dictionary containing default configuration values.

    Raises:
        ValueError: On missing or wrong input key

    Returns:
        Value: Value of parameter in config at the given key
    """
    default = defaults.get(key, None)
    if default is None:
        raise ValueError(
            f"Missing input parameter: '{key}': was not provided, "
            "and could not located in the current configuration file."
        )
    return default


def validate_key(key, value, v_type, sub_type=None, length=None) -> None:
    """Validates type of value at given key to be equal to v_type, or sub_type if value is a list/tuple of len = length.

    Args:
        key (str): Name of parameter to check value for
        value (_type_): Value of parameter in config at the given key
        v_type (_type_): Type of value
        sub_type (_type_, optional): Subtype if value is a list/tuple. Defaults to None.
        length (_type_, optional): Length if value is list/tuple. Defaults to None.

    Raises:
        ValueError: On wrong type of value at the given key.
    """
    if isinstance(value, list) or isinstance(value, tuple):
        if not all([isinstance(v, sub_type) for v in value]):
            raise ValueError(
                "Invalid input format: "
                f"'{key}' should be a {v_type.__name__} of {sub_type}."
            )
        if length is not None and len(value) != length:
            raise ValueError(
                "Invalid input format: "
                f"'{key}' should be a {v_type.__name__} of length {length}."
            )
    else:
        if not isinstance(value, v_type):
            raise ValueError(
                "Invalid input format: "
                f"'{key}' should have type {v_type}."
            )


# def save(kwargs, file_name) -> None:
#     """Saves configuration with values given by kwargs, in file file_name.

#     Args:
#         file_name (str): Absolute path to the configuration file
#         kwargs (dict): Dictionary representing the configuration
#     """
#     config = configparser.ConfigParser()
#     user_strings = {}
#     for key, value in kwargs.items():
#         if isinstance(value, tuple) or isinstance(value, list):
#             string = ', '.join([str(v) for v in value])
#         else:
#             string = str(value)
#         user_strings[key] = string
#     config['USER'] = user_strings
#     with open(file_name, 'w', encoding='utf8') as configfile:
#         config.write(configfile)
