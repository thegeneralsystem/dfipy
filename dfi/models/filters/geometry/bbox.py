"""BBox model definiton."""

from collections.abc import Sequence

from typing_extensions import Self

from dfi.errors import BBoxLatitudeMismatchError, BBoxLongitudeMismatchError, BBoxUndefinedError, BBoxValueError
from dfi.models.filters.geometry import Point

BBOX_LENGTH = 4


class BBox:
    """A 2D BBox as defined in [GeoJSON BBox](https://datatracker.ietf.org/doc/html/rfc7946#section-5)."""

    _min_lon: float
    _min_lat: float
    _max_lon: float
    _max_lat: float

    def __repr__(self) -> str:
        """Class representation."""
        return f"BBox([{self._min_lon}, {self._min_lat}, {self._max_lon}, {self._max_lat}])"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"BBox([{self._min_lon}, {self._min_lat}, {self._max_lon}, {self._max_lat}])"

    @property
    def min_lon(self) -> float:
        """The min_lon property."""
        return self._min_lon

    @property
    def min_lat(self) -> float:
        """The min_lat property."""
        return self._min_lat

    @property
    def max_lon(self) -> float:
        """The max_lon property."""
        return self._max_lon

    @property
    def max_lat(self) -> float:
        """The max_lat property."""
        return self._max_lat

    def from_corners(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> Self:
        """Create a BBox from specified longitude & latitude values.

        Parameters
        ----------
        min_lon:
            Minimum bound of the longitude.
        min_lat:
            Minimum bound of the latitude.
        max_lon:
            Maximum bound of the longitude.
        max_lat:
            Maximum bound of the latitude.

        Returns
        -------
        BBox

        Examples
        --------
        ### BBox From Corners
        ```python
        min_lon = 0.0
        min_lat = 0.0
        max_lon = 1.0
        max_lat = 1.0

        BBox().from_corners(min_lon, min_lat, max_lon, max_lat)
        ```
        ```python
        BBox([0.0, 0.0, 1.0, 1.0])
        ```
        """
        self._min_lon = min_lon
        self._min_lat = min_lat
        self._max_lon = max_lon
        self._max_lat = max_lat

        return self.validate()

    def from_list(self, bounds: list[float]) -> Self:
        """Create a BBox from a GeoJSON BBox.

        Parameters
        ----------
        bounds:
            a list of 4 floats representing [min_lon, min_lat, max_lon, max_lat].

        Returns
        -------
        BBox

        Raises
        ------
        BBoxValueError
        BBoxLongitudeMismatchError
        BBoxLatitudeMismatchError
        TypeError

        Examples
        --------
        ### BBox From List
        ```python
        BBox().from_list([0.0, 0.0, 1.0, 1.0])
        ```
        ```python
        BBox([0.0, 0.0, 1.0, 1.0])
        ```
        """
        match bounds:
            case list():
                if len(bounds) != BBOX_LENGTH:
                    raise BBoxValueError(f"BBox is defined from 4 values, {len(bounds)} given.")
                self._min_lon = bounds[0]
                self._min_lat = bounds[1]
                self._max_lon = bounds[2]
                self._max_lat = bounds[3]
            case _:
                raise TypeError("'bounds' is not of type list[float].")

        return self.validate()

    def validate(self) -> Self:
        """Validate the BBox.

        Returns
        -------
        BBox

        Raises
        ------
        BBoxLongitudeMismatchError
        BBoxLatitudeMismatchError
        """
        if not (
            hasattr(self, "_min_lon")
            or hasattr(self, "_min_lat")
            or hasattr(self, "_max_lon")
            or hasattr(self, "_max_lat")
        ):
            raise BBoxUndefinedError

        Point(self._min_lon, self._min_lat).validate()
        Point(self._max_lon, self._max_lat).validate()

        if self._min_lon >= self._max_lon:
            raise BBoxLongitudeMismatchError(f"min_lon ({self._min_lon}) is >= max_lon ({self._max_lon})")
        if self._min_lat >= self._max_lat:
            raise BBoxLatitudeMismatchError(f"min_lat ({self._min_lat}) is >= max_lat ({self._max_lat})")

        return self

    def build(self) -> dict[str, str | Sequence[float]]:
        """Validate the BBox is defined and format the BBox for use in Query Document."""
        self.validate()
        return {"type": "BoundingBox", "bounds": (self._min_lon, self._min_lat, self._max_lon, self._max_lat)}
