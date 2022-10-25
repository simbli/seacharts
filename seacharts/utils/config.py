"""Contains functionality for reading, processing and validating seacharts configuration settings"""
import configparser
from typing import List, String, Tuple

from . import paths as path


def validate_settings(settings, defaults) -> None:
    """Checks if the settings contain the minimum required parameters, and with valid values.

    Args:
        settings (dict): _description_
        defaults (dict): _description_
    """
    required_values = {
        'size': Tuple(float, float),
        'center': Tuple(float, float),
        'buffer': int,
        'tolerance': float,
        'layers': List[float],
        'depths': List[float],
        'files': List[String],
        'new_data': bool,
        'raw_data': bool,
        'border': bool,
        'verbose': bool,
        'center_lla': Tuple(float, float)
    }

    # FIX 1 SETTINGS; DROP DEFAULT SHITEN

    for key, value in required_values.items():
        if settings[key] is None:
            settings[key] = defaults[key]
        if settings[key] is None:


def validate_display_settings(settings):



def parse(file_name=path.config) -> Tuple[dict, dict]:
    """Parses a configuration file and returns the seacharts settings, split into user, default and display settings. Keys not provided by the user are defaulted.

    Args:
        file_name (str, optional): Absolute path to configuration file. Defaults to path.config.

    Returns:
        Tuple(dict, dict, dict): Configuration settings tuple of user and default settings, and display settings.
    """
    settings = read_settings(file_name, category='USER')
    defaults = read_settings(file_name, category='DEFAULT')

    validate_settings(settings, defaults)
    key = 'buffer'
        if settings['buffer'] is None:
            default = parse_key(key, defaults)
            self.buffer = int(default[0])
            utils.config.validate(key, self.buffer, int)
        if self.buffer < 0:
            raise ValueError(
                "Buffer should be a non-negative integer."
            )

        key = 'tolerance'
        if self.tolerance is None:
            default = utils.config.parse(key, defaults)
            self.tolerance = int(default[0])
        utils.config.validate(key, self.tolerance, int)
        if self.tolerance < 0:
            raise ValueError(
                "Tolerance should be a non-negative integer."
            )

        key = 'layers'
        if self.layers is None:
            self.layers = utils.config.parse(key, defaults)
        utils.config.validate(key, self.layers, list, str)
        for layer in self.layers:
            if layer.capitalize() not in spl.supported_layers:
                raise ValueError(
                    f"Feature '{layer}' not supported, "
                    f"possible candidates are: {spl.supported_layers}"
                )

        key = 'depths'
        if self.depths is None:
            default = utils.config.parse(key, defaults)
            self.depths = [int(v) for v in default]
        utils.config.validate(key, self.depths, list, int)
        if any(d < 0 for d in self.depths):
            raise ValueError(
                "Depth bins should be non-negative."
            )
        self.depths.sort()

        key = 'files'
        if self.files is None:
            self.files = utils.config.parse(key, defaults)
        utils.config.validate(key, self.files, list, str)
        for file_name in self.files:
            utils.files.verify_directory_exists(file_name)

        key = 'new_data'
        if self.new_data is None:
            default = utils.config.parse(key, defaults)
            self.new_data = bool(int(default[0]))
        utils.config.validate(key, self.new_data, bool)

        key = 'raw_data'
        if self.raw_data is None:
            default = utils.config.parse(key, defaults)
            self.raw_data = bool(int(default[0]))
        utils.config.validate(key, self.raw_data, bool)

        key = 'border'
        if self.border is None:
            default = utils.config.parse(key, defaults)
            self.border = bool(int(default[0]))
        utils.config.validate(key, self.border, bool)

        key = 'verbose'
        if self.verbose is None:
            default = utils.config.parse(key, defaults)
            self.verbose = bool(int(default[0]))
        utils.config.validate(key, self.verbose, bool)

        utils.config.save(dict(
            size=self.extent.size,
            center=self.extent.center,
            buffer=self.buffer,
            tolerance=self.tolerance,
            layers=self.layers,
            depths=self.depths,
            files=self.files,
            new_data=int(self.new_data),
            raw_data=int(self.raw_data),
            border=int(self.border),
            verbose=int(self.verbose),
        ), utils.paths.config)

    display = read_settings(file_name, category='DISPLAY')
    return settings, defaults, display


def read_settings(file_name=path.config, category='USER') -> dict:
    """Reads configuration settings for a given category from file

    Args:
        file_name (str, optional): Configuration file. Defaults to path.config.
        category (str, optional): Considered settings category. Defaults to 'USER'.

    Returns:
        dict: Dictionary of configuration settings.
    """
    settings = {}
    config = configparser.ConfigParser()
    config.read(file_name, encoding='utf8')
    for key, value in config[category].items():
        settings[key] = [v.strip(' ') for v in value.split(',')]


    return settings


def save(kwargs, file_name) -> None:
    """Saves configuration with values given by kwargs, in file file_name.

    Args:
        file_name (str): Absolute path to the configuration file
        kwargs (dict): Dictionary representing the configuration
    """
    config = configparser.ConfigParser()
    user_strings = {}
    for key, value in kwargs.items():
        if isinstance(value, tuple) or isinstance(value, list):
            string = ', '.join([str(v) for v in value])
        else:
            string = str(value)
        user_strings[key] = string
    config['USER'] = user_strings
    with open(file_name, 'w', encoding='utf8') as configfile:
        config.write(configfile)


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


def validate(key, value, v_type, sub_type=None, length=None) -> None:
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
