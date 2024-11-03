"""
Contains hard-coded paths to relevant files and directories.
"""
from pathlib import Path

# Get the root directory of the project by going up two levels from the current file's location
root = Path(__file__).parents[2]
# Define the main package directory for "seacharts"
package = root / "seacharts"

# Default path to the main configuration file for the project
config = package / "config.yaml"
# Path to the schema file that validates the structure of the configuration file
config_schema = package / "config_schema.yaml"

# Get the current working directory, where this script is being executed
cwd = Path.cwd()
# Define a 'data' directory within the current working directory, used to store source ENC data files
data = cwd / "data"
# Define the database directory within the 'data' folder, used for storing database files
db = data / "db"

default_resources = cwd, data, db

# Directory to store shapefiles, which are used for geographic and spatial data
shapefiles = data / "shapefiles"

# Path to the CSV file containing vessel data
vessels = data / "vessels.csv"

# Define the output directory, where results and generated files will be saved
output = root / "output"
