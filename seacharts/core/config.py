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
    Class for maintaining Electronic Navigational Charts configuration settings.
    """

    def __init__(self, config_path: Path | str = None):
        if config_path is None:
            config_path = dcp.config
        self._schema = read_yaml_into_dict(dcp.config_schema)
        self.validator = Validator(self._schema)
        self._valid_sections = self._extract_valid_sections()
        self._settings = None
        self.parse(config_path)

    @property
    def settings(self) -> dict:
        return self._settings

    @settings.setter
    def settings(self, new_settings: dict) -> None:
        self._settings = new_settings

    def _extract_valid_sections(self) -> list[str]:
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
            raise ValueError(f"Cerberus validation Error: " f"{self.validator.errors}")

        self._settings["enc"].get("depths", []).sort()
        for file_name in self._settings["enc"].get("files", []):
            files.verify_directory_exists(file_name)

    def parse(self, file_name: Path | str = dcp.config) -> None:
        self._settings = read_yaml_into_dict(file_name)
        self.validate(self._settings)

    def override(self, section: str = "enc", **kwargs) -> None:
        if not kwargs:
            return
        if section not in self._valid_sections:
            raise ValueError("Override settings in non-existing section!")

        new_settings = self._settings
        for key, value in kwargs.items():
            new_settings[section][key] = value
        self.validate(new_settings)
        self._settings = new_settings


def read_yaml_into_dict(file_name: Path | str = dcp.config) -> dict:
    with open(file_name, encoding="utf-8") as config_file:
        output_dict = yaml.safe_load(config_file)
    return output_dict
