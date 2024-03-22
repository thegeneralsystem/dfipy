"""Integration tests for unique_id_counts on Query V1 API.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

import logging
from datetime import datetime, timezone

import pandas as pd
import pytest
from _pytest.python_api import RaisesContext

from dfi import Client
from dfi.errors import BBoxUndefinedError, DFIResponseError, PolygonUndefinedError, TimeRangeUndefinedError
from dfi.models.filters import FieldType, FilterField, FilterOperator, Only, TimeRange
from dfi.models.filters.geometry import BBox, Polygon
from dfi.models.returns import IncludeField

_logger = logging.getLogger(__name__)


@pytest.mark.order(0)
@pytest.mark.parametrize(
    "uids,geometry,time_range,filter_fields,only,include,expectation",
    [
        ("aaa", Polygon(), None, None, None, None, pytest.raises(ValueError)),
        (None, Polygon(), None, None, None, None, pytest.raises(PolygonUndefinedError)),
        (None, BBox(), None, None, None, None, pytest.raises(BBoxUndefinedError)),
        (None, None, TimeRange(), None, None, None, pytest.raises(TimeRangeUndefinedError)),
        (None, None, None, "vegetables", None, None, pytest.raises(ValueError)),
        (None, None, None, ["vegetables"], None, None, pytest.raises(ValueError)),
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
            None,
            None,
            pytest.raises(DFIResponseError),
        ),
    ],
)
def test_records_error_conditions(
    dfi: Client,
    dataset_id: str,
    uids: list[str] | None,
    geometry: Polygon | BBox | None,
    time_range: TimeRange | None,
    filter_fields: list[FilterField] | None,
    only: str | None,
    include: str | None,
    expectation: RaisesContext[
        BBoxUndefinedError | PolygonUndefinedError | TimeRangeUndefinedError | ValueError | DFIResponseError
    ],
) -> None:
    with expectation:
        _ = dfi.query.records(
            dataset_id,
            uids=uids,  # type: ignore[arg-type]
            geometry=geometry,
            time_range=time_range,
            filter_fields=filter_fields,
            only=only,  # type: ignore[arg-type]
            include=include,  # type: ignore[arg-type]
        )


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "uids,geometry,time_range,filter_fields,only,include",
    [
        pytest.param(None, None, None, None, None, None, id="all None"),
        pytest.param(["01234567-89AB-CDEF-1234-0123456789AB"], None, None, None, None, None, id="single id"),
        pytest.param(None, BBox().from_corners(0.0, 0.0, 1.0, 1.0), None, None, None, None, id="BBox().from_corners()"),
        pytest.param(None, BBox().from_list([0.0, 0.0, 1.0, 1.0]), None, None, None, None, id="BBox().from_list()"),
        pytest.param(
            None,
            Polygon().from_raw_coords([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]),
            None,
            None,
            None,
            None,
            id="Polygon().from_raw_coords()",
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
            None,
            None,
            id="Polygon().from_geojson()",
        ),
        pytest.param(
            None,
            Polygon().from_raw_coords([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]),
            None,
            None,
            None,
            None,
            id="Polygon().from_raw_coords()",
        ),
        pytest.param(
            None,
            None,
            TimeRange().from_strings("2020-01-01T00:00:00+01:00", "2020-02-01T00:00:00+01:00"),
            None,
            None,
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
            None,
            None,
            id="TimeRange().from_datetimes()",
        ),
        pytest.param(
            None,
            None,
            TimeRange().from_millis(1577836800000, 1577836801000, timezone.utc),
            None,
            None,
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
            None,
            None,
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
            None,
            None,
            id="all filters",
        ),
    ],
)
def test_query_records(
    dfi: Client,
    dataset_id: str,
    uids: list[str] | None,
    geometry: Polygon | BBox | None,
    time_range: TimeRange | None,
    filter_fields: list[FilterField] | None,
    only: Only,
    include: list[IncludeField | str],
) -> None:
    records = dfi.query.records(
        dataset_id,
        uids=uids,  # type: ignore[arg-type]
        geometry=geometry,
        time_range=time_range,
        filter_fields=filter_fields,
        only=only,
        include=include,
    )
    assert isinstance(records, pd.DataFrame)


@pytest.mark.order(2)
@pytest.mark.parametrize(
    "only",
    [
        (Only("newest")),
        (Only("oldest")),
    ],
)
def test_records_only(dfi: Client, dataset_id: str, only: Only) -> None:
    records = dfi.query.records(dataset_id, only=only)
    assert records.shape[0] == 1


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "include,expected",
    [
        pytest.param(None, 3, id="all None"),
        pytest.param([IncludeField("fields")], 4, id="[IncludeField(fields)]"),
        pytest.param([IncludeField("metadataId")], 4, id="[IncludeField(metadataId)]"),
        pytest.param(
            [IncludeField("fields"), IncludeField("metadataId")],
            5,
            id="[IncludeField(fields), IncludeField(metadataId)]",
        ),
        pytest.param(["fields"], 4, id="[fields]"),
        pytest.param(["metadataId"], 4, id="[metadataId]"),
        pytest.param(["fields", "metadataId"], 5, id="[fields, metadataId]"),
    ],
)
def test_records_include_fields(
    dfi: Client,
    dataset_id: str,
    include: list[IncludeField | str],
    expected: int,
) -> None:
    records = dfi.query.records(
        dataset_id,
        include=include,
    )
    assert records.shape[1] == expected
    records.to_parquet("records.parquet")


@pytest.mark.parametrize(
    "expected_type",
    [(dict)],
)
def test_query_records_document_set(
    dfi: Client,
    dataset_id: str,
    expected_type: type,
) -> None:
    """Test document attribute is set after successful query."""
    _ = dfi.query.records(dataset_id)

    assert isinstance(dfi.query.document, expected_type)
