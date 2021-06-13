import configparser

from . import paths as path


def read_settings(category='USER'):
    settings = {}
    config = configparser.ConfigParser()
    config.read(path.config, encoding='utf8')
    for key, value in config[category].items():
        settings[key] = [v.strip(' ') for v in value.split(',')]
    return settings


def save(kwargs):
    config = configparser.ConfigParser()
    config.read(path.config, encoding='utf8')
    user_strings = {}
    for key, value in kwargs.items():
        if isinstance(value, tuple) or isinstance(value, list):
            string = ', '.join([str(v) for v in value])
        else:
            string = str(value)
        user_strings[key] = string
    config['USER'] = user_strings
    with open(path.config, 'w', encoding='utf8') as configfile:
        config.write(configfile)


def parse(key, defaults):
    default = defaults.get(key, None)
    if default is None:
        raise ValueError(
            f"Missing input parameter: '{key}': was not provided, "
            f"and could not located in the current configuration file."
        )
    return default


def validate(key, value, v_type, sub_type=None, length=None):
    if isinstance(value, list) or isinstance(value, tuple):
        if not all([isinstance(v, sub_type) for v in value]):
            raise ValueError(
                f"Invalid input format: "
                f"'{key}' should be a {v_type.__name__} of {sub_type}."
            )
        if length is not None and len(value) != length:
            raise ValueError(
                f"Invalid input format: "
                f"'{key}' should be a {v_type.__name__} of length {length}."
            )
    else:
        if not isinstance(value, v_type):
            raise ValueError(
                f"Invalid input format: "
                f"'{key}' should have type {v_type}."
            )
