# SeaCharts
Python-based application for reading Electronic Navigational Charts (ENC)

[![platform](https://img.shields.io/badge/platform-windows-lightgrey)]()
[![python version](https://img.shields.io/badge/python-3.7-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()


## Features

- Read and process depth data 
[FileGDB](https://gdal.org/drivers/vector/filegdb.html) files into points and
polygon coordinate lists.


## Code style
This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/) 
convention for Python code.


## Prerequisites

First, ensure that [Python 3.7](https://www.python.org/downloads/) 
(or another compatible version) and the required
[C++ build tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019) 
are installed.

Next, install the required Python packages (in a virtual environment):
```
pip install wheel
pip install pipwin
pipwin install numpy
pipwin install pandas
pipwin install shapely
pipwin install gdal
pipwin install fiona
```


## Usage
This module supports reading and processing the `FGDB` files for sea depth data 
found [here](https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).

### Downloading regional datasets
Follow the above link to download the `Depth data` (`Sjøkart - Dybdedata`) 
dataset from the [Norwegian Mapping Authority](https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority), 
by adding it to the Download queue and navigating to the separate 
[download page](https://kartkatalog.geonorge.no/nedlasting). 
Choose one or more county areas (e.g. `Møre og Romsdal`), and 
select the `EUREF89 UTM sone 33, 2d` (`UTM zone 33N`) projection and `FGDB 10.0` 
format. Finally, select your appropriate user group and purpose, and click 
`Download` to obtain the ZIP file(s).

### Processing ENC data into shapefiles
Place the downloaded ZIP file(s) in the path `data/external/`, where the 
top-level folder `data` is located in the same directory as the executing 
script.

Import the module, initialize an instance of `seacharts.ENC` with appropriate 
settings, and set its `parse_new_map_data` keyword argument to `True` in order 
to unpack and parse desired ENC features from the downloaded ZIP file(s) into 
shapefiles:

```python
import seacharts

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
window_size = (20000, 16000)  # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

charts = seacharts.ENC(origin, window_size, region, new_data=True)

```

Note that `region` may be one or several Norwegian county names
(or the whole country if the `Hele landet` data set is available), 
corresponding to each downloaded ZIP file. Furthermore, a user-defined set of 
sea `depths` bins and `features` to be extracted may be passed to `ENC` as 
additional keyword arguments.

### Reading feature shapefiles
After the data is parsed from the downloaded ZIP file(s) as shown above, the 
resulting shapefiles can be read by calling the `read_feature_coordinates` 
method for each feature layer independently. The returned data is compatible 
with the [Shapely](https://pypi.org/project/Shapely/) package for further 
geometric manipulation and analysis of shapes:

```python
import seacharts

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
window_size = (20000, 16000)  # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

charts = seacharts.ENC(origin, window_size, region)
coordinates = charts.read_feature_coordinates('seabed')

from shapely.geometry import Polygon

depth, points = coordinates[-1]
polygon = Polygon(points)

print(f"Number of extracted seabed polygons: {len(coordinates)}")
print(f"Minimum sea depth inside the last polygon: {depth}")
print(f"Number of points in the last polygon: {len(points)}")
print(f"Area of the last polygon: {int(polygon.area)}")

```

Note that the `parse_new_map_data` argument may be omitted or set to `False` if 
the desired regional feature data has already been unpacked and processed into 
shapefiles in a previous call. Additionally, the `origin` and `window_size` 
arguments here may be different from the one used to extract the external 
ENC data, allowing for loading of more specific (smaller) areas of interest 
into memory during runtime.  

An optional geometric API based on [Shapely](https://pypi.org/project/Shapely/)
is provided for convenience through use of the `read_feature_shapes` method and 
the accompanying `seacharts.features` classes:

```python
import seacharts

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
window_size = (20000, 16000)  # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

charts = seacharts.ENC(origin, window_size, region, new_data=True)
layer = charts.read_feature_shapes('seabed')
feature = layer[-1]

print("Feature name:                    ", feature.name)
print("Feature shape:                   ", feature.shape)
print("Feature category:                ", feature.category)
print("Number of feature polygon points:", len(feature.coordinates))
print("Minimum sea depth inside feature:", int(feature.depth))
print("Area of the feature polygon:     ", int(feature.area))

```


## Contributors

- Simon Blindheim ([simon.blindheim@ntnu.no](mailto:simon.blindheim@ntnu.no))


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.