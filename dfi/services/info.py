"""Class for handling version information."""

from dfi import __version__ as version
from dfi.connect import Connect


class Info:
    """Class for handling version information."""

    def __init__(self, conn: Connect) -> None:
        """Handle queries about versions."""
        self.conn = conn

    def __repr__(self) -> str:
        """Class representation."""
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"{self.__class__.__name__}(conn={self.conn!r})"

    def version(self) -> str:
        """Return the version of the dfipy python library."""
        return version

    def api_version(self) -> str:
        """Return the version of the Data Flow Index (DFI) API.

        ??? info "Endpoint"
            `GET version`
        """
        with self.conn.api_get("version", stream=False, params=None) as response:
            response.raise_for_status()
            return response.text

    def product_version(self) -> str:
        """Return the Data Flow Index (DFI) product version.

        ??? info "Endpoint"
            `GET product/version`
        """
        with self.conn.api_get("product/version", stream=False, params=None) as response:
            response.raise_for_status()
            return response.text
