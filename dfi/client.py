"""Class composition of all the other classes, to access the wrappers with syntactic sugar."""

from dfi.connect import Connect
from dfi.services.datasets import Datasets
from dfi.services.identities import Identities
from dfi.services.info import Info
from dfi.services.ingest import Ingest
from dfi.services.query import Query
from dfi.services.users import Users


class Client:
    """Collection of GS Platform services."""

    def __init__(
        self,
        api_token: str,
        base_url: str | None = None,
        query_timeout: int | None = 60,
        progress_bar: bool | None = False,
    ) -> None:
        """Create a connection to GS Platform services.

        Parameters
        ----------
        api_token:
            a unique token.
        base_url:
            where the GS Platform is located.
        query_timeout:
            will timeout if no response within this many seconds.
        progress_bar:
            if `True`, will show a progress bar.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)
        ```
        """
        self.conn = Connect(
            api_token=api_token,
            base_url=base_url,
            query_timeout=query_timeout,
            progress_bar=progress_bar,
        )
        self.datasets = Datasets(self.conn)
        self.identities = Identities(self.conn)
        self.info = Info(self.conn)
        self.ingest = Ingest(self.conn)
        self.users = Users(self.conn)
        self.query = Query(self.conn)

    def __repr__(self) -> str:
        """Class representation."""
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""
