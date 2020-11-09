# SeaCharts
Python-based application for reading Electronic Navigational Charts (ENC)

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
pip install pipwin
pipwin install gdal
pipwin install numpy
pipwin install scipy
pipwin install fiona
pipwin install shapely
pipwin install cartopy
pipwin install matplotlib

```

Simply copy and paste the entire block above (including the empty line) into 
the terminal of your virtual environment, and go get a cup of coffee when it 
does its thing.


## Usage
This module supports reading and processing the `FGDB` files for sea depth data 
found [here](https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).

### Downloading regional datasets
Follow the above link to download the `Depth data` (`Sjøkart - Dybdedata`) 
dataset from the [Norwegian Mapping Authority](https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority), 
by adding it to the Download queue and navigating to the separate 
[download page](https://kartkatalog.geonorge.no/nedlasting). 
Choose one or more county areas (e.g. `Møre og Romsdal`), and select the 
`EUREF89 UTM sone 33, 2d` (`UTM zone 33N`) projection and `FGDB 10.0` 
format. Finally, select your appropriate user group and purpose, and click 
`Download` to obtain the ZIP file(s).

### Processing ENC data into shapefiles
Place the downloaded ZIP file(s) in the path `data/external/`, where the 
top-level folder `data` is located in the same directory as the executing 
script.

Import the module, initialize an instance of `seacharts.ENC` with appropriate 
settings, and set its `new_data` keyword argument to `True` in order 
to unpack and parse desired ENC features from the downloaded ZIP file(s) into 
shapefiles:

```python
from seacharts import ENC

origin = (38100, 6948700)     # easting/northing (UTM zone 33N)
extent = (20000, 16000)       # w, h (east, north) distance in meters
region = 'Møre og Romsdal'    # name for a Norwegian county region

if __name__ == '__main__':
    enc = ENC(origin, extent, region, new_data=True)

```
Note that `region` may be one or several Norwegian county names
(or the whole country if the `Hele landet` data set is available), 
corresponding to each downloaded ZIP file. Furthermore, a user-defined list of 
sea `depths` bins may be passed to `ENC` as an additional keyword argument.

### Accessing features
After the data is parsed into shapefiles as shown above, 
[Shapely](https://pypi.org/project/Shapely/) features may be accessed and 
displayed through the following ENC attributes:
```python
from seacharts import ENC

origin = (42600, 6956400)     # easting/northing (UTM zone 33N)
extent = (3000, 2000)         # w, h (east, north) distance in meters

if __name__ == '__main__':
    enc = ENC(origin, extent)

    for feature in (enc.seabed, enc.land):
        polygon = feature[10]
        print("Feature name:                    ", feature.name)
        print("Feature shape:                   ", feature.shape.type)
        print("Area of the feature polygon:     ", int(polygon.area))
        print("Number of feature polygon points:", len(polygon.coords))
        print("Minimum sea depth inside feature:", int(polygon.depth))
        print()

    enc.visualize_environment()

```
Note that the `new_data` argument may be omitted or set to `False` if the 
desired regional feature data has already been unpacked and processed into 
shapefiles in a previous call. Available map features may be identified by the 
`ENC.supported_environment` attribute. Additionally, the `origin` and 
`extent` arguments here may be different from the one used to extract the 
external ENC data, allowing for loading of more specific (smaller) areas 
of interest into memory during runtime.

### Visualizing the environment
The `ENC.visualize_environment` method continuously reads the `x_position`, 
`y_position` and `heading` (in degrees) of ships in a csv file named 
`ships.csv`, located in the `data` folder. The ship poses are displayed in a 
decoupled environment using multiprocessing, and may be saved as a GIF using 
`ENC.save_visualization` after the display is closed. Create the csv file as 
in the example below, and update it during runtime to visualize any number of 
ships:

```
x_position,y_position,heading

1200,1200,45
1500,1300,305
```


## Contributors

- Simon Blindheim ([simon.blindheim@ntnu.no](mailto:simon.blindheim@ntnu.no))


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.