"""Tests for GroupBy."""

import pytest
from _pytest.python_api import RaisesContext

from dfi.models.returns import GroupBy


@pytest.mark.parametrize(
    "field,expectation",
    [
        ("altitude", pytest.raises(ValueError)),
        (1234, pytest.raises(ValueError)),
    ],
)
def test_groupby_error_conditions(field: str | int, expectation: RaisesContext[ValueError]) -> None:
    """Test GroupBy validation."""
    with expectation:
        GroupBy(field)


@pytest.mark.parametrize(
    "field,expected",
    [
        ("uniqueId", {"groupBy": {"type": "uniqueId"}}),
    ],
)
def test_groupby(field: str, expected: dict) -> None:
    """Test GroupBy builds."""
    assert expected == GroupBy(field).build()
