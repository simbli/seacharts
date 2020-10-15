# ENC
Electronic Navigational Charts module for reading sea depth data.

[![platform](https://img.shields.io/badge/platform-windows-lightgrey)]()
[![python version](https://img.shields.io/badge/python-3.9-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()


## Features

- Read and process depth data 
[FileGDB](https://gdal.org/drivers/vector/filegdb.html) files into points and
polygon coordinate lists.


## Code style
This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/) 
convention for Python code.


## Prerequisites

First, ensure that [Python 3.9](https://www.python.org/downloads/) 
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

### Unpacking depth data example
Place the downloaded ZIP file(s) in the path `data/external/`, where the 
top-level folder `data` is located in the same directory as the executing 
script.

Import the module, initialize an instance of `ENCParser` with appropriate 
settings, and use its `parse_external_data` method to extract desired 
ENC features from the downloaded ZIP file(s):

```python
import enc

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
window_size = (20000, 16000)  # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

parser = enc.ENCParser(origin, window_size, region)
parser.parse_external_data()  # used only to parse newly downloaded data
```

Note that `region` may be one or several Norwegian county names
(or the whole country if the `Hele landet` data set is available), 
corresponding to each downloaded ZIP file. Furthermore, a user-defined set of 
sea `depths` bins and `features` to be extracted may be passed to the parser as 
additional keyword arguments.

### Reading feature shapefiles example
After the data is extracted from the downloaded ZIP file(s), the shapefile 
data can be read by calling the `read_feature_shapes` function for each 
feature layer. The returned data is compatible with the 
[Shapely](https://pypi.org/project/Shapely/) package for further geometric 
manipulation and analysis of shapes:

```python
import enc

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
window_size = (20000, 16000)  # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

parser = enc.ENCParser(origin, window_size, region)
data = parser.read_feature_shapes('seabed')


from shapely.geometry import Polygon

depth, coords = data[-1]
polygon = Polygon(coords)

print(f"\nNumber of extracted seabed polygons: {len(data)}")
print(f"Minimum sea depth inside the last polygon: {depth}")
print(f"Number of points in the last polygon: {len(coords)}")
print(f"Area of the last polygon: {int(polygon.area)}")

```

Note that the `origin` and `window_size` arguments here may be different 
from the one used to extract the external ENC data, allowing for loading of 
smaller areas of interest into memory during runtime. 


## Contributors

- Simon Blindheim ([simon.blindheim@ntnu.no](mailto:simon.blindheim@ntnu.no))


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.