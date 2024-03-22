"""TimeRange filter describes how to filter on time."""

from datetime import datetime, timezone

from typing_extensions import Self

from dfi.errors import TimeRangeMismatchError, TimeRangeUndefinedError, TimeZoneUndefinedError

# DATETIME_MIN = 0
# DATETIME_MAX = 2_147_483_647


class TimeRange:
    """A TimeRange is a a way to bound time.

    If a bound (`min_time` or `max_time`) is None, then time in that direction is unbound
    i.e. bounds will "expand" to the first or last record in dataset based on timestamp.
    """

    _min_time: datetime | None
    _max_time: datetime | None

    def __repr__(self) -> str:
        """Class representation."""
        time_range = self.build()
        min_time = time_range["minTime"]
        max_time = time_range["maxTime"]
        return f"TimeRange({min_time}, {max_time})"

    def __str__(self) -> str:
        """Class string formatting."""
        time_range = self.build()
        min_time = time_range["minTime"]
        max_time = time_range["maxTime"]
        return f"TimeRange({min_time}, {max_time})"

    @property
    def min_time(self) -> datetime | None:
        """The min_time property."""
        return self._min_time

    @property
    def max_time(self) -> datetime | None:
        """The max_time property."""
        return self._max_time

    def from_datetimes(self, min_time: datetime | None = None, max_time: datetime | None = None) -> Self:
        """Create a TimeRange from `datetime` objects.

        Parameters
        ----------
        min_time:
            Lower time bound.
        max_time:
            Upper time bound.

        Returns
        -------
        TimeRange

        Raises
        ------
        TimeRangeUndefinedError
        TimeRangeMismatchError
        TypeError

        Examples
        --------
        ### TimeRange From `datetime`s
        ```python
        from datetime import datetime, timezone

        min_time = datetime(
            2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc
        )
        min_time = datetime(
            2020, 1, 1, 0, 0, 1, tzinfo=timezone.utc
        )

        TimeRange().from_datetimes(min_time, max_time)
        ```
        ```python
        TimeRange(2020-01-01T00:00:00, 2020-01-01T00:00:01)
        ```
        """
        match min_time:
            case datetime():
                self._min_time = min_time
            case None:
                self._min_time = None
            case _:
                raise TypeError(f"min_time should be of type str | None, found '{type(min_time)}'")

        match max_time:
            case datetime():
                self._max_time = max_time
            case None:
                self._max_time = None
            case _:
                raise TypeError(f"max_time should be of type str | None, found '{type(max_time)}'")

        return self.validate()

    def from_strings(self, min_time: str | None = None, max_time: str | None = None) -> Self:
        """Create a TimeRange from [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) strings.

        Parameters
        ----------
        min_time:
            Lower time bound.
        max_time:
            Upper time bound.

        Returns
        -------
        TimeRange

        Raises
        ------
        TimeRangeUndefinedError
        TimeRangeMismatchError
        TypeError

        Examples
        --------
        ??? attention

            Creating datetimes from strings in Zulu time (e.g. `"2024-02-06T10:41:54Z"`) are not supported in Python 3.10


        ### TimeRange From Strings
        ```python
        TimeRange().from_strings(
            "2020-01-01T00:00:00.001000+00:00",
            "2020-01-01T00:00:01.001000+00:00",
        )
        ```
        ```python
        TimeRange(2020-01-01T00:00:00+01:00, 2020-01-01T00:00:01+01:00)
        ```
        """
        match min_time:
            case str():
                self._min_time = datetime.fromisoformat(min_time)
            case None:
                self._min_time = None
            case _:
                raise TypeError(f"min_time should be of type str | None, found '{type(min_time)}'")

        match max_time:
            case str():
                self._max_time = datetime.fromisoformat(max_time)
            case None:
                self._max_time = None
            case _:
                raise TypeError(f"max_time should be of type str | None, found '{type(max_time)}'")

        return self.validate()

    def from_millis(
        self, min_time: int | None = None, max_time: int | None = None, tz: timezone = timezone.utc
    ) -> Self:
        """Create a TimeRange from integers representing Unix Epoch in milliseconds.

        Parameters
        ----------
        min_time:
            Lower time bound.
        max_time:
            Upper time bound.
        tz:
            The timezone for the datetime.  Defaults to UTC.

        Returns
        -------
        TimeRange

        Raises
        ------
        TimeRangeUndefinedError
        TimeRangeMismatchError
        TypeError

        Examples
        --------
        ### TimeRange From Milliseconds Since Unix Epoch
        ```python
        TimeRange().from_millis(1577836800000, 1577836801000)
        ```
        ```python
        TimeRange(2020-01-01T00:00:00.001000+00:00, 2020-01-01T00:00:01.001000+00:00)
        ```
        """
        match min_time:
            case int():
                self._min_time = datetime.fromtimestamp(min_time / 1000.0, tz)
            case None:
                self._min_time = None
            case _:
                raise TypeError(f"min_time should be of type str | None, found '{type(min_time)}'")

        match max_time:
            case int():
                self._max_time = datetime.fromtimestamp(max_time / 1000.0, tz)
            case None:
                self._max_time = None
            case _:
                raise TypeError(f"max_time should be of type str | None, found '{type(max_time)}'")

        return self.validate()

    def validate(self) -> Self:
        """Validate the TimeRange bounds.

        Raises
        ------
        TimeRangeUndefinedError
        TimeRangeMismatchError
        """
        if not (hasattr(self, "_min_time") or hasattr(self, "_max_time")):
            raise TimeRangeUndefinedError

        if (self._min_time is not None) and (self._max_time is not None):
            if self._min_time > self._max_time:
                raise TimeRangeMismatchError

            if (self._min_time.tzinfo is None) or (self._max_time.tzinfo is None):
                raise TimeZoneUndefinedError

            # TODO ask @matt what the limits (if any) are
            # if self._min_time < 0:
            #     raise TimeRangeOutOfBoundsError(
            #         f"min_time value '{self._min_time}' not within ({DATETIME_MIN}, {DATETIME_MAX})"
            #     )
            # if self._max_time > 0:
            #     raise TimeRangeOutOfBoundsError(
            #         f"max_time value '{self._max_time}' not within ({DATETIME_MIN}, {DATETIME_MAX})"
            #     )

        return self

    def build(self) -> dict[str, str | None]:
        """Validate the TimeRange is defined and format the TimeRange for use in Query Document."""
        self.validate()
        min_time = None if self._min_time is None else self._min_time.isoformat()
        max_time = None if self._max_time is None else self._max_time.isoformat()

        return {"maxTime": max_time, "minTime": min_time}
