"""Unit tests for TimeRange."""

import logging
from datetime import datetime, timezone

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import TimeRangeMismatchError, TimeRangeUndefinedError, TimeZoneUndefinedError
from dfi.models.filters import TimeRange

_logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "expectation",
    [(pytest.raises(TimeRangeUndefinedError))],
)
def test_timerange_undefined_error_condition(expectation: RaisesContext[TimeRangeUndefinedError]) -> None:
    """Test PolygonUndefinedError is raised."""
    with expectation:
        TimeRange().validate()


@pytest.mark.parametrize(
    "min_time,max_time,expectation",
    [
        (datetime(2020, 1, 1, 0, 0, 0), datetime(2020, 1, 1, 0, 0, 1), pytest.raises(TimeZoneUndefinedError)),
        (
            datetime(2020, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            pytest.raises(TimeRangeMismatchError),
        ),
    ],
)
def test_timerange_from_datetimes_error_conditions(
    min_time: datetime, max_time: datetime, expectation: RaisesContext[TimeRangeMismatchError | TimeZoneUndefinedError]
) -> None:
    """Test TimeRange errors are raised."""
    with expectation:
        TimeRange().from_datetimes(min_time, max_time).build()


@pytest.mark.parametrize(
    "min_time,max_time,expected",
    [
        (None, None, {"minTime": None, "maxTime": None}),
        (
            None,
            datetime(2020, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            {"minTime": None, "maxTime": "2020-01-01T00:00:01+00:00"},
        ),
        (
            datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            None,
            {"minTime": "2020-01-01T00:00:00+00:00", "maxTime": None},
        ),
        (
            datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2020, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            {"minTime": "2020-01-01T00:00:00+00:00", "maxTime": "2020-01-01T00:00:01+00:00"},
        ),
    ],
)
def test_timerange_from_datetimes(min_time: datetime, max_time: datetime, expected: datetime) -> None:
    """Test TimeRange can be built from datetimes."""
    assert expected == TimeRange().from_datetimes(min_time, max_time).build()


@pytest.mark.parametrize(
    "min_time,max_time,expectation",
    [
        ("2020-01-01T00:00:00", "2020-01-01T00:00:01", pytest.raises(TimeZoneUndefinedError)),
        ("2020-01-01T00:00:01+00:00", "2020-01-01T00:00:00+00:00", pytest.raises(TimeRangeMismatchError)),
    ],
)
def test_timerange_from_strings_error_conditions(
    min_time: str, max_time: str, expectation: RaisesContext[TimeRangeMismatchError | TimeZoneUndefinedError]
) -> None:
    """Test TimeRange errors are raised."""
    with expectation:
        TimeRange().from_strings(min_time, max_time).build()


@pytest.mark.parametrize(
    "min_time,max_time,expected",
    [
        (None, None, {"minTime": None, "maxTime": None}),
        (None, "2020-01-01T00:00:01+01:00", {"minTime": None, "maxTime": "2020-01-01T00:00:01+01:00"}),
        ("2020-01-01T00:00:00+01:00", None, {"minTime": "2020-01-01T00:00:00+01:00", "maxTime": None}),
        (
            "2020-01-01T00:00:00+01:00",
            "2020-01-01T00:00:01+01:00",
            {"minTime": "2020-01-01T00:00:00+01:00", "maxTime": "2020-01-01T00:00:01+01:00"},
        ),
        (
            "2020-01-01T00:00:00+01:00",
            "2020-01-01T00:00:01+01:00",
            {"minTime": "2020-01-01T00:00:00+01:00", "maxTime": "2020-01-01T00:00:01+01:00"},
        ),
    ],
)
def test_timerange_from_strings(min_time: str, max_time: str, expected: datetime) -> None:
    """Test TimeRange can be built from ISO 8601 strings."""
    assert expected == TimeRange().from_strings(min_time, max_time).build()


@pytest.mark.parametrize(
    "min_time,max_time,tz,expectation",
    [
        (
            1577836801000,
            1577836800000,
            timezone.utc,
            pytest.raises(TimeRangeMismatchError),
        ),
    ],
)
def test_timerange_from_millis_error_conditions(
    min_time: int, max_time: int, tz: timezone, expectation: RaisesContext[TimeRangeMismatchError]
) -> None:
    """Test TimeRange errors are raised."""
    with expectation:
        TimeRange().from_millis(min_time, max_time, tz).build()


@pytest.mark.parametrize(
    "min_time,max_time,tz,expected",
    [
        (None, None, timezone.utc, {"minTime": None, "maxTime": None}),
        (None, 1577836801000, timezone.utc, {"minTime": None, "maxTime": "2020-01-01T00:00:01+00:00"}),
        (1577836800000, None, timezone.utc, {"minTime": "2020-01-01T00:00:00+00:00", "maxTime": None}),
        (
            1577836800000,
            1577836801000,
            timezone.utc,
            {"minTime": "2020-01-01T00:00:00+00:00", "maxTime": "2020-01-01T00:00:01+00:00"},
        ),
        (
            1577836800001,
            1577836801001,
            timezone.utc,
            {"minTime": "2020-01-01T00:00:00.001000+00:00", "maxTime": "2020-01-01T00:00:01.001000+00:00"},
        ),
    ],
)
def test_timerange_from_millis(min_time: int, max_time: int, tz: timezone, expected: datetime) -> None:
    """Test TimeRange can be built from integers representing milliseconds from Unix epoch."""
    assert expected == TimeRange().from_millis(min_time, max_time, tz).build()
