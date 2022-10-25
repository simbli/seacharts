"""Contains functionality for reading, processing and validating seacharts configuration settings"""
from typing import List, Tuple

import yaml
from cerberus import Validator

from . import paths as path


def validate(settings) -> None:
    if not settings:
        raise ValueError("Empty settings!")

    with open(path.config_schema, encoding='utf-8') as config_schema:
        schema = yaml.safe_load(config_schema)

    validator = Validator(schema)
    return validator.validate(settings)


def parse(file_name=path.config) -> dict:

    settings = read(file_name)

    validate(settings)

        # key = 'layers'
        # if self.layers is None:
        #     self.layers = utils.config.parse(key, defaults)
        # utils.config.validate(key, self.layers, list, str)
        # for layer in self.layers:
        #     if layer.capitalize() not in spl.supported_layers:
        #         raise ValueError(
        #             f"Feature '{layer}' not supported, "
        #             f"possible candidates are: {spl.supported_layers}"
        #         )

        # key = 'depths'
        # if self.depths is None:
        #     default = utils.config.parse(key, defaults)
        #     self.depths = [int(v) for v in default]
        # utils.config.validate(key, self.depths, list, int)
        # if any(d < 0 for d in self.depths):
        #     raise ValueError(
        #         "Depth bins should be non-negative."
        #     )
        # self.depths.sort()

        # key = 'files'
        # if self.files is None:
        #     self.files = utils.config.parse(key, defaults)
        # utils.config.validate(key, self.files, list, str)
        # for file_name in self.files:
        #     utils.files.verify_directory_exists(file_name)

    return settings


def read(file_name=path.config) -> dict:
    with open(file_name, encoding='utf-8') as config_file:
        settings = yaml.safe_load(config_file)
    return settings


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
