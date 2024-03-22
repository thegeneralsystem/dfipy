"""Tests for Count."""

import pytest
from _pytest.python_api import RaisesContext

from dfi.models.returns import Count, GroupBy


@pytest.mark.parametrize(
    "groupby,expectation",
    [
        ("altitude", pytest.raises(ValueError)),
        (1234, pytest.raises(ValueError)),
    ],
)
def test_count_error_conditions(groupby: str, expectation: RaisesContext[ValueError]) -> None:
    """Test Count validation."""
    with expectation:
        Count(groupby=groupby)


@pytest.mark.parametrize(
    "groupby,expected",
    [
        (None, {"type": "count"}),
        (GroupBy("uniqueId"), {"type": "count", "groupBy": {"type": "uniqueId"}}),
        ("uniqueId", {"type": "count", "groupBy": {"type": "uniqueId"}}),
    ],
)
def test_count(groupby: GroupBy | str | None, expected: dict) -> None:
    """Test Count builds."""
    assert expected == Count(groupby=groupby).build()
