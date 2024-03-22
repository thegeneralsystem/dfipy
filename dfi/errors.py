"""Enumerated errors for possible DFI errors that may arise.

??? note
    Errors and Warnings prefixed with `DFI` (e.g. `DFI<name>Error`) indicates it 
    originates from within the GS Platform API.
"""


class DFIResponseError(Exception):
    """Raised when an error propagated back from the DFI API."""


class UnreachableError(Exception):
    """Indicates a section of code was reached that should be unreachable."""


class LinearRingError(Exception):
    """Raised when a Polygon is not a linear ring (<4 points)."""


class PolygonNotClosedError(Exception):
    """Raised when a Polygon not closed (first point is identical to last point)."""


class PolygonUndefinedError(Exception):
    """Raised when a Polygon is uninitialized."""


class LongitudeOutOfBoundsError(Exception):
    """Raised when a longitude value is not within (-180.0 < longitude < 180.0)."""


class LatitudeOutOfBoundsError(Exception):
    """Raised when a latitude value is not within (-90.0 < latitude < 90.0)."""


class AltitudeOutOfBoundsError(Exception):
    """Raised when an altitude value is not within (`-1.7976931348623157e308 < altitude < 1.7976931348623157e308`)."""


class BBoxLongitudeMismatchError(Exception):
    """Raised when `min_lon >= max_lon`."""


class BBoxLatitudeMismatchError(Exception):
    """Raised when `min_lat >= max_lat`."""


class BBoxValueError(Exception):
    """Raised when more than 4 values are used to create a BBox."""


class BBoxUndefinedError(Exception):
    """Raised when a BBox is uninitialized."""


class TimeRangeOutOfBoundsError(Exception):
    """Raised when a TimeRange value is not within.

    - datetime form:          (`1970-01-01 00:00:00+00:00 <= datetime <= 2038-01-19 03:14:08+00:00`)
    - unix epoch millis form: (`0 <= datetime <= 2,147,483,647`)
    """


class TimeRangeMismatchError(Exception):
    """Raised when `min_time > max_time`."""


class TimeRangeUndefinedError(Exception):
    """Raised when a TimeRange is uninitialized."""


class TimeZoneUndefinedError(Exception):
    """Raised when a TimeRange is defined without specifying a timezone."""


class FilterFieldNameNotInSchema(Exception):
    """Raised when a Filter Field is given a name that is not in the dataset schema."""


class FilterFieldValueError(Exception):
    """Raised when a Filter Field value is not a valid value for the field type."""


class FilterFieldTypeError(Exception):
    """Raised when a Filter Field value is not a valid value for the field type."""


class FilterFieldOperationValueError(Exception):
    """Raised when a Filter Field operation is not a valid value for the field type."""


class FilterFieldInvalidNullability(Exception):
    """Raised when a Filter Field nullability does not match the schema definition."""


class UnkownMessageReceivedError(Exception):
    """Raised when an unknown Server Side Event message is received."""


class NoFinishMessageReceivedError(Exception):
    """Raised when a stream ends without receving a 'finish' event."""


class EventsMissedError(Exception):
    """Raised when a fewer events are received than were sent."""


class NoEventsRecievedError(Exception):
    """Raised when 0 events received from the DFI API."""


class InvalidQueryDocument(Exception):
    """Raised when a QueryDocument is invalid."""
