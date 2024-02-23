"""Integration tests for record_counts on Query V1 API.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

from datetime import datetime, timezone

import pytest
from _pytest.python_api import RaisesContext

from dfi import Client
from dfi.errors import BBoxUndefinedError, DFIResponseError, PolygonUndefinedError, TimeRangeUndefinedError
from dfi.models.filters import FieldType, FilterField, FilterOperator, TimeRange
from dfi.models.filters.geometry import BBox, Point, Polygon


@pytest.mark.order(0)
@pytest.mark.parametrize(
    "uids,geometry,time_range,filter_fields,expectation",
    [
        ("aaa", Polygon(), None, None, pytest.raises(ValueError)),
        (None, Polygon(), None, None, pytest.raises(PolygonUndefinedError)),
        (None, BBox(), None, None, pytest.raises(BBoxUndefinedError)),
        (None, None, TimeRange(), None, pytest.raises(TimeRangeUndefinedError)),
        (None, None, None, "vegetables", pytest.raises(ValueError)),
        (None, None, None, ["vegetables"], pytest.raises(ValueError)),
        (
            None,
            None,
            None,
            [
                FilterField(
                    name="ipv4",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema=None,
                )
            ],
            pytest.raises(DFIResponseError),
        ),
    ],
)
def test_record_counts_error_conditions(
    dfi: Client,
    dataset_id: str,
    uids: list[str] | None,
    geometry: Polygon | BBox | None,
    time_range: TimeRange | None,
    filter_fields: list[FilterField] | None,
    expectation: RaisesContext[BBoxUndefinedError | PolygonUndefinedError | TimeRangeUndefinedError | ValueError],
) -> None:
    with expectation:
        _ = dfi.query.record_counts(
            dataset_id, uids=uids, geometry=geometry, time_range=time_range, filter_fields=filter_fields  # type: ignore[arg-type]
        )


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "uids,geometry,time_range,filter_fields",
    [
        pytest.param(None, None, None, None, id="all None"),
        pytest.param(["01234567-89AB-CDEF-1234-0123456789AB"], None, None, None, id="single id"),
        pytest.param(None, BBox().from_corners(0.0, 0.0, 1.0, 1.0), None, None, id="BBox().from_corners()"),
        pytest.param(None, BBox().from_list([0.0, 0.0, 1.0, 1.0]), None, None, id="BBox().from_list()"),
        pytest.param(
            None,
            Polygon().from_raw_coords([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]),
            None,
            None,
            id="Polygon().from_raw_coords()",
        ),
        pytest.param(
            None,
            Polygon().from_points(
                [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 1.0), Point(0.0, 0.0)]
            ),
            None,
            None,
            id="Polygon().from_points()",
        ),
        pytest.param(
            None,
            Polygon().from_geojson(
                {
                    "type": "Polygon",
                    "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
                },
            ),
            None,
            None,
            id="Polygon().from_geojson()",
        ),
        pytest.param(
            None,
            None,
            TimeRange().from_strings("2020-01-01T00:00:00+01:00", "2020-02-01T00:00:00+01:00"),
            None,
            id="TimeRange().from_strings()",
        ),
        pytest.param(
            None,
            None,
            TimeRange().from_datetimes(
                datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2020, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
            ),
            None,
            id="TimeRange().from_datetimes()",
        ),
        pytest.param(
            None,
            None,
            TimeRange().from_millis(1577836800000, 1577836801000, timezone.utc),
            None,
            id="TimeRange().from_millis()",
        ),
        pytest.param(
            None,
            None,
            None,
            [
                FilterField(
                    name="ipv4",
                    field_type=FieldType("ip"),
                    value="0.0.0.0",
                    operation=FilterOperator("eq"),
                    schema=None,
                )
            ],
            id="FilterField(ip)",
        ),
        pytest.param(
            ["01234567-89AB-CDEF-1234-0123456789AB"],
            Polygon().from_raw_coords([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]),
            TimeRange().from_strings("2020-01-01T00:00:00+01:00", "2020-02-01T00:00:00+01:00"),
            [
                FilterField(
                    name="ipv4",
                    field_type=FieldType("ip"),
                    value="0.0.0.0",
                    operation=FilterOperator("eq"),
                    schema=None,
                )
            ],
            id="all filters",
        ),
    ],
)
def test_query_record_counts(
    dfi: Client,
    dataset_id: str,
    uids: list[str] | None,
    geometry: Polygon | BBox | None,
    time_range: TimeRange | None,
    filter_fields: list[FilterField] | None,
) -> None:
    count = dfi.query.record_counts(
        dataset_id, uids=uids, geometry=geometry, time_range=time_range, filter_fields=filter_fields  # type: ignore[arg-type]
    )
    assert isinstance(count, int)


@pytest.mark.parametrize(
    "expected_type",
    [(dict)],
)
def test_query_record_counts_document_set(
    dfi: Client,
    dataset_id: str,
    expected_type: type,
) -> None:
    """Test document attribute is set after successful query."""
    _ = dfi.query.record_counts(dataset_id)

    assert isinstance(dfi.query.document, expected_type)
