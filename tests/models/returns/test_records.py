"""Tests for Records."""

import pytest
from _pytest.python_api import RaisesContext

from dfi.models.returns import IncludeField, Records


@pytest.mark.parametrize(
    "include,expectation",
    [
        ([], pytest.raises(ValueError)),
        ([None], pytest.raises(ValueError)),
        ([1234], pytest.raises(ValueError)),
        ("fields", pytest.raises(ValueError)),
    ],
)
def test_records_error_conditions(include: list[str | int] | None, expectation: RaisesContext[ValueError]) -> None:
    """Test Records validation."""
    with expectation:
        Records(include=include)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "include,expected",
    [
        (None, {"type": "records"}),
        ([IncludeField("fields")], {"type": "records", "include": ["fields"]}),
        ([IncludeField("metadataId")], {"type": "records", "include": ["metadataId"]}),
        (
            [IncludeField("fields"), IncludeField("metadataId")],
            {"type": "records", "include": ["fields", "metadataId"]},
        ),
        pytest.param(
            ["fields"], {"type": "records", "include": ["fields"]}, id="implicit IncludeField conversion ['fields']"
        ),
        pytest.param(
            ["metadataId"],
            {"type": "records", "include": ["metadataId"]},
            id="implicit IncludeField conversion ['metadata']",
        ),
        pytest.param(
            ["fields", "metadataId"],
            {"type": "records", "include": ["fields", "metadataId"]},
            id="implicit IncludeField conversion ['fields', 'metadata']",
        ),
    ],
)
def test_records(include: list[IncludeField | str] | None, expected: dict) -> None:
    """Test Records builds."""
    assert expected == Records(include=include).build()
