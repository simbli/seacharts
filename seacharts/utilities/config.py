import configparser

from . import paths as path


def read_settings(file_name=path.config ,category='USER') -> dict:
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


def parse(key, defaults):
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
