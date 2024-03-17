"""Class composition of all the other classes, to access the wrappers with syntactic sugar."""

from dfi.connect import Connect
from dfi.services.datasets import Datasets
from dfi.services.delete import Delete
from dfi.services.get import Get
from dfi.services.identities import Identities
from dfi.services.info import Info
from dfi.services.ingest import Ingest
from dfi.services.query import Query
from dfi.services.sql import Sql
from dfi.services.users import Users


class Client:
    """Client class gathering all the classes and method in a single one. Facade of dfi.Connect.

    See documentation of dfi.Connect for its input values.

    :example:
    ```python
    from dfi import Client

    dfi = Client(token, url)
    ```
    """

    def __init__(
        self,
        api_token: str,
        base_url: str | None = None,
        query_timeout: int | None = 60,
        progress_bar: bool | None = False,
    ) -> None:
        """Group services under one class."""
        self.conn = Connect(
            api_token=api_token,
            base_url=base_url,
            query_timeout=query_timeout,
            progress_bar=progress_bar,
        )
        self.datasets = Datasets(self.conn)
        self.delete = Delete(self.conn)
        self.get = Get(self.conn)
        self.identities = Identities(self.conn)
        self.info = Info(self.conn)
        self.ingest = Ingest(self.conn)
        self.users = Users(self.conn)
        self.query = Query(self.conn)
        self.sql = Sql(self.query)

    def __repr__(self) -> str:
        """Class representation."""
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""
