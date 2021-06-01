import pathlib

cwd = pathlib.Path.cwd()

data = cwd / 'data'
config = data / 'config.ini'
external = data / 'external'
vessels = data / 'vessels.csv'
shapefiles = data / 'shapefiles'

reports = cwd / 'reports'
frames_dir = reports / 'frames'
simulation = reports / 'simulation.gif'
frame_files = frames_dir / 'frame_*.png'
