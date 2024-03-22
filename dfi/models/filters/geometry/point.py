"""A Point or vertice of a Polygon."""

from typing_extensions import Self

from dfi.errors import AltitudeOutOfBoundsError, LatitudeOutOfBoundsError, LongitudeOutOfBoundsError

LONGITUDE_MAX = 180.0
LONGITUDE_MIN = -180.0
LATITUDE_MIN = -90.0
LATITUDE_MAX = 90.0
ALTITUDE_MIN = -1.7976931348623157e308
ALTITUDE_MAX = 1.7976931348623157e308


class Point:
    """A vertice of a Polygon."""

    def __init__(self, lon: float, lat: float) -> None:
        """Create a Point from coordinates and checks bounds.

        Parameters
        ----------
        lon:
            longitude
        lat:
            latitude

        Raises
        ------
        LongitudeOutOfBoundsError
        LatitudeOutOfBoundsError

        Examples
        --------
        ```python
        Point(0.0, 1.0)
        ```
        ```python
        Point(0.0, 1.0)
        ```
        """
        self._lon = lon
        self._lat = lat
        self.validate()

    def __repr__(self) -> str:
        """Class representation."""
        return f"Point({self._lon}, {self._lat})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"Point({self._lon}, {self._lat})"

    def __eq__(self, other: object) -> bool:
        """Equality check."""
        if not isinstance(other, Point):
            return NotImplemented
        return self.__dict__ == other.__dict__

    @property
    def lon(self) -> float:
        """The longitude property."""
        return self._lon

    @property
    def lat(self) -> float:
        """The latitude property."""
        return self._lat

    @staticmethod
    def _validate_latitude(lat: float) -> None:
        """Validate the bounds of the latitude.

        Raises
        ------
        LatitudeOutOfBoundsError
        """
        if not LATITUDE_MIN < lat < LATITUDE_MAX:
            raise LatitudeOutOfBoundsError(f"Latitude value '{lat}' not within ({LATITUDE_MIN}, {LATITUDE_MAX})")

    @staticmethod
    def _validate_longitude(lon: float) -> None:
        """Validate the bounds of the latitude.

        Raises
        ------
        LongitudeOutOfBoundsError
        """
        if not LONGITUDE_MIN < lon < LONGITUDE_MAX:
            raise LongitudeOutOfBoundsError(f"Longitude value '{lon}' not within ({LONGITUDE_MIN}, {LONGITUDE_MAX})")

    @staticmethod
    def _validate_altitude(alt: float) -> None:
        """Validate the bounds of the latitude.

        Raises
        ------
        AltitudeOutOfBoundsError
        """
        if not ALTITUDE_MIN < alt < ALTITUDE_MAX:
            raise AltitudeOutOfBoundsError(f"Altitude value '{alt}' not within ({ALTITUDE_MIN}, {ALTITUDE_MAX})")

    def validate(self) -> Self:
        """Validate the Point.

        Returns
        -------
        Point

        Raises
        ------
        LongitudeOutOfBoundsError
        LatitudeOutOfBoundsError
        """
        self._validate_longitude(self._lon)
        self._validate_latitude(self._lat)
        return self

    def build(self) -> tuple[float, float]:
        """Return values formatted for the Query Document."""
        return (self._lon, self._lat)
