# script to quickly setup seacharts downloaded from github on Windows

$baseDir = "data"
New-Item -ItemType Directory -Path $baseDir -Force
# Create 'shapefiles' and 'data' subdirectories inside 'db'
New-Item -ItemType Directory -Path "$baseDir\shapefiles" -Force
New-Item -ItemType Directory -Path "$baseDir\db" -Force
