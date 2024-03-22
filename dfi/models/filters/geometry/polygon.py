"""Polygon model definition."""

from typing import Any, TypeAlias

from typing_extensions import Self

from dfi.errors import LinearRingError, PolygonNotClosedError, PolygonUndefinedError
from dfi.models.filters.geometry import Point

RawCoords: TypeAlias = tuple[float, float]
"""Alias for `tuple[float, float]`"""

MIN_VERTICES = 4


class Polygon:
    """A 2D Polygon as defined in GeoJSON https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6.

    ??? attention
        Polygons should be composed of a singular linear ring.  MultiPolygons are not supported.

    """

    _coordinates: tuple[Point, ...]

    def __repr__(self) -> str:
        """Class representation."""
        return f"Polygon({self._coordinates})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"Polygon({self._coordinates})"

    @property
    def coordinates(self) -> tuple[Point, ...]:
        """The coordinates property."""
        return self._coordinates

    def from_geojson(self, geojson: dict[str, Any]) -> Self:
        """Create a Polygon from a given GeoJSON Polygon.

        Parameters
        ----------
        geojson:
            a geojson dictionary.

        Raises
        ------
        LinearRingError
        PolygonNotClosedError
        PolygonUndefinedError

        Examples
        --------
        ### Polygon from Points
        ```python
        geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [0.0, 1.0],
                    [0.0, 0.0],
                ]
            ],
        }
        Polygon().from_geojson(geojson)
        ```
        ```python
        Polygon(
            (
                Point(0.0, 0.0),
                Point(0.0, 1.0),
                Point(1.0, 1.0),
                Point(1.0, 0.0),
                Point(0.0, 0.0),
            )
        )
        ```
        """
        match geometry := geojson.get("type"):
            case "Polygon":
                coordinates = geojson["coordinates"][0]
                self._coordinates = tuple(Point(lon, lat) for lon, lat in coordinates)
            case "FeatureCollection" | "Feature" | "MultiPolygon" | "LineString" | "Point":
                raise TypeError(f"'geojson' is not a Polygon, found {geometry}.")
            case _:
                raise TypeError("'geojson' could not be parsed.")

        return self.validate()

    def from_points(self, coordinates: list[Point], geojson: bool = True) -> Self:
        """Create a Polygon from given coordinates.

        Parameters
        ----------
        coordinates:
            a list of Points.
        geojson:
            indicates if coordinate order follow GeoJSON specification.

            - if `True` expects coordinates with the form (longitude, latitude)
            - if `False` expects coordinates with the form (latitude, longitude)

        Returns
        -------
        Polygon

        Raises
        ------
        LinearRingError
        PolygonNotClosedError
        PolygonUndefinedError

        Examples
        --------
        ### Polygon from Points
        ```python
        raw_coords = [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            [0.0, 0.0],
        ]
        points = [Point(p.lon, p.lat) for p in raw_coords]
        Polygon().from_points(points)
        ```
        ```python
        Polygon(
            (
                Point(0.0, 0.0),
                Point(0.0, 1.0),
                Point(1.0, 1.0),
                Point(1.0, 0.0),
                Point(0.0, 0.0),
            )
        )
        ```
        """
        match coordinates:
            case list() | tuple():
                pass
            case _:
                raise TypeError("'coordinates' is not of type list[float].")
        if geojson:
            self._coordinates = tuple(coordinates)
        else:
            self._coordinates = tuple(Point(point.lat, point.lon) for point in coordinates)

        return self.validate()

    def from_raw_coords(self, coordinates: list[RawCoords], geojson: bool = True) -> Self:
        """Create a Polygon from given coordinates.

        Parameters
        ----------
        coordinates:
            a list of RawCoords (i.e. list[float, float]).
        geojson:
            indicates if coordinate order follow GeoJSON specification.

            - if `True` expects coordinates with the form (longitude, latitude)
            - if `False` expects coordinates with the form (latitude, longitude)

        Returns
        -------
        Polygon

        Raises
        ------
        LinearRingError
        PolygonNotClosedError
        PolygonUndefinedError

        Examples
        --------
        ### Polygon from RawCoords
        From RawCoords is useful when the coordinates of the Polygon are in a list.
        ```python
        raw_coords = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]
        points =
        Polygon().from_raw_coords(raw_coords)
        ```
        ```python
        Polygon(
            (
                Point(0.0, 0.0),
                Point(0.0, 1.0),
                Point(1.0, 1.0),
                Point(1.0, 0.0),
                Point(0.0, 0.0),
            )
        )
        ```
        """
        if geojson:
            self._coordinates = tuple(Point(lon, lat) for lon, lat in coordinates)
        else:
            self._coordinates = tuple(Point(lon, lat) for lat, lon in coordinates)

        return self.validate()

    def validate(self) -> Self:
        """Validate the Polygon.

        Returns
        -------
        Polygon

        Raises
        ------
        LinearRingError
        PolygonNotClosedError
        PolygonUndefinedError
        """
        if not hasattr(self, "_coordinates"):
            raise PolygonUndefinedError

        if len(self._coordinates) < MIN_VERTICES:
            raise LinearRingError(
                f"Polygons should be a linear rings with four or more points - only {len(self._coordinates)} found."
            )
        if self._coordinates[0] != self._coordinates[-1]:
            raise PolygonNotClosedError("Polygons should be a linear ring - first and last points are not identical.")

        return self

    def build(self) -> dict[str, str | tuple[RawCoords, ...]]:
        """Validate the polygon is defined and format the polygon for the Query Document."""
        self.validate()
        return {"type": "Polygon", "coordinates": tuple(point.build() for point in self._coordinates)}
