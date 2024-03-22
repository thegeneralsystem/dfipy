"""Unit tests for QueryDocument."""

import logging
from datetime import datetime

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import (
    BBoxUndefinedError,
    InvalidQueryDocument,
    PolygonUndefinedError,
    TimeRangeUndefinedError,
)
from dfi.models import QueryDocument
from dfi.models.filters import FieldType, FilterField, FilterOperator, Only, TimeRange
from dfi.models.filters.geometry import BBox, Point, Polygon, RawCoords
from dfi.models.returns import Count, GroupBy, Records

_logger = logging.getLogger(__name__)

#########################
# Error Conditions
#########################


@pytest.mark.parametrize(
    "dataset_id,return_model,expectation",
    [
        (None, Records(), pytest.raises(InvalidQueryDocument)),
        (1234, Records(), pytest.raises(InvalidQueryDocument)),
        ("test-dataset", None, pytest.raises(InvalidQueryDocument)),
        ("test-dataset", "records", pytest.raises(InvalidQueryDocument)),
    ],
)
def test_query_document_initialization_error_conditions(
    dataset_id: str | None,
    return_model: Records | Count | None,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test QueryDocument errors are raised."""
    with expectation:
        _ = QueryDocument(
            dataset_id=dataset_id,  # type: ignore
            return_model=return_model,  # type: ignore
        ).build()


@pytest.mark.parametrize(
    "dataset_id,return_model,expectation",
    [
        ("test-dataset", Records(), pytest.raises(InvalidQueryDocument)),
    ],
)
def test_set_dataset_id_error_conditions(
    dataset_id: str,
    return_model: Records | Count,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test QueryDocument errors are raised when an invalid dataset_id is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_dataset_id(None)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,expectation",
    [
        ("test-dataset", None, pytest.raises(InvalidQueryDocument)),
        ("test-dataset", "records", pytest.raises(InvalidQueryDocument)),
    ],
)
def test_set_return_model_error_conditions(
    dataset_id: str,
    return_model: Records | str | None,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test QueryDocument errors are raised when an invalid return_model is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=Count(),
            )
            .set_return_model(return_model)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,only,expectation",
    [
        ("test-dataset", Count(), "newest", pytest.raises(InvalidQueryDocument)),
        (
            "test-dataset",
            Count(groupby=GroupBy("uniqueId")),
            Only("newest"),
            pytest.raises(InvalidQueryDocument),
        ),
        (
            "test-dataset",
            Count(groupby=GroupBy("uniqueId")),
            Only("oldest"),
            pytest.raises(InvalidQueryDocument),
        ),
    ],
)
def test_set_only_error_conditions(
    dataset_id: str,
    return_model: Count,
    only: Only | str | None,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test QueryDocument errors are raised when an invalid only filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_only(only)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,uids,expectation",
    [
        ("test-dataset", Count(), "aaa", pytest.raises(ValueError)),
    ],
)
def test_set_uids_error_conditions(
    dataset_id: str,
    return_model: Count,
    uids: str,
    expectation: RaisesContext[ValueError],
) -> None:
    """Test QueryDocument errors are raised when an invalid only filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_uids(uids)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,time_range,expectation",
    [
        (
            "test-dataset",
            Count(),
            datetime(2020, 1, 1, 0, 0, 0),
            pytest.raises(ValueError),
        ),
        (
            "test-dataset",
            Count(),
            (datetime(2020, 1, 1, 0, 0, 0), datetime(2020, 1, 2, 0, 0, 0)),
            pytest.raises(ValueError),
        ),
        ("test-dataset", Count(), "2020-01-01T00:00:00", pytest.raises(ValueError)),
        (
            "test-dataset",
            Count(),
            ("2020-01-01T00:00:00", "2020-01-02T00:00:00"),
            pytest.raises(ValueError),
        ),
        ("test-dataset", Count(), TimeRange(), pytest.raises(TimeRangeUndefinedError)),
    ],
)
def test_set_time_range_error_conditions(
    dataset_id: str,
    return_model: Count,
    time_range: str,
    expectation: RaisesContext[ValueError],
) -> None:
    """Test QueryDocument errors are raised when an invalid TimeRange filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_time_range(time_range)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,geometry,expectation",
    [
        (
            "test-dataset",
            Count(),
            [
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                Point(1.0, 1.0),
                Point(0.0, 1.0),
                Point(0.0, 0.0),
            ],
            pytest.raises(ValueError),
        ),
        (
            "test-dataset",
            Count(),
            [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],
            pytest.raises(ValueError),
        ),
        (
            "test-dataset",
            Count(),
            Polygon(),
            pytest.raises(PolygonUndefinedError),
        ),
        (
            "test-dataset",
            Count(),
            BBox(),
            pytest.raises(BBoxUndefinedError),
        ),
    ],
)
def test_set_geometry_error_conditions(
    dataset_id: str,
    return_model: Count,
    geometry: list[RawCoords] | list[Point],
    expectation: RaisesContext[ValueError | PolygonUndefinedError | BBoxUndefinedError],
) -> None:
    """Test QueryDocument errors are raised when an invalid geometry filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_geometry(geometry)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,filter_field,expectation",
    [
        (
            "test-dataset",
            Count(),
            None,
            pytest.raises(ValueError),
        ),
        (
            "test-dataset",
            Count(),
            {"vegetable": "cauliflower"},
            pytest.raises(ValueError),
        ),
    ],
)
def test_set_filter_field_error_conditions(
    dataset_id: str,
    return_model: Count,
    filter_field: dict[str, str] | None,
    expectation: RaisesContext[ValueError],
) -> None:
    """Test QueryDocument errors are raised when an invalid Filter Field filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_filter_field(filter_field)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,return_model,filter_fields,expectation",
    [
        (
            "test-dataset",
            Count(),
            {"vegetable": "cauliflower"},
            pytest.raises(ValueError),
        ),
        (
            "test-dataset",
            Count(),
            [{"vegetable": "cauliflower"}, {"ip": "0.0.0.0"}],
            pytest.raises(ValueError),
        ),
    ],
)
def test_set_filter_fields_error_conditions(
    dataset_id: str,
    return_model: Count,
    filter_fields: list[dict[str, str]] | dict[str, str],
    expectation: RaisesContext[ValueError],
) -> None:
    """Test QueryDocument errors are raised when an invalid Filter Fields filter is set."""
    with expectation:
        _ = (
            QueryDocument(
                dataset_id=dataset_id,
                return_model=return_model,
            )
            .set_filter_fields(filter_fields)  # type: ignore
            .build()
        )


@pytest.mark.parametrize(
    "dataset_id,expectation",
    [
        (None, pytest.raises(InvalidQueryDocument)),
        (1234, pytest.raises(InvalidQueryDocument)),
    ],
)
def test_validate_dataset_id_raises_errors(
    dataset_id: int | None,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test _validate_dataset_id errors are raised when an invalid dataset_id is set."""
    with expectation:
        QueryDocument._validate_dataset_id(dataset_id)  # type: ignore


@pytest.mark.parametrize(
    "return_model,expectation",
    [
        (None, pytest.raises(InvalidQueryDocument)),
        ("records", pytest.raises(InvalidQueryDocument)),
    ],
)
def test_validate_return_model_raises_errors(
    return_model: str | None,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test _validate_return_model errors are raised when an invalid return_model is set."""
    with expectation:
        QueryDocument._validate_return_model(return_model)  # type: ignore


@pytest.mark.parametrize(
    "only,return_model,expectation",
    [
        (Only("newest"), Count(), pytest.raises(InvalidQueryDocument)),
        (Only("oldest"), Count(), pytest.raises(InvalidQueryDocument)),
        (
            Only("newest"),
            Count(groupby=GroupBy("uniqueId")),
            pytest.raises(InvalidQueryDocument),
        ),
        (
            Only("oldest"),
            Count(groupby=GroupBy("uniqueId")),
            pytest.raises(InvalidQueryDocument),
        ),
    ],
)
def test_validate_only_filter_raises_errors(
    only: str | None,
    return_model: Count,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test _validate_only_filter errors are raised when an invalid only filter and return_model are set."""
    with expectation:
        QueryDocument._validate_only_filter(only, return_model)  # type: ignore


@pytest.mark.parametrize(
    "dataset_id,return_model,only,expectation",
    [
        (None, None, None, pytest.raises(InvalidQueryDocument)),
        ("test-dataset", None, None, pytest.raises(InvalidQueryDocument)),
        ("test-dataset", "records", None, pytest.raises(InvalidQueryDocument)),
        (None, Records(), None, pytest.raises(InvalidQueryDocument)),
        (1234, Records(), None, pytest.raises(InvalidQueryDocument)),
        # invalid only x return_model combos
        ("test-dataset", Only("newest"), Count(), pytest.raises(InvalidQueryDocument)),
        ("test-dataset", Only("oldest"), Count(), pytest.raises(InvalidQueryDocument)),
        (
            "test-dataset",
            Only("newest"),
            Count(groupby=GroupBy("uniqueId")),
            pytest.raises(InvalidQueryDocument),
        ),
        (
            "test-dataset",
            Only("oldest"),
            Count(groupby=GroupBy("uniqueId")),
            pytest.raises(InvalidQueryDocument),
        ),
    ],
)
def test_validate_raises_errors(
    dataset_id: str | int | None,
    return_model: Records | Count | str | None,
    only: Only,
    expectation: RaisesContext[InvalidQueryDocument],
) -> None:
    """Test _validate_return_model errors are raised when an invalid return_model is set."""
    with expectation:
        QueryDocument(dataset_id=dataset_id, return_model=return_model, only=only).validate()  # type: ignore


#########################
# Normal Conditions
#########################
@pytest.mark.parametrize(
    "dataset_id,return_model,uids,geometry,time_range,filter_fields,only,expected",
    [
        (
            "test-dataset",
            Records(),
            None,
            None,
            None,
            None,
            None,
            {"datasetId": "test-dataset", "filters": {}, "return": {"type": "records"}},
        ),
        (
            "test-dataset",
            Records(),
            ["aaa"],
            Polygon().from_raw_coords(
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
            ),
            TimeRange().from_strings(
                "2020-01-01T00:00:00+00:00", "2020-01-01T00:00:01+00:00"
            ),
            [
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                    },
                ),
            ],
            Only("newest"),
            {
                "datasetId": "test-dataset",
                "filters": {
                    "id": ["aaa"],
                    "geo": {
                        "type": "Polygon",
                        "coordinates": (
                            (0.0, 0.0),
                            (1.0, 0.0),
                            (1.0, 1.0),
                            (0.0, 1.0),
                            (0.0, 0.0),
                        ),
                    },
                    "time": {
                        "maxTime": "2020-01-01T00:00:01+00:00",
                        "minTime": "2020-01-01T00:00:00+00:00",
                    },
                    "only": "newest",
                    "fields": {"delta distance": {"outside": [-22, 0]}},
                },
                "return": {"type": "records"},
            },
        ),
    ],
)
def test_query_document(
    dataset_id: str,
    return_model: Records,
    uids: list[str | int] | None,
    geometry: Polygon | BBox | None,
    time_range: TimeRange | None,
    filter_fields: list[FilterField] | None,
    only: Only | None,
    expected: dict,
) -> None:
    """Test QueryDocument can be built from inputs."""
    document = QueryDocument(
        dataset_id=dataset_id,
        return_model=return_model,
        uids=uids,  # type: ignore
        geometry=geometry,
        time_range=time_range,
        filter_fields=filter_fields,
        only=only,
    ).build()

    assert expected == document


@pytest.mark.parametrize("dataset_id", [("test-dataset")])
def test_validate_dataset_id(dataset_id: str) -> None:
    """Test validate_dataset_id does not raise error when valid dataset_id given."""
    QueryDocument._validate_dataset_id(dataset_id)


@pytest.mark.parametrize(
    "return_model", [(Count()), (Count(groupby=GroupBy("uniqueId"))), (Records())]
)
def test_validate_return_model(return_model: Records | Count) -> None:
    """Test validate_return_model does not raise error when valid return_model given."""
    QueryDocument._validate_return_model(return_model)


@pytest.mark.parametrize(
    "dataset_id,return_model",
    [
        ("test-dataset", Count()),
        ("test-dataset", Count(groupby=GroupBy("uniqueId"))),
        ("test-dataset", Records()),
    ],
)
def test_validate(dataset_id: str, return_model: Records | Count) -> None:
    """Test validate does not raise error when valid dataset_id and return_model given."""
    QueryDocument(dataset_id=dataset_id, return_model=return_model).validate()


@pytest.mark.parametrize(
    "dataset_id,return_model,expected",
    [
        (
            "test-dataset-2",
            Records(),
            {
                "datasetId": "test-dataset-2",
                "filters": {},
                "return": {"type": "records"},
            },
        ),
    ],
)
def test_set_dataset_id(dataset_id: str, return_model: Records, expected: dict) -> None:
    """Test set_dataset_id builds properly."""
    assert (
        expected
        == QueryDocument("test-dataset", return_model)
        .set_dataset_id(dataset_id)
        .build()
    )


@pytest.mark.parametrize(
    "dataset_id,initial_return_model,return_model,expected",
    [
        (
            "test-dataset",
            Records(),
            Count(),
            {"datasetId": "test-dataset", "filters": {}, "return": {"type": "count"}},
        ),
        (
            "test-dataset",
            Count(),
            Count(groupby=GroupBy("uniqueId")),
            {
                "datasetId": "test-dataset",
                "filters": {},
                "return": {"type": "count", "groupBy": {"type": "uniqueId"}},
            },
        ),
        (
            "test-dataset",
            Count(),
            Records(),
            {"datasetId": "test-dataset", "filters": {}, "return": {"type": "records"}},
        ),
    ],
)
def test_set_return_model(
    dataset_id: str,
    initial_return_model: Records | Count,
    return_model: Records | Count,
    expected: dict,
) -> None:
    """Test set_return_model build properly."""
    assert (
        expected
        == QueryDocument(dataset_id, initial_return_model)
        .set_return_model(return_model)
        .build()
    )


@pytest.mark.parametrize(
    "dataset_id,return_model,only,expected",
    [
        (
            "test-dataset",
            Records(),
            Only("newest"),
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"only": "newest"},
            },
        ),
        (
            "test-dataset",
            Records(),
            Only("oldest"),
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"only": "oldest"},
            },
        ),
        (
            "test-dataset",
            Records(),
            "newest",
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"only": "newest"},
            },
        ),
        (
            "test-dataset",
            Records(),
            "oldest",
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"only": "oldest"},
            },
        ),
        (
            "test-dataset",
            Records(),
            None,
            {"datasetId": "test-dataset", "return": {"type": "records"}, "filters": {}},
        ),
    ],
)
def test_set_only(
    dataset_id: str, return_model: Records, only: Only | None, expected: dict
) -> None:
    """Test set_only builds properly."""
    assert expected == QueryDocument(dataset_id, return_model).set_only(only).build()


@pytest.mark.parametrize(
    "dataset_id,return_model,uids,expected",
    [
        (
            "test-dataset",
            Records(),
            ["aaa"],
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"id": ["aaa"]},
            },
        ),
        (
            "test-dataset",
            Records(),
            None,
            {"datasetId": "test-dataset", "return": {"type": "records"}, "filters": {}},
        ),
    ],
)
def test_set_uids(
    dataset_id: str, return_model: Records, uids: list[str | int] | None, expected: dict
) -> None:
    """Test set_uids builds properly."""
    assert expected == QueryDocument(dataset_id, return_model).set_uids(uids).build()


@pytest.mark.parametrize(
    "dataset_id,return_model,time_range,expected",
    [
        (
            "test-dataset",
            Records(),
            TimeRange().from_strings(
                "2020-01-01T00:00:00+00:00", "2020-01-01T00:00:01+00:00"
            ),
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {
                    "time": {
                        "minTime": "2020-01-01T00:00:00+00:00",
                        "maxTime": "2020-01-01T00:00:01+00:00",
                    }
                },
            },
        ),
        (
            "test-dataset",
            Records(),
            None,
            {"datasetId": "test-dataset", "return": {"type": "records"}, "filters": {}},
        ),
    ],
)
def test_set_time_range(
    dataset_id: str, return_model: Records, time_range: TimeRange | None, expected: dict
) -> None:
    """Test set_time_range builds properly."""
    assert (
        expected
        == QueryDocument(dataset_id, return_model).set_time_range(time_range).build()
    )


@pytest.mark.parametrize(
    "dataset_id,return_model,geometry,expected",
    [
        (
            "test-dataset",
            Records(),
            Polygon().from_raw_coords(
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
            ),
            {
                "datasetId": "test-dataset",
                "filters": {
                    "geo": {
                        "type": "Polygon",
                        "coordinates": (
                            (0.0, 0.0),
                            (1.0, 0.0),
                            (1.0, 1.0),
                            (0.0, 1.0),
                            (0.0, 0.0),
                        ),
                    }
                },
                "return": {"type": "records"},
            },
        ),
        (
            "test-dataset",
            Records(),
            BBox().from_corners(0.0, 0.0, 1.0, 1.0),
            {
                "datasetId": "test-dataset",
                "filters": {
                    "geo": {"type": "BoundingBox", "bounds": (0.0, 0.0, 1.0, 1.0)}
                },
                "return": {"type": "records"},
            },
        ),
        (
            "test-dataset",
            Records(),
            None,
            {"datasetId": "test-dataset", "return": {"type": "records"}, "filters": {}},
        ),
    ],
)
def test_set_geometry(
    dataset_id: str,
    return_model: Records,
    geometry: Polygon | BBox | None,
    expected: dict,
) -> None:
    """Test set_geometry builds properly."""
    assert (
        expected
        == QueryDocument(dataset_id, return_model).set_geometry(geometry).build()
    )


@pytest.mark.parametrize(
    "dataset_id,return_model,filter_field,expected",
    [
        (
            "test-dataset",
            Records(),
            FilterField(
                name="delta distance",
                field_type=FieldType("signed number"),
                value=[-22, 0],
                operation=FilterOperator("outside"),
                schema={
                    "absolute distance": {"type": "number", "signed": False},
                    "delta distance": {"type": "number", "signed": True},
                },
            ),
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"fields": {"delta distance": {"outside": [-22, 0]}}},
            },
        ),
    ],
)
def test_set_filter_field(
    dataset_id: str, return_model: Records, filter_field: FilterField, expected: dict
) -> None:
    """Test set_filter_field builds properly."""
    assert (
        expected
        == QueryDocument(dataset_id, return_model)
        .set_filter_field(filter_field)
        .build()
    )


@pytest.mark.parametrize(
    "dataset_id,return_model,filter_fields,expected",
    [
        pytest.param(
            "test-dataset",
            Records(),
            [
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                    },
                ),
            ],
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"fields": {"delta distance": {"outside": [-22, 0]}}},
            },
            id="single field",
        ),
        pytest.param(
            "test-dataset",
            Records(),
            [
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                    },
                ),
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("between"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                    },
                ),
            ],
            {
                "datasetId": "test-dataset",
                "return": {"type": "records"},
                "filters": {"fields": {"delta distance": {"between": [-22, 0]}}},
            },
            id="new field with same name overwrites existing field",
        ),
        pytest.param(
            "test-dataset",
            Records(),
            None,
            {"datasetId": "test-dataset", "return": {"type": "records"}, "filters": {}},
            id="None deletes all fields",
        ),
    ],
)
def test_set_filter_fields(
    dataset_id: str,
    return_model: Records,
    filter_fields: list[FilterField] | None,
    expected: dict,
) -> None:
    """Test set_filter_field builds properly."""
    assert (
        expected
        == QueryDocument(dataset_id, return_model)
        .set_filter_fields(filter_fields)
        .build()
    )
