"""Unit tests for Polygon."""

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import (
    LatitudeOutOfBoundsError,
    LinearRingError,
    LongitudeOutOfBoundsError,
    PolygonNotClosedError,
    PolygonUndefinedError,
)
from dfi.models.filters.geometry import Point, Polygon, RawCoords


@pytest.mark.parametrize(
    "expectation",
    [(pytest.raises(PolygonUndefinedError))],
)
def test_polygon_undefined_error_condition(expectation: RaisesContext[PolygonUndefinedError]) -> None:
    """Test PolygonUndefinedError is raised."""
    with expectation:
        Polygon().validate()


@pytest.mark.parametrize(
    "coordinates,geojson,expectation",
    [
        ([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]], True, pytest.raises(LinearRingError)),
        ([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [1.0, 1.0]], True, pytest.raises(PolygonNotClosedError)),
        (
            [[360.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [360.0, 0.0]],
            True,
            pytest.raises(LongitudeOutOfBoundsError),
        ),
        (
            [[0.0, 180.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 180.0]],
            True,
            pytest.raises(LatitudeOutOfBoundsError),
        ),
    ],
)
def test_polygon_from_raw_coords_error_conditions(
    coordinates: list[RawCoords],
    geojson: bool,
    expectation: RaisesContext[PolygonNotClosedError | LongitudeOutOfBoundsError | LatitudeOutOfBoundsError],
) -> None:
    """Test Polygon errors are raised."""
    with expectation:
        Polygon().from_raw_coords(coordinates, geojson).build()


@pytest.mark.parametrize(
    "coordinates,geojson,expected",
    [
        (
            [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
            True,
            {"type": "Polygon", "coordinates": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0))},
        ),
        (
            [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
            False,
            {"type": "Polygon", "coordinates": ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0))},
        ),
    ],
)
def test_polygon_from_raw_coords(coordinates: list[RawCoords], geojson: bool, expected: dict) -> None:
    """Test Polygon can be built from list of raw coordinate pairs."""
    assert expected == Polygon().from_raw_coords(coordinates, geojson).build()


@pytest.mark.parametrize(
    "coordinates,geojson,expectation",
    [
        ([Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0)], True, pytest.raises(LinearRingError)),
        (
            [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0), Point(1.0, 1.0)],
            True,
            pytest.raises(PolygonNotClosedError),
        ),
    ],
)
def test_polygon_from_points_error_conditions(
    coordinates: list[Point], geojson: bool, expectation: RaisesContext
) -> None:
    """Test Polygon errors are raised."""
    with expectation:
        Polygon().from_points(coordinates, geojson).build()


@pytest.mark.parametrize(
    "coordinates,geojson,expected",
    [
        (
            [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0), Point(0.0, 0.0)],
            True,
            {"type": "Polygon", "coordinates": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0))},
        ),
        (
            [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0), Point(0.0, 0.0)],
            False,
            {"type": "Polygon", "coordinates": ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0))},
        ),
    ],
)
def test_polygon_from_points(coordinates: list[Point], geojson: bool, expected: dict) -> None:
    """Test Polygon can be built from list of Points."""
    assert expected == Polygon().from_points(coordinates, geojson).build()


@pytest.mark.parametrize(
    "geojson,expectation",
    [
        pytest.param(
            {
                "type": "Polygon",
                "coordinates": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
            },
            pytest.raises(TypeError),
            id="2/3 nested lists",
        ),
        pytest.param(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
                            "type": "Polygon",
                        },
                    }
                ],
            },
            pytest.raises(TypeError),
            id="FeatureCollection",
        ),
        pytest.param(
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
                    "type": "Polygon",
                },
            },
            pytest.raises(TypeError),
            id="Feature",
        ),
        pytest.param(
            {
                "type": "MultiPolygon",
                "coordinates": [
                    [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
                    [[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75], [0.25, 0.25]],
                ],
            },
            pytest.raises(TypeError),
            id="MultiPolygon",
        ),
        pytest.param(
            {
                "type": "Linestring",
                "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]],
            },
            pytest.raises(TypeError),
            id="Linestring",
        ),
        pytest.param(
            {
                "type": "Point",
                "coordinates": [0.0, 0.0],
            },
            pytest.raises(TypeError),
            id="Point",
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]],
            },
            pytest.raises(LinearRingError),
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]],
            },
            pytest.raises(PolygonNotClosedError),
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [[[360.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [360.0, 0.0]]],
            },
            pytest.raises(LongitudeOutOfBoundsError),
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [[[0.0, 180.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 180.0]]],
            },
            pytest.raises(LatitudeOutOfBoundsError),
        ),
    ],
)
def test_polygon_from_geojson_error_conditions(
    geojson: dict,
    expectation: RaisesContext[PolygonNotClosedError | LongitudeOutOfBoundsError | LatitudeOutOfBoundsError],
) -> None:
    """Test Polygon errors are raised."""
    with expectation:
        Polygon().from_geojson(geojson).build()


@pytest.mark.parametrize(
    "geojson,expected",
    [
        (
            {
                "type": "Polygon",
                "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
            },
            {"type": "Polygon", "coordinates": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0))},
        ),
    ],
)
def test_polygon_from_geojson(geojson: dict, expected: dict) -> None:
    """Test Polygon can be built from geojson polygon."""
    assert expected == Polygon().from_geojson(geojson).build()
