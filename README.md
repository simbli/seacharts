# SeaCharts
Python-based API for Electronic Navigational Charts (ENC)

[![platform](https://img.shields.io/badge/platform-windows-lightgrey)]()
[![python version](https://img.shields.io/badge/python-3.9-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()

![](images/example.png?raw=true "Example usage visualization")

## Features

- Read and process spatial depth data from 
[FileGDB](https://gdal.org/drivers/vector/filegdb.html) files into shapefiles.
 - Access and manipulate standard geometric shapes such as points and polygon 
 collections.
- Visualize colorful seacharts features and vessels using multiprocessing.


## Code style
This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/) 
convention for Python code.


## Prerequisites

First, ensure that [Python 3.9](https://www.python.org/downloads/) 
(or another compatible version) and the required [C++ build tools](
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019) 
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
the terminal of your virtual environment, and go get a cup of coffee while it 
does its thing.


## Usage
This module supports reading and processing the `FGDB` files for sea depth data 
found [here](
https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).

### Downloading regional datasets
Follow the above link to download the `Depth data` (`Sjøkart - Dybdedata`) 
dataset from the [Norwegian Mapping Authority](
https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority), 
by adding it to the Download queue and navigating to the separate 
[download page](https://kartkatalog.geonorge.no/nedlasting). 
Choose one or more county areas (e.g. `Møre og Romsdal`), and select the 
`EUREF89 UTM sone 33, 2d` (`UTM zone 33N`) projection and `FGDB 10.0` 
format. Finally, select your appropriate user group and purpose, and click 
`Download` to obtain the ZIP file(s).

### Processing ENC data into shapefiles
Unpack the downloaded file(s) and place the extracted `.gdb` in the 
`data/external/` directory, where the top-level folder `data` is located in the
same directory as the executing script.

Import the module, and initialize an instance of `seacharts.ENC` with optional
settings. The `new_data` keyword argument must be set to `True` during the 
initial setup run, and/or for any subsequent desired re-parsing in order 
to unpack and store `ENC` features from the downloaded FGDB files as 
shapefiles:

```python
if __name__ == '__main__':

    import seacharts

    size = 18000, 12000              # w, h (east, north) distance in meters
    center = 44300, 6956450          # easting/northing (UTM zone 33N)
    files = ['More_og_Romsdal.gdb']  # Norwegian county database name

    enc = seacharts.ENC(size=size, center=center, files=files, new_data=True)

```
Note that all `ENC` settings parameters may be set and modified directly in
`data/config.ini`, wherein user settings are saved alongside the project 
defaults. Parameters passed to `ENC` overrides the defaults of the 
configuration file. See the documentation of the `ENC` input parameters for 
descriptions of all available configuration settings.


### Accessing geometric shapes
After the spatial data is parsed into shapefiles as shown above, geometric 
shapes based on the [Shapely](https://pypi.org/project/Shapely/) library may 
be accessed and manipulated through various `ENC` attributes. The seacharts 
feature layers are stored in `seabed`, `shore` and `land`.

```python
if __name__ == '__main__':

    import seacharts

    enc = seacharts.ENC(new_data=False)

    print(enc.seabed[10])
    print(enc.shore)
    print(enc.land)

```
Note how the `new_data` argument may be set to `False` (or omitted) if the 
desired regional spatial data has already been unpacked and processed into 
shapefiles in a previous call. Additionally, the `size`, `center` or `origin` 
parameters may be different from the one used to extract the external `ENC` 
data, allowing for loading of more specific (smaller) areas of interest into 
memory during runtime.

### Visualizing the environment
The `ENC.show_display` method is used to show a Matplotlib figure plot of the 
loaded seacharts features. Layers visibility may be toggled on and off using
the `v`, `t`, `g`, `h`, `b`, `k` and `l` keys. Furthermore, vessels may be 
added and shown by passing appropriately formatted vessel poses to the 
`ENC.add_vessels` method, or manually storing the vessel details in 
`data/vessels.csv`. The below snippet produces the example usage visualization 
image shown at the top of this page, assuming a `More_og_Romsdal.gdb` directory 
is correctly extracted and placed as discussed in the shapefile processing 
section:

```python
if __name__ == '__main__':

    import seacharts
    
    # (id, easting, northing, heading, color)
    ships = [  
        (1, 46100, 6957000, 132, 'orange'),
        (2, 45000, 6956000, 57, 'yellow'),
        (3, 44100, 6957500, 178, 'purple'),
        (4, 42000, 6955200, 86, 'green'),
        (5, 44000, 6955500, 68, 'pink'),
        (6, 46600, 6956400, -68, 'red'),
    ]

    enc = seacharts.ENC()

    enc.add_vessels(*ships)

    enc.show_display()

```

The `id` values of the vessel details should be unique identifiers, used as
references to the feature artists added to the Matplotlib plot. The color 
values are strings of any named Matplotlib [CSS4 color](
https://matplotlib.org/stable/gallery/color/named_colors.html).

### Visualization using multiprocessing
Initializing an `ENC` instance with the `multiprocessing` parameter set to 
`True` spawns a `Process` thread from the Python standard library 
[multiprocessing module](
https://docs.python.org/3/library/multiprocessing.html), creating an 
independent environment display running an infinite visualization loop, based 
on the current user (or default) settings stored in the `data/config.ini` file.
The visualization loop continuously reads the `data/vessels.csv` file, and 
updates the plot with any present vessels. Repeated updating of the vessels 
file by any arbitrary alternative method is thus reflected in the plot in near
real-time. As such, this feature may be utilized for parallel or concurrent 
visualization of vessels in an environment, e.g. based on vessel trajectories 
produced by a separate and independent simulation or optimization algorithm.


## Contributors

- Simon Blindheim ([simon.blindheim@ntnu.no](mailto:simon.blindheim@ntnu.no))


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.