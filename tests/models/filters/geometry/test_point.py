"""Unit tests for Point."""

from contextlib import nullcontext as does_not_raise

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import AltitudeOutOfBoundsError, LatitudeOutOfBoundsError, LongitudeOutOfBoundsError
from dfi.models.filters.geometry import Point


@pytest.mark.parametrize(
    "lon,expectation",
    [
        (-360.0, pytest.raises(LongitudeOutOfBoundsError)),
        (-180.0, pytest.raises(LongitudeOutOfBoundsError)),
        (-179.9, does_not_raise()),
        (0.0, does_not_raise()),
        (179.0, does_not_raise()),
        (180.0, pytest.raises(LongitudeOutOfBoundsError)),
        (360.0, pytest.raises(LongitudeOutOfBoundsError)),
    ],
)
def test_validate_longitude(lon: float, expectation: RaisesContext) -> None:
    """Test longitude value is within bounds and raises LongitudeOutOfBoundsError if not."""
    with expectation:
        Point._validate_longitude(lon)


@pytest.mark.parametrize(
    "lat,expectation",
    [
        (-180.0, pytest.raises(LatitudeOutOfBoundsError)),
        (-90.0, pytest.raises(LatitudeOutOfBoundsError)),
        (-89.9, does_not_raise()),
        (0.0, does_not_raise()),
        (89.0, does_not_raise()),
        (90.0, pytest.raises(LatitudeOutOfBoundsError)),
        (180.0, pytest.raises(LatitudeOutOfBoundsError)),
    ],
)
def test_validate_latitude(lat: float, expectation: RaisesContext) -> None:
    """Test latitude value is within bounds and raises LatitudeOutOfBoundsError if not."""
    with expectation:
        Point._validate_latitude(lat)


@pytest.mark.parametrize(
    "alt,expectation",
    [
        (-1.7976931348623157e308, pytest.raises(AltitudeOutOfBoundsError)),
        (0.0, does_not_raise()),
        (1.7976931348623157e308, pytest.raises(AltitudeOutOfBoundsError)),
    ],
)
def test_validate_altitude(alt: float, expectation: RaisesContext) -> None:
    """Test altitude value is within bounds and raises AltitudeOutOfBoundsError if not."""
    with expectation:
        Point._validate_altitude(alt)


@pytest.mark.parametrize(
    "lon,lat,expectation",
    [
        (-360.0, 0.0, pytest.raises(LongitudeOutOfBoundsError)),
        (0.0, -180.0, pytest.raises(LatitudeOutOfBoundsError)),
        (0.0, 0.0, does_not_raise()),
    ],
)
def test_point(lon: float, lat: float, expectation: RaisesContext) -> None:
    """Test Point can be built from coords and is valid."""
    with expectation:
        assert (lon, lat) == Point(lon, lat).build()
