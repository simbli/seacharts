# ENC
Electronic Navigational Charts module for reading sea chart shapefiles

[![platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)](https://gitlab.stud.idi.ntnu.no/tdt4140-2020/52/-/commits/master)
[![python version](https://img.shields.io/badge/python-3.7-blue)](https://gitlab.stud.idi.ntnu.no/tdt4140-2020/52/-/commits/master)
[![license](https://img.shields.io/badge/license-MIT-green)](https://gitlab.stud.idi.ntnu.no/tdt4140-2020/52/-/commits/master)


## Features

- Read and process depth data shapefiles into coordinate dictionaries
- Split different ocean depths into separate layers of polygons


## Code style
This module follows the [PEP8](https://www.python.org/dev/peps/pep-0008/) convention for Python code.



## Prerequisites

Download and install [Python 3.7](https://www.python.org/downloads/) (or a newer version).

Additionally, [Fiona](https://github.com/Toblerity/Fiona) is required in order to use this module. Install it using the [Conda](https://docs.conda.io/en/latest/) package manager:

```
conda install -c conda-forge fiona
```

## Usage
This module supports reading and processing shapefiles given in the format found [here](https://kartkatalog.geonorge.no/metadata/2751aacf-5472-4850-a208-3532a51c529a).

### Downloading regional datasets
Follow the above link to download the `Depth data` dataset from the [Norwegian Mapping Authority](https://kartkatalog.geonorge.no/?organization=Norwegian%20Mapping%20Authority), by adding it to the Download queue and navigating to the separate [download page](https://kartkatalog.geonorge.no/nedlasting). Choose one or more county areas, and select the `WGS84 Geografisk` projection and `Shape` format. Finally, select your appropriate usergroup and purpose, and click `Download` to obtain the zip file.

### Unpacking depth data example
Place the downloaded zip file(s) in the path `data/external/zipped_charts`, where the top-level folder `data` is located in the same directory as the executing script.

Import the module and use the `unpack_chart_files` function to unzip the downloaded zip file(s) and extract desired map features:

```python
import enc

regions = ['trondelag']

terrains = [('ocean', ('depth', ), ('Dybdeareal', )), 
            ('surface', ('shore', 'land'), ('Torrfall', 'Landareal')), 
            ('objects', ('rocks', 'shallows'), ('Skjaer', 'Grunne'))]

min_longitude, min_latitude = 10.213, 63.401
max_longitude, max_latitude = 10.654, 63.601
bounding_box = min_longitude, min_latitude, max_longitude, max_latitude

ocean_depths = [0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500]   # depth bins in meters

enc.unpack_chart_files(regions, terrains, bounding_box, ocean_depths)
```

Note that `regions` contains the Norwegian counties corresponding to each downloaded zip file, and `terrains` have the form `<terrain_category>, <features_to_be_extracted>, <Norwegian_feature_names>` for each self-defined feature category.

### Reading feature shapefiles example

After the depth data is unpacked and extracted from the downloaded zip files, the shapefile data can be read by calling the `read_shapes` function for each feature category:

```python
import enc

region = 'trondelag'

min_longitude, min_latitude = 10.213, 63.401
max_longitude, max_latitude = 10.654, 63.601
bounding_box = min_longitude, min_latitude, max_longitude, max_latitude

category, feature = 'ocean', 'depth_100'
shapes = enc.read_shapes(category, feature, region, bounding_box)

for polygon_coordinates, min_depth, index in shapes:
    print('{} {} polygon number {}:'.format(category, feature, index))
    print('\tminimum depth in meters =', min_depth)
    print('\tnumber of points =', len(polygon_coordinates))
    print()

category, feature = 'surface', 'land'
shapes = enc.read_shapes(category, feature, region, bounding_box)

for polygon_coordinates, min_depth, index in shapes:
    print('{} {} polygon number {}:'.format(category, feature, index))
    print('\tminimum depth in meters =', min_depth)
    print('\tnumber of points =', len(polygon_coordinates))
    print()
```

Note that the `bounding_box` here may be different from the area used to extract the map data from the ENC datasets. This allows one to load smaller areas of interest into memory during runtime.

## Contributors

- Simon Blindheim ([simon.blindheim@ntnu.no](mailto:simon.blindheim@ntnu.no))


## License

This project uses the [MIT](https://choosealicense.com/licenses/mit/) license.