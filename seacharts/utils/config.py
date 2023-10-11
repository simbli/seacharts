"""Contains functionality for reading, processing and validating seacharts configuration settings"""
from pathlib import Path
from typing import List

import yaml
from cerberus import Validator

from . import files
from . import paths as dcp  # default configuratin paths


class ENCConfig:
    """Class for maintaining Electronic Navigational Charts configuration settings"""

    def __init__(self, config_file_name: Path = dcp.config, **kwargs):

        self._schema = read_yaml_into_dict(dcp.config_schema)
        self.validator = Validator(self._schema)
        self._valid_sections = self.extract_valid_sections()

        self.parse(config_file_name)
        self.override(**kwargs)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new_settings: dict):
        self._settings = new_settings

    def extract_valid_sections(self) -> List[str]:
        if self._schema is None:
            raise ValueError("No configuration schema provided!")

        sections = []
        for section in self._schema.keys():
            sections.append(section)
        return sections

    def validate(self, settings: dict) -> None:
        if not settings:
            raise ValueError("Empty settings!")

        if not self._schema:
            raise ValueError("Empty schema!")

        if not self.validator.validate(settings):
            raise ValueError(f"Cerberus validation Error: {self.validator.errors}")

        self._settings["enc"]["depths"].sort()

        for file_name in self._settings["enc"]["files"]:
            files.verify_directory_exists(file_name)

    def parse(self, file_name=dcp.config) -> None:
        self._settings = read_yaml_into_dict(file_name)
        self.validate(self._settings)

    def override(self, section="enc", **kwargs) -> None:
        if not kwargs:
            return

        if section not in self._valid_sections:
            raise ValueError("Override settings in non-existing section!")

        new_settings = self._settings
        for key, value in kwargs.items():
            new_settings[section][key] = value

        self.validate(new_settings)

        self._settings = new_settings


def read_yaml_into_dict(file_name=dcp.config) -> dict:
    with open(file_name, encoding="utf-8") as config_file:
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
            raise ValueError("Invalid input format: " f"'{key}' should be a {v_type.__name__} of {sub_type}.")
        if length is not None and len(value) != length:
            raise ValueError("Invalid input format: " f"'{key}' should be a {v_type.__name__} of length {length}.")
    else:
        if not isinstance(value, v_type):
            raise ValueError("Invalid input format: " f"'{key}' should have type {v_type}.")


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
