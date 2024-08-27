# script to quickly setup seacharts downloaded from github on Windows

$baseDir = "data"
New-Item -ItemType Directory -Path $baseDir -Force
# Create 'shapefiles' and 'data' subdirectories inside 'db'
New-Item -ItemType Directory -Path "$baseDir\shapefiles" -Force
New-Item -ItemType Directory -Path "$baseDir\db" -Force

# Create a virtual environment named 'venv' (if it doesn't exist)
python -m venv venv

# Activate the virtual environment
& .\venv\Scripts\Activate.ps1

# Upgrade pip within the virtual environment
python -m pip install --upgrade pip

# Install wheel package
pip install wheel

# Install pipwin package
pip install pipwin

# Use pipwin to install specific packages
pipwin install numpy
pipwin install gdal
pipwin install fiona
pipwin install shapely

# Install additional Python packages
pip install cartopy
pip install setuptools
pip install requests
pip install pyyaml
pip install cerberus
pip install matplotlib-scalebar

# Deactivate the virtual environment
Deactivate
