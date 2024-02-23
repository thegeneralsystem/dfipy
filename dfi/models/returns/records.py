"""Model definition for Records return type."""

import logging
from enum import Enum

_logger = logging.getLogger(__name__)


class IncludeField(str, Enum):
    """Enumerates the valid types for a extra fields that can be returned with records."""

    FIELDS = "fields"
    METADATA_ID = "metadataId"

    def __str__(self) -> str:
        """Return the value as a string rather than a string of the full enum."""
        return self.value

    def build(self) -> str:
        """Return an IncludeField return model definition for QueryDocument."""
        return str(self)


class Records:
    """Records return model."""

    __match_args__ = ("include",)
    _include: list[IncludeField] | None

    def __init__(self, include: list[IncludeField | str] | None = None):
        """Initialize to base records.  Filter Fields and Metadata are optionally returned."""
        self._include = self._validate_include_fields(include)

    def __repr__(self) -> str:
        """Class representation."""
        return f"Records(include={self.include})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"Records(include={self.include})"

    @property
    def include(self) -> list[IncludeField] | None:
        """The include property."""
        return self._include

    def _validate_include_fields(self, include: list[IncludeField | str] | None) -> list[IncludeField] | None:
        match include:
            case None:
                return None
            case list() if len(include) > 0:
                include_fields = []
                for field in include:
                    match field:
                        case IncludeField():
                            include_fields.append(field)
                        case str():
                            include_fields.append(IncludeField(field))
                        case _:
                            raise ValueError(f"{field} is not a valid IncludeField")
                return include_fields
            case _:
                raise ValueError(f"{include} is not a valid list[IncludeField]")

    def build(self) -> dict[str, str | list[str]]:
        """Return a records return model definition for QueryDocument."""
        result: dict[str, str | list[str]] = {"type": "records"}
        if self.include:
            result.update({"include": [field.build() for field in self.include]})
        return result
