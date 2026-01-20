"""
Contains the Config class for ENC configuration settings.
"""
from pathlib import Path

import yaml
from cerberus import Validator

from . import files
from . import paths as dcp


class Config:
    """
    Class for managing Electronic Navigational Charts (ENC) configuration settings.

    This class handles loading, validating, and modifying ENC settings 
    defined in a YAML configuration file.
    """

    def __init__(self, config_path: Path | str | None = None):
        """
        Initializes the Config object.

        If no config_path is provided, it defaults to the path defined in the 'paths' module.

        :param config_path: Path to the configuration file (YAML format).
        """
        if config_path is None:
            config_path = dcp.config
        self._schema = read_yaml_into_dict(dcp.config_schema)
        self.validator = Validator(self._schema)
        self._valid_sections = self._extract_valid_sections()
        self._settings = None
        self.parse(config_path)


    @property
    def settings(self) -> dict:
        """
        Gets the current settings.

        :return: A dictionary containing the current configuration settings.
        """
        return self._settings


    @settings.setter
    def settings(self, new_settings: dict) -> None:
        """
        Sets new settings.

        :param new_settings: A dictionary containing the new configuration settings.
        """
        self._settings = new_settings


    def _extract_valid_sections(self) -> list[str]:
        """
        Extracts the valid sections defined in the configuration schema.

        :return: A list of valid section names from the configuration schema.
        :raises ValueError: If the schema is not provided.
        """
        if self._schema is None:
            raise ValueError("No configuration schema provided!")
        sections = []
        for section in self._schema.keys():
            sections.append(section)
        return sections


    def validate_settings(self) -> None:
        """
        Validates the provided assigned settings against the schema.
        :raises ValueError: If the settings are empty, schema is empty, 
                            or validation fails.
        """
        if not self._settings:
            raise ValueError("Empty settings!")

        if not self._schema:
            raise ValueError("Empty schema!")

        if not self.validator.validate(self._settings):
            raise ValueError(f"Cerberus validation Error: " f"{self.validator.errors}")

        self._settings.get("enc", {}).get("depths", []).sort()
        for file_name in self._settings.get("enc", {}).get("files", []):
            files.verify_directory_exists(file_name)


    def parse(self, file_name: Path | str = dcp.config) -> None:
        """
        Parses the YAML configuration file and validates the settings.

        :param file_name: Path to the YAML configuration file. Defaults to the path defined in 'paths'.
        """
        self._settings = read_yaml_into_dict(file_name)
        self.validate_settings()


def read_yaml_into_dict(file_name: Path | str = dcp.config) -> dict:
    """
    Reads a YAML file and converts it into a dictionary.

    :param file_name: Path to the YAML file to read.
    :return: A dictionary containing the contents of the YAML file.
    """
    with open(file_name, encoding="utf-8") as config_file:
        output_dict = yaml.safe_load(config_file)
    return output_dict
