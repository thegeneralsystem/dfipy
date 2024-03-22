"""Model definition for Count return type."""

import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class GroupBy(str, Enum):
    """Enumerates the valid groupby fields."""

    UNIQUE_IDS = "uniqueId"

    def __str__(self) -> str:
        """Return the value as a string rather than a string of the full enum."""
        return self.value

    def build(self) -> dict[str, dict[str, str]]:
        """Return a GroupBy return model definition for QueryDocument."""
        return {"groupBy": {"type": str(self)}}


class Count:
    """Count return model."""

    __match_args__ = ("groupby",)
    _groupby: GroupBy | None

    def __init__(self, groupby: GroupBy | str | None = None):
        """Initialize to Coutn return model. Optionally specify a groupby field."""
        self._groupby = self._validate_groupby(groupby)

    def __repr__(self) -> str:
        """Class representation."""
        return f"Count(groupby={self._groupby})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"Count(groupby={self._groupby})"

    def _validate_groupby(self, groupby: GroupBy | str | None) -> GroupBy | None:
        """Validate the include list.

        Parameters
        ----------
        include:
            Can be a GroupBy object or a str that can be used to create a GroupBy object or None.
        """
        match groupby:
            case None | GroupBy():
                return groupby
            case str():
                return GroupBy(groupby)
            case _:
                raise ValueError(f"{groupby} is not a valid GroupBy")

    @property
    def groupby(self) -> GroupBy | None:
        """The groupby property."""
        return self._groupby

    def build(self) -> dict:
        """Return a count return model definition for QueryDocument."""
        result: dict[str, str | dict[str, str]] = {"type": "count"}
        if self._groupby:
            result.update(self._groupby.build())
        return result
