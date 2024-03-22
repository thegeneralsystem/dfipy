"""Unit tests for BBox."""

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import (
    BBoxLatitudeMismatchError,
    BBoxLongitudeMismatchError,
    BBoxUndefinedError,
    BBoxValueError,
    LatitudeOutOfBoundsError,
    LongitudeOutOfBoundsError,
)
from dfi.models.filters.geometry import BBox


@pytest.mark.parametrize(
    "expectation",
    [(pytest.raises(BBoxUndefinedError))],
)
def test_bbox_undefined_error_condition(expectation: RaisesContext[BBoxUndefinedError]) -> None:
    """Test AttributeError is raised when validating an uninitialized BBox."""
    with expectation:
        BBox().validate()


@pytest.mark.parametrize(
    "min_lon,min_lat,max_lon,max_lat,expectation",
    [
        (1.0, 0.0, 0.0, 1.0, pytest.raises(BBoxLongitudeMismatchError)),
        (0.0, 1.0, 1.0, 0.0, pytest.raises(BBoxLatitudeMismatchError)),
        (0.0, 0.0, 360.0, 1.0, pytest.raises(LongitudeOutOfBoundsError)),
        (0.0, 0.0, 1.0, 180.0, pytest.raises(LatitudeOutOfBoundsError)),
    ],
)
def test_bbox_from_corners_error_conditions(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    expectation: RaisesContext[
        BBoxLongitudeMismatchError | BBoxLatitudeMismatchError | LongitudeOutOfBoundsError | LatitudeOutOfBoundsError
    ],
) -> None:
    """Test BBox errors are raised."""
    with expectation:
        BBox().from_corners(min_lon, min_lat, max_lon, max_lat).build()


@pytest.mark.parametrize(
    "min_lon,min_lat,max_lon,max_lat,expected",
    [
        (0.0, 0.0, 1.0, 1.0, {"type": "BoundingBox", "bounds": (0.0, 0.0, 1.0, 1.0)}),
    ],
)
def test_bbox_from_corners(min_lon: float, min_lat: float, max_lon: float, max_lat: float, expected: dict) -> None:
    """Test Polygon can be built from list of Points."""
    assert expected == BBox().from_corners(min_lon, min_lat, max_lon, max_lat).build()


@pytest.mark.parametrize(
    "bounds,expectation",
    [
        ([1.0, 0.0, 0.0, 1.0], pytest.raises(BBoxLongitudeMismatchError)),
        ([0.0, 1.0, 1.0, 0.0], pytest.raises(BBoxLatitudeMismatchError)),
        ([0.0, 0.0, 360.0, 1.0], pytest.raises(LongitudeOutOfBoundsError)),
        ([0.0, 0.0, 1.0, 180.0], pytest.raises(LatitudeOutOfBoundsError)),
        ([0.0, 0.0, 1.0, 1.0, 1.0], pytest.raises(BBoxValueError)),
        ([0.0, 0.0, 1.0], pytest.raises(BBoxValueError)),
    ],
)
def test_bbox_from_list_error_conditions(
    bounds: list[float],
    expectation: RaisesContext[
        BBoxLongitudeMismatchError | BBoxLatitudeMismatchError | LongitudeOutOfBoundsError | LatitudeOutOfBoundsError
    ],
) -> None:
    """Test BBox errors are raised."""
    with expectation:
        BBox().from_list(bounds).build()


@pytest.mark.parametrize(
    "bounds,expected",
    [([0.0, 0.0, 1.0, 1.0], {"type": "BoundingBox", "bounds": (0.0, 0.0, 1.0, 1.0)})],
)
def test_bbox_from_list(bounds: list[float], expected: tuple[float]) -> None:
    """Test BBox can be built from list."""
    assert expected == BBox().from_list(bounds).build()
