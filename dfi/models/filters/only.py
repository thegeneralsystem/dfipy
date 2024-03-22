"""Only filter model definition."""

from enum import Enum


class Only(str, Enum):
    """Enumerates the valid types for a Only filter.."""

    NEWEST = "newest"
    OLDEST = "oldest"

    def __str__(self) -> str:
        """Return the value as a string rather than a string of the full enum."""
        return self.value

    def build(self) -> str:
        """Return an Only filter definition for QueryDocument."""
        return str(self)
