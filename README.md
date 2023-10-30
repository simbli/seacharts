# SeaCharts
Python-based API for Electronic Navigational Charts (ENC)

[![python version](https://img.shields.io/badge/python-3.11-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()
[![platform](https://img.shields.io/badge/platform-linux-lightgrey)]()
[![platform](https://img.shields.io/badge/platform-windows-lightgrey)]()


![](https://github.com/simbli/seacharts/blob/master/images/example1.svg?raw=True
"Example visualization with demonstration shapes")

## Features

- Read and process spatial depth data from
  [FileGDB](https://gdal.org/drivers/vector/filegdb.html) files into
  shapefiles.
- Access and manipulate standard geometric shapes such as points and polygon
  collections.
- Visualize colorful seacharts features and vessels using multiprocessing.

## Code style

This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/)
convention for Python code.

## Roadmap
- 1: Add better compatibility for all operating systems (Windows, Linux++). Right now, gdal and cartopy are problematic to install on most platforms. Consider finding other packages for map loading and chart projections.
- 2: Add support for multiple map data formats (.gis, .gdb, .json, ) from any region in the world, in all UTM zones or lat/lon coordinates. To do this, the current loading functionality should be separated from the simplification and geometry classification, such that one can load from any map data file first.
- 3: Separate backend (Environment object) from frontend (Display object).
- 4: Use another plotting framework that has higher refresh rate/ is feasible for real-time (Qt?, React?)
- 5: Create clearly defined interface between Environment/ENC backend and frontend Display
- 6: Add option for plotting trajectories, ships, traffic information/AIS data etc. on the frontend display.
- 7: Add support for reading and loading in weather data (wind and current
  maps++) in a separate module.
- 8: Select and adopt rules for project-wide (automatic) formatting, e.g.
  Black.
- 9: Use Poetry for packaging management.
- 10: Add deprecation warnings for planned API changes.
- 11: Refactor and simplify the exposed top-level API.
- 12: Document all sub-modules after API cleanup.

## Prerequisites

### Linux (Virtual Environment)

First, ensure that you have gdal and geos libraries installed, as these are required in order to successfully install gdal and cartopy:
```
sudo apt-get install libgeos-dev libgdal-dev
```
Then, from the root folder you can install an editable version of the package as follows:
```
pip install -e .
```
This should preferably be done inside a virtual environment in order to prevent python packaging conflicts.

### Anaconda

Install an edition of the [Anaconda](
https://www.anaconda.com/products/individual-d) package manager, and then
create a new _conda environment_
with [Python 3.11](https://www.python.org/downloads/) or higher using e.g. the
graphical
user interface of [PyCharm Professional](
https://www.jetbrains.com/lp/pycharm-anaconda/) as detailed [here](
https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html
).

The required data processing libraries for spatial calculations and
visualization may subsequently be installed simply by running the following
command in the terminal of your chosen environment:

```
conda install -c conda-forge fiona cartopy matplotlib
```

### Windows (Pipwin)

First, ensure that [Python 3.11](https://www.python.org/downloads/) or higher
is installed. Next, install all required packages using
[Pipwin](https://pypi.org/project/pipwin/):
```
python -m pip install --upgrade pip
pip install wheel
pip install pipwin
pipwin install numpy
pipwin install gdal
pipwin install fiona
pipwin install shapely
pip install cartopy
pip install pyyaml
pip install cerberus
pip install matplotlib-scalebar

```

Simply copy and paste the entire block above (including the empty line) into
the terminal of your virtual environment, and go get a cup of coffee while it
does its thing.

## Installation

After the necessary dependencies have been correctly installed, the SeaCharts
package may be installed directly through the Python Package Index ([PyPI](
https://pypi.org/
)) by running the following command in the terminal:

```
pip install seacharts
```

or locally inside the seacharts root folder as an editable package with `pip install -e .`

![](https://github.com/simbli/seacharts/blob/master/images/example2.svg?raw=True
"Example visualization with default settings")

## Usage

This module supports reading and processing `FGDB` files for sea depth data
such as the Norwegian coastal data set used for demonstration purposes, found
[here](
https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).

### Downloading regional datasets

Follow the above link to download the `Depth data` (`Sjøkart - Dybdedata`)
dataset from the [Norwegian Mapping Authority](
https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority),
by adding it to the Download queue and navigating to the separate
[download page](https://kartkatalog.geonorge.no/nedlasting). Choose one or more
county areas (e.g. `Møre og Romsdal`), and select the
`EUREF89 UTM sone 33, 2d` (`UTM zone 33N`) projection and `FGDB 10.0`
format. Finally, select your appropriate user group and purpose, and click
`Download` to obtain the ZIP file(s).

### Processing ENC data into shapefiles
Unpack the downloaded file(s) and place the extracted `.gdb` in the
`data/external/` directory, where the top-level folder `data` is located in the
same directory as the executing script.

The `config.yaml` file specifies what ENC data to load and how it will be processed and displayed.
The corresponding `config_schema.yaml` specifies the required parameters that must be provided for the software to function properly.

The minimal example below imports the `ENC` class from `seacharts.enc` with the default configuration under `seacharts/config.yaml`, and
shows the interactive seachart display.

```python
if __name__ == '__main__':

    from seacharts.enc import ENC

    enc = ENC()
    enc.start_display()
```

You can also specify settings at run-time, such as the window size, coordinate (easting, northing) origin and file
to load shapefile data from, and whether or not to load new data. Here, the
`new_data` keyword argument must be set to `True` during the
initial setup run, and/or for any subsequent desired re-parsing in order
to unpack and store `ENC` features from the downloaded FGDB files as
shapefiles:

```python
if __name__ == '__main__':

    from seacharts.enc import ENC

    size = 9000, 5062                # w, h (east, north) distance in meters
    center = 44300, 6956450          # easting/northing (UTM zone 33N)
    files = ['More_og_Romsdal_utm33.gdb']  # Norwegian county database name

    enc = ENC(size=size, center=center, files=files, new_data=True)

```
Note that all `ENC` settings parameters may be set and modified directly in
`seacharts/config.yaml`, which are validated by the `seacharts/config_schema.yaml` using `cerberus`. Parameters passed to `ENC` overrides the defaults of the
configuration file. See the documentation of the `ENC` input parameters for
descriptions of all available configuration settings.


![](https://github.com/simbli/seacharts/blob/master/images/example3.svg?raw=True
"Example visualization with dark mode and ownship hazards")


### API usage and accessing geometric shapes
After the spatial data is parsed into shapefiles as shown above, geometric
shapes based on the [Shapely](https://pypi.org/project/Shapely/) library may
be accessed and manipulated through various `ENC` attributes. The seacharts
feature layers are stored in `seabed`, `shore` and `land`.

```python
if __name__ == '__main__':
    from seacharts.enc import ENC

    size = 9000, 5062
    center = 44300, 6956450
    enc = ENC(new_data=True, size=size, center=center)
    enc.start_display()

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

See the documentation for each top-level ENC method for all API usage and
visualization possibilities currently available to the SeaCharts package.


![](https://github.com/simbli/seacharts/blob/master/images/example4.svg?raw=True
"Example visualization with zoom and paths")


### Interactive environment visualization (Parts of this is DEPRECATED)
The `ENC.start_display` method is used to show a Matplotlib figure plot of the
loaded seacharts features. Zoom and pan the environment view using the mouse
scroll button, and holding and dragging the plot with left click, respectively.

Fullscreen mode may be toggled using the `f` key, and dark mode may be toggled
using the `d` key. An optional colorbar showing the various depth legends may
be toggled using the `c` key. Moreover, the visibility of each individual layer
may be toggled on and off using the `t`, `g`,`h`, `b`, and `l` keys. Press and
hold the left `Alt` key and press any of the arrow keys to move the anchor of
the figure window.

A controllable ownship with a sector horizon of hazards and arrows pointing to
the closest point on a polygon within it may be added and toggled through the
`o`, `z` and `a` keys, respectively. Steer the ship with the arrows keys.

The filter depths of the displayed hazardous obstacles may be toggled using the
`n` and `m` keys, and the size of the horizon may be altered using `,`, `.`,
`[`, and `]` (on a US keyboard layout). Furthermore, vessels may be added and
shown by passing appropriately formatted vessel poses to the `ENC.add_vessels`
method, or manually storing the vessel details in `data/vessels.csv` and
pressing the `u` key to update the display. Toggle their visibility through the
`v` key.

Shift left-click on the environment to add yellow path waypoints, move them
around by pressing Shift and holding down the mouse button, and Shift right-
click to remove them. One may also Shift right-click on a path edge to create
an intermediate waypoint between two existing waypoints. Additionally, a
second path of magenta color may be added and manipulated by replacing Shift
with the Control key.

Images of the currently shown display may be saved in various resolutions by
pressing Control + `s`, Shift + `s` or `s`. The below snippet produces the
example usage visualization images shown at the top of this page, assuming
default settings and that a `More_og_Romsdal.gdb` directory is correctly
extracted and placed as discussed in the shapefile processing section:

```python
if __name__ == "__main__":
    import shapely.geometry as geo
    from seacharts.enc import ENC

    size = 9000, 5062
    center = 44300, 6956450
    enc = ENC(new_data=True, size=size, center=center)
    enc.start_display()

    # (id, easting, northing, heading, color)
    ships = [
        (1, 46100, 6957000, 132, "orange"),
        (2, 45000, 6956000, 57, "yellow"),
        (3, 44100, 6957500, 178, "red"),
        (4, 42000, 6955200, 86, "green"),
        (5, 44000, 6955500, 68, "pink"),
    ]

    enc.add_vessels(*ships)

    x, y = center
    width, height = 1900, 1900
    box = geo.Polygon(
        (
            (x - width, y - height),
            (x + width, y - height),
            (x + width, y + height),
            (x - width, y + height),
        )
    )
    areas = list(box.difference(enc.seabed[10].geometry))
    enc.draw_circle(center, 1000, "yellow", thickness=2, edge_style="--", alpha=0.5)
    enc.draw_rectangle(center, (600, 1200), "blue", rotation=20, alpha=0.5)
    enc.draw_circle(center, 700, "green", edge_style=(0, (5, 8)), thickness=3, fill=False)
    enc.draw_line([(center[0], center[1] + 800), center, (center[0] - 300, center[1] - 400)], "white")
    enc.draw_line([(center[0] - 300, center[1] + 400), center, (center[0] + 200, center[1] - 600)], "magenta", width=0.0, thickness=5.0, edge_style=(0, (1, 4)))
    enc.draw_arrow(center, (center[0] + 700, center[1] + 600), "orange", head_size=300, width=50, thickness=5)
    enc.draw_polygon(enc.seabed[100].geometry[-3], "cyan", alpha=0.5)
    enc.draw_polygon(enc.shore.geometry[56], "highlight", alpha=0.5)
    for area in areas[3:8] + [areas[14], areas[17]] + areas[18:21]:
        enc.draw_polygon(area, "red", alpha=0.5)
    enc.draw_rectangle(center, (width, height), "pink", fill=False, edge_style=(0, (10, 10)), thickness=1.5)

    enc.save_image("example1", extension="svg")
```

The `id` values of the vessel details should be unique identifiers, used as
references to the feature artists added to the Matplotlib plot. The color
values may be strings of one of the custom ship colors of this package, or any
named Matplotlib [CSS4 color](
https://matplotlib.org/stable/gallery/color/named_colors.html).

### Visualization using multiprocessing (DEPRECATED)
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


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.
