import pathlib

cwd = pathlib.Path.cwd()
package = pathlib.Path(__file__).parent.parent

config = package / 'config.ini'

data = cwd / 'data'
external = data / 'external'
shapefiles = data / 'shapefiles'

vessels = data / 'vessels.csv'

hazards = data / 'hazards'
dynamic = hazards / 'dynamic.csv'
static = hazards / 'static.csv'

paths = data / 'paths'
path1 = paths / 'path1.csv'
path2 = paths / 'path2.csv'

reports = cwd / 'reports'
frames_dir = reports / 'frames'
simulation = reports / 'simulation.gif'
frame_files = frames_dir / 'frame_*.png'
