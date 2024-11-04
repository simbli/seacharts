# SeaCharts Library - Version 4.0, User Documentation

> **Important**: Current version requires Conda environment setup. Pip installation support is planned for future releases.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Configuration Setup](#configuration-setup)
3. [ENC Class for Maritime Spatial Data](#enc-class-for-maritime-spatial-data)
4. [Display Features](#display-features)
5. [Weather Visualization](#weather-visualization)
6. [Interactive Controls](#interactive-controls)
7. [Drawing Functions](#drawing-functions)
8. [Image Export](#image-export)

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/meeqn/seacharts_s57
```

2. Set up the Conda environment:
   * Use the provided `conda_requirements.txt` file:
   ```bash
   conda create --name <envname> --file conda_requirements.txt
   conda activate <envname>
   ```

3. Set up directory structure:
   * **Windows users**: Use the provided `setup.ps1` PowerShell script
   * **Other platforms**: Manually create these directories:
     * `data`
     * `data/db`
     * `data/shapefiles`

4. Download map data:
   * Download the `US1GC09M` map from [here](https://www.charts.noaa.gov/ENCs/US1GC09M.zip)
   * Extract and place the `US1GC09M` directory (found in map's ENC_ROOT directory) inside `data/db` folder

5. Test the installation:
   * Either run `test_seacharts_4_0.py` directly (may need manual setting up PYTHONPATH for run  configuration)
   * Or copy the test code into a `main.py` file in your project root directory



![Expected output](images/test_results.svg "Expected test_seacharts_4_0.py output")

### Weather Module Setup (Optional)

If you need weather functionality:

```bash
git clone https://github.com/SanityRemnants/PyThor
cd PyThor
conda create --name <envname> --file requirements.txt
conda activate -n <envname>
python app.py
```

## Configuration Setup

### Configuration File Structure

The SeaCharts library is configured via `config.yaml` located in the seacharts directory (by default). Below are the detailed configuration options:

### ENC (Electronic Navigation Chart) Configuration

```yaml
enc:
  size: [width, height]        # Size of the chart in chosen CRS unit
  origin: [lon, lat]           # Origin coordinates in chosen CRS unit (excludes center)
  center: [lon, lat]           # Center point coordinates in chosen CRS unit (excludes origin)
  crs: "coordinate_system"     # Coordinate reference system
  S57_layers:                  # List of additional S-57 layers with display colors given in hex as value
    "LAYER_NAME": "#COLOR_IN_HEX"     # e.g., "TSSLPT": "#8B0000"
  resources: [data_paths]      # Path to ENC data root, is currently a list but expects one argument
```

#### Important Notes on ENC Configuration:
- `origin` and `center` are mutually exclusive - use only one
- For `CRS`, you can use:
  - "WGS84" for **latitude/longitude coordinates** (required for `S57 maps`)
  - "UTM" with zone and hemisphere, for **easting/northing coordinates** (e.g., "UTM33N" for UTM zone 33 North, used for `FGDB maps`)
- `S57_layers` field is **required** for S57 maps (can be empty list)
- Default S-57 layers (automatically included, dont need to be specified in `S57_layers` field):
  - `LNDARE` (Land)
  - `DEPARE` (Depth Areas)
  - `COALNE` (Coastline)
- The resources directory should contain path to **only one** map
- A useful S57 layer catalogue can be found at: https://www.teledynecaris.com/s-57/frames/S57catalog.htm

### Weather Configuration

```yaml
weather:
  PyThor_address: "http://127.0.0.1:5000"  # PyThor server address
  variables: [                              # Weather variables to display
    "wave_direction",
    "wave_height",
    "wave_period",
    "wind_direction",
    "wind_speed",
    "sea_current_speed",
    "sea_current_direction",
    "tide_height"
  ]
```

### Time Configuration

```yaml
time:
  time_start: "DD-MM-YYYY HH:MM"  # Start time (must match format exactly)
  time_end: "DD-MM-YYYY HH:MM"    # End time
  period: String                  # Time period unit
  period_multiplier: Integer      # Multiplier for time period
```

#### Time Configuration Notes:
- Valid period values:
  - "hour"
  - "day"
  - "week"
  - "month"
  - "year"
- Period multiplier works with hour, day, and week periods
- For example, for 2-hour intervals:
  - period: "hour"
  - period_multiplier: 2
- Month and year periods **don't support** multipliers

### Display Configuration

```yaml
display:
  colorbar: Boolean            # Enable/disable depth colorbar (default: False)
  dark_mode: Boolean           # Enable/disable dark mode (default: False)
  fullscreen: Boolean          # Enable/disable fullscreen mode (default: False)
  controls: Boolean            # Show/hide controls window (default: True)
  resolution: Integer          # Display resolution (default: 640)
  anchor: String               # Window position ("center", "top_left", etc.)
  dpi: Integer                # Display DPI (default: 96)
```

### PyThor Configuration
For Copernicus marine data access (sea currents and tides), configure PyThor:

```yaml
coppernicus_account:
  username: "your_username"    # Copernicus marine account username
  password: "your_password"    # Copernicus marine account password
resolution: float             # Output data resolution in degrees
```

## ENC Class for Maritime Spatial Data

> **Important API Note**: All SeaCharts API functions expect coordinates in **UTM CRS** (easting and northing), regardless of the CRS set in *config.yaml*.

The ENC class provides methods for handling and visualizing maritime spatial data, including reading, storing, and plotting from specified regions.

### Key Functionalities

* **Initialization**
    * The ENC object can be initialized with a path to a config.yaml file or a Config object.

* **Geometric Data Access**
    * The ENC provides attributes for accessing spatial layers:
        * `land`: Contains land shapes.
        * `shore`: Contains shorelines.
        * `seabed`: Contains bathymetric (seafloor) data by depth.

* **Coordinate and Depth Retrieval**
    * `get_depth_at_coord(easting, northing)`: Returns the depth at a specific coordinate.
    * `is_coord_in_layer(easting, northing, layer_name)`: Checks if a coordinate falls within a specified layer.

* **Visualization**
    * `display`: Returns a Display instance to visualize marine geometric data and vessels.

* **Spatial Data Update**
    * `update()`: Parses and updates ENC data from specified resources.

### Example Usage

```python
from seacharts import ENC

# Initialize ENC with configuration
enc = ENC("config.yaml")

# Get depth at specific UTM coordinates
depth = enc.get_depth_at_coord(easting, northing)

# Check if coordinates are in a specific layer (e.g., TSSLPT)
in_traffic_lane = enc.is_coord_in_layer(easting, northing, "TSSLPT")

# Add a vessel and display
display = enc.display
display.add_vessels((1, easting, northing, 45, "red"))
display.show()
```

## Display Features

The Display class provides various methods to control the visualization:

### Basic Display Controls

```python
display.start()              # Start the display
display.show(duration=0.0)   # Show display for specified duration (0 = indefinite)
display.close()              # Close the display window
```

### View Modes

```python
display.dark_mode(enabled=True)      # Toggle dark mode
display.fullscreen(enabled=True)     # Toggle fullscreen mode
display.colorbar(enabled=True)       # Toggle depth colorbar
```

### Plot Management

```python
display.redraw_plot()    # Redraw the entire plot
display.update_plot()    # Update only animated elements
```

## Weather Visualization

Weather data can be visualized using various variables:

* Wind (speed and direction)
* Waves (height, direction, period)
* Sea currents (speed and direction)
* Tide height

The visualization type is automatically selected based on the variable:

* Scalar values: displayed as heatmaps
* Vector values: displayed as arrow maps with direction indicators

## Interactive Controls

When `controls: True` in the config, a control panel provides:

* **Time Slider**
    * Allows navigation through different timestamps with labels for date and time.
* **Layer Selection**
    * Includes radio buttons to select weather variables such as wind, waves, and sea current.

## Drawing Functions

The Display class offers various drawing functions for maritime shapes:

### Vessel Management

```python
display.add_vessels(*vessels)     # Add vessels to display
# vessels format: (id, x, y, heading, color)
display.clear_vessels()           # Remove all vessels
```

### Shape Drawing

#### Lines

```python
display.draw_line(
    points=[(x1,y1), ...],   # List of coordinate pairs
    color="color_string",     # Line color
    width=float,             # Optional: line width
    thickness=float,         # Optional: line thickness
    edge_style=str|tuple,    # Optional: line style
    marker_type=str          # Optional: point marker style
)
```
#### Circles

```python
display.draw_circle(
    center=(x, y),           # Center coordinates
    radius=float,            # Circle radius
    color="color_string",    # Circle color
    fill=Boolean,            # Optional: fill circle (default: True)
    thickness=float,         # Optional: line thickness
    edge_style=str|tuple,    # Optional: line style
    alpha=float             # Optional: transparency (0-1)
)
```

#### Rectangles

```python
display.draw_rectangle(
    center=(x, y),           # Center coordinates
    size=(width, height),    # Rectangle dimensions
    color="color_string",    # Rectangle color
    rotation=float,          # Optional: rotation in degrees
    fill=Boolean,            # Optional: fill rectangle (default: True)
    thickness=float,         # Optional: line thickness
    edge_style=str|tuple,    # Optional: line style
    alpha=float              # Optional: transparency (0-1)
)
```

#### Polygons

```python
display.draw_polygon(
    geometry=shape_geometry,  # Shapely geometry or coordinate list
    color="color_string",     # Polygon color
    interiors=[[coords]],     # Optional: interior polygon coordinates
    fill=Boolean,             # Optional: fill polygon (default: True)
    thickness=float,          # Optional: line thickness
    edge_style=str|tuple,     # Optional: line style
    alpha=float              # Optional: transparency (0-1)
)
```

#### Arrows

```python
display.draw_arrow(
    start=(x1, y1),           # Start coordinates
    end=(x2, y2),             # End coordinates
    color="color_string",      # Arrow color
    width=float,              # Optional: line width
    fill=Boolean,             # Optional: fill arrow (default: False)
    head_size=float,          # Optional: arrow head size
    thickness=float,          # Optional: line thickness
    edge_style=str|tuple      # Optional: line style
)
```

### Available color options
1. **Ship Colors**: Predefined colors specifically intended for objects or ship-related overlays. These colors have both solid and semi-transparent options:

   - **Red**: `"red"` or `#ff0000`, semi-transparent: `#ff000055`
   - **Blue**: `"blue"` or `#0000ff`, semi-transparent: `#0000ff55`
   - **Green**: `"green"` or `#00ff00`, semi-transparent: `#00ff0055`
   - **Yellow**: `"yellow"` or `#ffff00`, semi-transparent: `#ffff0055`
   - **Cyan**: `"cyan"` or `#00ffff`, semi-transparent: `#00ffff55`
   - **Magenta**: `"magenta"` or `#ff00ff`, semi-transparent: `#ff00ff55`
   - **Pink**: `"pink"` or `#ff88ff`, semi-transparent: `#ff88ff55`
   - **Purple**: `"purple"` or `#bb22ff`, semi-transparent: `#bb22ff55`
   - **Orange**: `"orange"` or `#ff9900`, semi-transparent: `#ff990055`
   - **White**: `"white"` or `#ffffff`, semi-transparent: `#ffffff77`
   - **Grey Variants**:
     - Light Grey: `"lightgrey"` or `#b7b7b7`, semi-transparent: `#b7b7b755`
     - Grey: `"grey"` or `#666666`, semi-transparent: `#66666655`
     - Dark Grey: `"darkgrey"` or `#333333`, semi-transparent: `#33333355`
   - **Black**: `"black"` or `#000000`, semi-transparent: `#00000077`

2. **Horizon Colors**: Specialized colors for visualizing different regions of a horizon. Each area has a unique color, with both solid and semi-transparent options:

   - **Full Horizon**: `"full_horizon"` or `#ffffff55`, very transparent: `#ffffff11`
   - **Starboard Bow**: `"starboard_bow"` or `#00ff0099`, semi-transparent: `#00ff0055`
   - **Starboard Side**: `"starboard_side"` or `#33ff3399`, semi-transparent: `#33ff3355`
   - **Starboard Aft**: `"starboard_aft"` or `#ccffcc99`, semi-transparent: `#ccffcc55`
   - **Rear Aft**: `"rear_aft"` or `#eeeeee99`, semi-transparent: `#eeeeee55`
   - **Port Aft**: `"port_aft"` or `#ffcccc99`, semi-transparent: `#ffcccc55`
   - **Port Side**: `"port_side"` or `#ff333388`, semi-transparent: `#ff333355`
   - **Port Bow**: `"port_bow"` or `#ff000066`, semi-transparent: `#ff000055`

3. **Layer Colors**: Colors that represent specific environmental layers, created by sampling from colormaps. These can be useful for visualizing different regions of a plot:

   - **Seabed**: `"Seabed"`, a deep shade of blue from the "Blues" colormap
   - **Land**: `"Land"`, a rich green from the "Greens" colormap
   - **Shore**: `"Shore"`, a lighter shade of green from the "Greens" colormap
   - **Highlight**: `"highlight"`, a semi-transparent white: `#ffffff44`
   - **Blank**: `"blank"`, an opaque white: `#ffffffff`

4. **CSS4 Color Names**: Any color name from the CSS4 color set is supported. These are standard color names recognized by most plotting libraries, including `matplotlib`. Examples include:
   - `"aliceblue"`
   - `"antiquewhite"`
   - `"aqua"`
   - `"aquamarine"`
   - `"azure"`
   - (and many more CSS4 color names...)

5. **Hexadecimal Color Codes**: Custom colors can be specified directly using hexadecimal color codes. Accepted formats include:
   - **RGB**: `"#RRGGBB"` or `"#RGB"`
   - **RGBA**: `"#RRGGBBAA"` or `"#RGBA"`

   For example:
   - Solid blue: `"#0000FF"`
   - Semi-transparent red: `"#FF000080"`

## Image Export

The `save_image` function allows you to export the current display or plot as an image file. This function offers several customizable options for setting the file name, location, resolution, and file format. It wraps around the internal `_save_figure` method, which handles the actual saving and setting of default values when specific parameters are not provided.

### Usage

```python
display.save_image(
    name=str,               # Optional: output filename (default: current window title)
    path=Path,              # Optional: output directory path (default: "reports/")
    scale=float,            # Optional: resolution scaling factor (default: 1.0)
    extension=str           # Optional: file format extension (default: "png")
)
```

## End note
We recommend checking out files placed in `tests` directory as reference, to get familiar with the SeaCharts usage.