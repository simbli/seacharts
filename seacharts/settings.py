import configparser
import csv
import os
import pathlib
from dataclasses import dataclass
from typing import Sequence, Union

from . import features as sf
from .display import colors

_environment_features = (
    sf.Seabed,
    sf.Land,
    sf.Shore,
    sf.Shallows,
    sf.Rocks
)
_entity_features = (
    sf.Ship,
)
supported_environment = [_f.__name__ for _f in _environment_features]
supported_crs = ['UTM']
supported_utm_zones = [33]
supported_regions = [
    'Agder', 'Hele landet', 'Møre og Romsdal', 'Nordland', 'Nordsjøen',
    'Norge', 'Oslo', 'Rogaland', 'Svalbard', 'Troms og Finnmark', 'Trøndelag',
    'Vestfold og Telemark', 'Vestland', 'Viken'
]


@dataclass
class Environment:
    seabed: sf.Seabed = None
    land: sf.Land = None
    shore: sf.Shore = None
    shallows: sf.Shallows = None
    rocks: sf.Rocks = None

    def __iter__(self):
        for key in self.__dict__:
            attribute = getattr(self, key)
            if attribute is not None:
                yield attribute

    def __getattr__(self, item):
        return getattr(self, item)


@dataclass
class Scope:
    origin: tuple
    extent: tuple
    region: Union[str, Sequence[str]]
    depths: tuple
    bounding_box: tuple
    environment: Environment


# Paths

path_cwd = pathlib.Path.cwd()
path_module = pathlib.Path(__file__).parent
path_package = path_module.parent
path_data = path_package / 'data'
path_ships = path_data / 'ships.csv'
path_config = path_data / 'config.ini'
path_external = path_data / 'external'
path_shapefiles = path_data / 'shapefiles'
path_reports = path_cwd / 'reports'
path_frames_dir = path_reports / 'frames'
path_simulation = path_reports / 'simulation.gif'
path_frame_files = path_frames_dir / 'frame_*.png'


def _build_directory_structure():
    path_reports.mkdir(parents=True, exist_ok=True)
    path_external.mkdir(parents=True, exist_ok=True)
    path_shapefiles.mkdir(parents=True, exist_ok=True)
    path_frames_dir.mkdir(parents=True, exist_ok=True)
    for feature in supported_environment:
        shapefile_dir = path_shapefiles / feature.lower()
        shapefile_dir.mkdir(parents=True, exist_ok=True)


def _read_config_section(category):
    settings = {}
    config = configparser.ConfigParser()
    config.read(path_config, encoding='utf8')
    for key, value in config[category].items():
        values = [v.strip(' ') for v in value.split(',')]
        settings[key] = values
    return settings


_build_directory_structure()

# Display

_display = _read_config_section('DISPLAY')

_fps_max = 144
fps = int(_display['fps'][0])
if not 0 < fps <= _fps_max:
    raise ValueError(
        f"Fps '{fps}' not supported, "
        f"should be 0 < fps <= {_fps_max}"
    )

_crs_base, _crs_zone = _display['crs']
if _crs_base not in supported_crs:
    raise ValueError(
        f"Coordinate reference system '{_crs_base}' not supported, "
        f"possible candidates are: {supported_crs}"
    )
elif int(_crs_zone) not in supported_utm_zones:
    raise ValueError(
        f"CRS zone '{_crs_zone}' not supported, "
        f"possible candidates are: {supported_utm_zones}"
    )
crs = _environment_features[0].crs

ship_scale = float(_display['ship_scale'][0])

grid_size = tuple(int(_i) for _i in _display['grid_size'])

figure_size = tuple(int(_i) for _i in _display['figure_size'])

color = colors.color

colorbar = colors.colorbar

Ship = _entity_features[0]


# User

def get_user_scope():
    user = _read_config_section('USER')

    feature_names = user['features']
    for feature in feature_names:
        if feature not in supported_environment:
            raise ValueError(
                f"Feature '{feature}' not supported, "
                f"possible candidates are: {supported_environment}"
            )
    depths = tuple(float(d) for d in user['depths'])
    if any(d < 0 for d in depths):
        raise ValueError(
            f"Depth bins must be non-negative"
        )

    origin = tuple(int(i) for i in user['origin'])

    extent = tuple(int(i) for i in user['extent'])

    upper_right_corner = (i + j for i, j in zip(origin, extent))
    bounding_box = (*origin, *upper_right_corner)

    region = user['region']
    for sector in region:
        if sector not in supported_regions:
            raise ValueError(
                f"Region '{sector}' not supported, "
                f"possible candidates are: {supported_regions}"
            )

    env = (f for f in _environment_features if f.__name__ in feature_names)
    environment = Environment(**{f.__name__.lower(): f() for f in env})

    return Scope(origin, extent, region, depths, bounding_box, environment)


def write_user_input_to_config_file(args=None, kwargs=None):
    if len(args) > 5:
        raise ValueError(
            f"Too many positional arguments passed to ENC"
        )
    for kwarg in kwargs:
        if kwarg not in Scope.__annotations__:
            raise ValueError(
                f"'{kwarg}' is not a valid keyword argument for ENC"
            )
    user_call = {}
    for i, key in enumerate(Scope.__annotations__):
        value = args[i] if len(args) > i else kwargs.get(key, None)
        if value is not None:
            if key == 'origin' or key == 'extent':
                if not (isinstance(value, tuple) and len(value) == 2):
                    raise TypeError(
                        f"{key.capitalize()} should be a tuple of size two"
                    )
                else:
                    value = str(value).lstrip('(').rstrip(')')
            elif key == 'region':
                if isinstance(value, str):
                    region = [value]
                elif (isinstance(value, Sequence)
                      and all(isinstance(v, str) for v in value)):
                    region = value
                else:
                    raise TypeError(
                        f"Invalid region format for '{value}', "
                        f"should be string or sequence of strings"
                    )
                for sector in region:
                    if sector not in supported_regions:
                        raise ValueError(
                            f"Region '{sector}' not supported, "
                            f"possible candidates are: "
                            f"{supported_regions}"
                        )
                else:
                    value = ', '.join(region)
            elif key == 'depths':
                if not (isinstance(value, Sequence)
                        and all(isinstance(v, int) for v in value)):
                    raise TypeError(
                        f"Depth bins should be a sequence of numbers"
                    )
                else:
                    value = ', '.join(str(v) for v in value)
            elif key == 'features':
                if (isinstance(value, Sequence)
                        and all(isinstance(v, str) for v in value)):
                    features = value
                else:
                    raise TypeError(
                        f"Invalid region format for '{value}', "
                        f"should be sequence of strings"
                    )
                for feature in features:
                    if feature not in supported_environment:
                        raise ValueError(
                            f"Feature '{feature}' not supported, "
                            f"possible candidates are: "
                            f"{supported_environment}"
                        )
                else:
                    value = ', '.join(features)
            user_call[key] = value
    config = configparser.ConfigParser()
    config.read(path_config, encoding='utf8')
    config['USER'] = user_call
    with open(path_config, 'w', encoding='utf8') as configfile:
        config.write(configfile)


def read_ship_poses():
    try:
        with open(path_ships) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            _ = next(reader)
            rows = tuple(reader)
    except PermissionError:
        return None
    except StopIteration:
        return None
    return tuple((float(v) for v in row) for row in rows if row)


def get_gdb_zip_paths(region_names):
    zip_paths = []
    translation = str.maketrans('æøå ', 'eoa_')
    for name in region_names:
        label = name.translate(translation)
        for file_name in next(os.walk(path_external))[2]:
            if label in file_name:
                file_gdb = _match_file_gdb_to_template(file_name)
                zip_paths.append(file_gdb)
                break
        else:
            raise FileNotFoundError(
                f"Region FileGDB for '{name}' not found at "
                f"'{path_external}'"
            )
    return zip_paths


def _match_file_gdb_to_template(file_name):
    template = 'Basisdata_<#>_<name>_<projection>_Dybdedata_FGDB.zip'
    template_parts = template.split('_')
    file_parts = file_name.split('_')
    if any(file_parts[-i] != template_parts[-i] for i in range(3)):
        raise ValueError(
            f"'{file_name}' does not match the correct template for "
            f"Norwegian FileGDB charts: {template}"
        )
    projection = file_parts[-3]
    if int(projection[-2:]) not in supported_utm_zones:
        raise ValueError(
            f"Unsupported UTM zone '{projection[-2:]}' for "
            f"'{file_name}', possible candidates are: "
            f"{supported_utm_zones}"
        )
    gdb = file_name.replace('.zip', '.gdb')
    forward_slashed = str(path_external).replace('\\', '/')
    return '/'.join(('zip:/', forward_slashed, file_name, gdb))


def remove_past_gif_frames():
    for file_name in path_frames_dir.iterdir():
        os.remove(path_frames_dir / file_name)
