import pathlib

# Defines (hard-coded paths to relevant files)
root = pathlib.Path(__file__).parents[2]
package = root / "seacharts"

config = package / "config.yaml"
config_schema = package / "config_schema.yaml"

cwd = pathlib.Path.cwd()
data = cwd / "data"
db = data / "db"
default_resources = cwd, data, db
shapefiles = data / "shapefiles"

vessels = data / "vessels.csv"

reports = root / "reports"
