"""
Class with DFI getters, wrappers of the DFI python API for delete methods.
Composition of the class Connection.
"""
from dfi.connect import Connect


class Delete:
    """
    Class responsible to call the HTTP API and delete data from DFI.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param conn: Instance of a Connect.
    :example:
    ```python
    from dfi import Client

    dfi = Client(token, url)
    dfi.delete.truncate(dataset_id)
    ```
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def truncate(self, dataset_id: str) -> None:
        """
        Delete all data in the target DFI instance.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param dataset_id: id of the dataset.
        :return: None.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.delete.truncate(dataset_id)
        ```
        """
        params = {"instance": dataset_id}

        with self.conn.api_post("truncate", params=params, stream=False) as response:
            response.raise_for_status()
