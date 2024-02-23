"""Tests for raw_request.

- Tests do not check for correctness of the query, only that results are parsed correctly.
- Only the return options are tested here because `dfi.query.raw_request` passes a raw document
    to the API and only needs to know the return type so it can parse the different responses.
"""

import logging

import pandas as pd
import pytest

from dfi import Client

_logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "document,expected_type",
    [
        pytest.param({"return": "count"}, int, id="record_count (simple)"),
        pytest.param({"return": {"type": "count"}}, int, id="record_count"),
        pytest.param(
            {"return": {"type": "count", "groupBy": {"type": "uniqueId"}}},
            dict,
            id="unique_id_counts",
        ),
        pytest.param(
            {"return": {"type": "records"}},
            pd.DataFrame,
            id="records",
        ),
    ],
)
def test_raw_request_result_type(
    dfi: Client,
    dataset_id: str,
    document: dict,  # type: ignore[type-arg]
    expected_type: type,
) -> None:
    """Test raw_request works as intended."""
    document["datasetId"] = dataset_id
    result = dfi.query.raw_request(document)
    assert isinstance(result, expected_type)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "document,expected_type,include",
    [
        pytest.param(
            {"return": {"type": "records", "include": ["metadataId"]}},
            pd.DataFrame,
            ["metadataId"],
            id="records-metadataId",
        ),
        pytest.param(
            {"return": {"type": "records", "include": ["fields"]}},
            pd.DataFrame,
            ["fields"],
            id="records-fields",
        ),
        pytest.param(
            {"return": {"type": "records", "include": ["metadataId", "fields"]}},
            pd.DataFrame,
            ["metadataId", "fields"],
            id="records-metadataId-fields",
        ),
    ],
)
def test_raw_request_records_include_fields(
    dfi: Client, dataset_id: str, document: dict, expected_type: type, include: list[str]  # type: ignore[type-arg]
) -> None:
    """Test raw_request works as intended."""
    document["datasetId"] = dataset_id
    result: pd.DataFrame = dfi.query.raw_request(document)
    assert isinstance(result, expected_type)
    assert set(include).issubset(set(result.columns))


@pytest.mark.parametrize(
    "document,expected_type",
    [({"return": {"type": "records", "include": ["metadataId"]}}, dict)],
)
def test_raw_request_document_set(
    dfi: Client,
    dataset_id: str,
    document: dict,  # type: ignore[type-arg]
    expected_type: type,
) -> None:
    """Test document attribute is set after successful query."""
    document["datasetId"] = dataset_id
    _ = dfi.query.raw_request(document)

    assert isinstance(dfi.query.document, expected_type)
