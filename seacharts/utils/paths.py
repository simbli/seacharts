import pathlib
import sys

# Defines (hard-coded paths to relevant files)
root = pathlib.Path(__file__).parents[2]
package = root / 'seacharts'

config = package / 'config.yaml'
config_schema = package / 'config_schema.yaml'

data_locations = [pathlib.Path(sys.argv[0]).absolute().parents[1],
                  root,
                  pathlib.Path(__file__).parents[1],
                  pathlib.Path.cwd().absolute().parents[0]
                ]
data = None
for data_location in data_locations:
    data_candidate = data_location / 'data'
    if data_candidate.exists():
        data = data_candidate
        break
if not data:
    raise FileNotFoundError('Data folder not found in any of the following locations: {}'.format(set([_.as_posix() for _ in data_locations])))
external = data / 'external'
shapefiles = data / 'shapefiles'

vessels = data / 'vessels.csv'

hazards = data / 'hazards'
dynamic = hazards / 'dynamic.csv'
static = hazards / 'static.csv'

paths = data / 'paths'
path1 = paths / 'path1.csv'
path2 = paths / 'path2.csv'

reports = root / 'reports'
frames_dir = reports / 'frames'
simulation = reports / 'simulation.gif'
frame_files = frames_dir / 'frame_*.png'
