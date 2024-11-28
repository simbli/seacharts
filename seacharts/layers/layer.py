"""
Contains the Layer class and depth-specific types for layered spatial data.
"""
from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo
from shapely.geometry import base as geobase, Polygon, Point
from shapely.ops import unary_union

from seacharts.layers.types import ZeroDepth, SingleDepth, MultiDepth
from seacharts.shapes import Shape


@dataclass
class Layer(Shape, ABC):
    """
    Abstract base class representing a geometric layer with spatial data.

    This class serves as a foundation for all specific layer types, 
    providing common geometry handling and methods to unify geometries 
    from records.

    :param geometry: The geometry of the layer, defaulting to an empty MultiPolygon.
    :param depth: An optional depth associated with the layer.
    """
    geometry: geobase.BaseMultipartGeometry = field(default_factory=geo.MultiPolygon)
    depth: int = None
    records: list[dict] = None
    
    @property
    def label(self) -> str:
        """
        Returns the label of the layer, derived from its name.

        :return: A string representing the lowercase name of the layer.
        """
        return self.name.lower()

    def _geometries_to_multi(self, multi_geoms, geometries, geo_class):
        """
        Combines geometries into a single MultiGeometry.

        :param multi_geoms: A list of MultiGeometries to combine.
        :param geometries: A list of geometries to add to the MultiGeometry.
        :param geo_class: The class type for the resulting geometry (MultiPolygon or MultiLineString).
        :return: A unified geometry of the specified type.
        """
        if len(geometries):
            geometries = self.as_multi(geometries)
            multi_geoms.append(geometries)
        geom = unary_union(multi_geoms)
        if not isinstance(geom, geo_class):
            geom = geo_class([geom])
        return geom

    def records_as_geometry(self, records: list[dict]) -> None:
        """
        Converts a list of geometric data records into geometries for the layer.

        This method processes each record in the provided list, extracting geometric 
        representations based on the geometry type specified in each record. The 
        resulting geometries are organized into appropriate collections, which are 
        then unified into a single geometry representation for the layer.

        :param records: A list of dictionaries representing geometrical data. Each 
                        dictionary is expected to contain information necessary for 
                        constructing a geometry, which is handled by the 
                        _record_to_geometry method.

        The method distinguishes between different types of geometries:
        - Polygons and MultiPolygons are stored for area representations.
        - LineStrings and MultiLineStrings are stored for linear representations.

        If any geometries are found, they are combined into a MultiGeometry format 
        appropriate for the layer's type (either MultiPolygon or MultiLineString).
        """

        # Initialize lists to store geometries by type
        geometries = []
        multi_geoms = []
        linestrings = []
        multi_linestrings = []

        # Process each record to convert it to a geometry
        if len(records) > 0:
            for record in records:
                # Convert the record to a geometry using a helper method
                geom_tmp = self._record_to_geometry(record)

                # Classify the geometry type and append it to the corresponding list
                if isinstance(geom_tmp, geo.Polygon):
                    geometries.append(geom_tmp) # For area geometries
                elif isinstance(geom_tmp, geo.MultiPolygon):
                    multi_geoms.append(geom_tmp) # For multiple area geometries
                elif isinstance(geom_tmp, geo.LineString):
                    linestrings.append(geom_tmp) # For linear geometries
                elif isinstance(geom_tmp, geo. MultiLineString):
                    multi_linestrings.append(geom_tmp) # For multiple linear geometries

            if len(geometries) + len(multi_geoms) > 0:
                self.geometry = self._geometries_to_multi(multi_geoms, geometries, geo.MultiPolygon)

            elif len(linestrings) + len(multi_linestrings) > 0:
                self.geometry = self._geometries_to_multi(multi_linestrings, linestrings, geo.MultiLineString)
        
    def unify(self, records: list[dict]) -> None:
        """
        Unifies geometries from a list of records into the layer's geometry.

        :param records: A list of dictionaries representing geometrical data.
        """
        geometries = [self._record_to_geometry(r) for r in records]
        self.geometry = self.collect(geometries)

    def get_params_at_coord(self, easting: int, northing: int) -> dict | None:
        point = Point(easting, northing)
        for record in self.records:
            if record['geometry']['type'] == 'Polygon' and Polygon(record['geometry']['coordinates'][0]).contains(point):
                return record['properties']
        return None
    
@dataclass
class ZeroDepthLayer(Layer, ZeroDepth, ABC):
    """Layer type representing geometries at zero depth."""
    ...


@dataclass
class SingleDepthLayer(Layer, SingleDepth, ABC):
    """Layer type representing geometries at a single depth."""
    @property
    def name(self) -> str:
        """
        Returns the name of the layer including its depth.

        :return: A string representing the name of the layer with depth.
        """
        return self.__class__.__name__ + f"{self.depth}m"


@dataclass
class MultiDepthLayer(Layer, MultiDepth, ABC):
    """Layer type representing geometries at multiple depths."""
    ...


@dataclass
class WeatherLayer:
    """
    Class representing weather data at a specific time.

    :param time: The time associated with the weather data.
    :param data: A list of weather data points.
    """
    time: int
    data: list[list[float]]


@dataclass
class VirtualWeatherLayer:
    """
    Class representing a collection of weather data.

    :param name: The name of the virtual weather layer.
    :param weather: A list of WeatherLayer instances.
    """
    name: str
    weather: list[WeatherLayer]
