# SeaCharts
Python-based API for Electronic Navigational Charts (ENC)

[![python version](https://img.shields.io/badge/python-3.11-blue)]()
[![license](https://img.shields.io/badge/license-MIT-green)]()
[![platform](https://img.shields.io/badge/platform-linux-lightgrey)]()
[![platform](https://img.shields.io/badge/platform-windows-lightgrey)]()

![](images/example1.svg
"Example visualization with vessels and geometric shapes in dark mode.")

## Features

- Read and process spatial depth data from
  [FileGDB](https://gdal.org/drivers/vector/filegdb.html) files into
  shapefiles.
- Read and process spatial depth data from [S-57](https://gdal.org/en/latest/drivers/vector/s57.html) files into shapefiles.
- Visualize S-57 [layers](https://www.teledynecaris.com/s-57/frames/S57catalog.htm).
- Access and manipulate standard geometric shapes such as points and polygon
  collections.
- Visualize colorful seacharts features and vessels.

## Code style

This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/)
convention for Python code.


## Prerequisites - For SeaCharts 4.0 see [this](#seacharts-40-setup-tips) section

### DEPRECATED - Linux (Virtual Environment)

First, ensure that you have the GDAL and GEOS libraries installed, as these are
required in order to successfully install GDAL and Cartopy:
```
sudo apt-get install libgeos-dev libgdal-dev
```

From the root folder, one may then install an editable version of the package as
follows:
```
pip install -e .
```

This should preferably be done inside a virtual environment in order to prevent
Python packaging conflicts.

### DEPRECATED - Anaconda

Install an edition of the [Anaconda](
https://www.anaconda.com/products/individual-d) package manager, and then create a new
_conda environment_
with [Python 3.11](https://www.python.org/downloads/) or higher using e.g. the
graphical user interface of [PyCharm Professional](
https://www.jetbrains.com/lp/pycharm-anaconda/) as detailed [here](
https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html
).

The required data processing libraries for spatial calculations and
visualization may subsequently be installed simply by running the following
commands in the terminal of your chosen environment:

```
conda install -c conda-forge fiona cartopy matplotlib
conda install matplotlib-scalebar cerberys pyyaml
```

### DEPRECATED - Windows (Pipwin)

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

or locally inside the SeaCharts root folder as an editable package with `pip install
-e .`

## Usage

This module supports reading and processing `FGDB` and 'S-57' files for sea depth data.

### Downloading regional datasets - FGDB

The Norwegian coastal data set used for demonstration purposes, found
[here](
https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).
To visualize and access coastal data of Norway, follow the above link to download
the `Depth data` (`Sjøkart - Dybdedata`) dataset from the [Norwegian Mapping Authority](
https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority) by adding
it to the Download queue and navigating to the separate
[download page](https://kartkatalog.geonorge.no/nedlasting). Choose one or more
county areas (e.g. `Møre og Romsdal`), and select the
`EUREF89 UTM sone 33, 2d` (`UTM zone 33N`) projection and `FGDB 10.0`
format. Finally, select your appropriate user group and purpose, and click
`Download` to obtain the ZIP file(s).

### Configuration and startup

Unpack the downloaded file(s) and place the extracted `.gdb` or 'S-57' folder in a suitable location,
in which the SeaCharts setup may be configured to search. The current
working directory as well as the relative `data/` and `data/db/` folders are
included by default.

The minimal example below imports the `ENC` class from `seacharts.enc` with the
default configuration found in `seacharts/config.yaml`, and shows the interactive
SeaCharts display. Note that at least one database with spatial data (e.g. `Møre og
Romsdal` from the Norwegian Mapping Authority) is required.

```python
if __name__ == '__main__':

    from seacharts.enc import ENC

    enc = ENC()
    enc.display.show()
```

The `config.yaml` file specifies which file paths to open and which area to load. In the configuration file the desired map type can be specified by listring data to display - depths for 'FDGB', and [layers](https://www.teledynecaris.com/s-57/frames/S57catalog.htm) for 'S-57'.
The corresponding `config_schema.yaml` specifies how the required setup parameters
must be provided, using `cerberus`.


### API usage and accessing geometric shapes

After the spatial data is parsed into shapefiles during setup, geometric
shapes based on the [Shapely](https://pypi.org/project/Shapely/) library may be
accessed and manipulated through various `ENC` attributes. The seacharts
feature layers are stored in `seabed`, `shore` and `land`.

```python
if __name__ == '__main__':
    from seacharts.enc import ENC

    # Values set in user-defined 'seacharts.yaml'
    # size = 9000, 5062
    # center = 44300, 6956450
    enc = ENC("seacharts.yaml")

    print(enc.seabed[10])
    print(enc.shore)
    print(enc.land)

    enc.display.show()
```

Note how custom settings may be set in a user-defined .yaml-file, if its path is
provided to the ENC during initialization. One may also import and create an
instance of the `seacharts.Config` dataclass, and provide it directly to the ENC.

### FGDB demonstration
![](images/example2.svg "Example visualization of vessels and a
colorbar with depth values in light mode.")

### S-57 demonstration
![](images/example3.png "Example visualization of S-57 map with TSS layer and a
colorbar with depth values in light mode.")

### Environment visualization
The `ENC.start_display` method is used to show a Matplotlib figure plot of the
loaded sea charts features. Zoom and pan the environment view using the mouse
scroll button, and holding and dragging the plot with left click, respectively.

Dark mode may be toggled using the `d` key, and an optional colorbar showing
the various depth legends may be toggled using the `c` key. Images of the
currently shown display may be saved in various resolutions by pressing
Control + `s`, Shift + `s` or `s`.

### SeaCharts 4.0 setup tips
```
Please be aware that these setup tips require setting up Conda environment.
Possible support for pip installation will be resolved in the future.
```

This is a short to-do list that might come useful when setting up SeaCharts 4.0 for the first time:
1. Set up conda environment as instructed in `conda_requirements.txt` file
2. Use `setup.ps1` (WINDOWS ONLY) to setup directory structure needed by SeaCharts or manually create directories: `data`, `data/db` and `data/shapefiles`
3. Download US1GC09M map via [this link](https://www.charts.noaa.gov/ENCs/US1GC09M.zip), and put the `US1GC09M` directory (found in ENC_ROOT directory) inside data/db folder.
4. Run `test_seacharts_4_0.py` code either by pasting code into some main.py file in root of your project directory or by running it directly (needs fixing the issues with importing seacharts in the test file)
5. After execution you can expect such image to be displayed:
![](images/test_results.svg
"Example visualization with vessels and geometric shapes in dark mode.")

```
For further experimentation options, look into files: `enc.py`, `config.yaml` and `config-schema.yaml` (for reference)
```
## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.
