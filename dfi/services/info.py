"""
Class with DFI getters, wrappers of the DFI python API for info methods.
Composition of the class Connection.
"""
import logging
from typing import List, Union

import requests

from dfi import __version__ as version
from dfi import validate
from dfi.connect import Connect

_logger = logging.getLogger(__name__)


class Info:
    """
    Class responsible to call the HTTP API and submit queries for information methods.
    ```
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def api_version(self) -> str:
        """
        Returns the version of the Data Flow Index (DFI) API.
        """
        with self.conn.api_get("version", stream=False, params=None) as response:
            response.raise_for_status()
            return response.text

    def dfipy_version(self) -> str:
        """
        Returns the version of the dfipy python library.
        """
        return version

    def product_version(self) -> str:
        """
        Returns the Data Flow Index (DFI) product version.
        """
        with self.conn.api_get("product/version", stream=False, params=None) as response:
            try:
                return response.json()["version"]
            except KeyError as err:
                raise validate.DFIResponseError(
                    "Product version endpoint should return a dictionary with 'version' as key. "
                    f"It returned instead {response.json()}"
                ) from err

    def instances(self) -> List[dict]:
        """
        Returns the list of available instances serviced by the Data Flow Index.

        :returns: List of dictionaries containing the names and descriptions of rhe DFI instances available
            for the given url.
        :raises `DFIResponseError`: if the queried json can not be parsed correctly, or if the resource is not available.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.get.instances()
        ```
        """
        with self.conn.api_get("instances") as response:
            return self._receive_json(response)

    def profile(self) -> dict:
        """
        Returns the details of your profile.

        :returns: a dictionary with the details referring to your user's profile. These are base on the API token you have selected.
        :raises `DFIResponseError`: if the queried json can not be parsed correctly, or if the resource is not available.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.get.profile()
        ```
        """
        with self.conn.api_get("profile") as response:
            return self._receive_json(response)

    @staticmethod
    def _receive_json(response: requests.models.Response) -> Union[List[dict], dict]:
        try:
            return response.json()
        except TypeError as type_err:
            msg = f"Parsing response to json returned: {type_err}"
        except requests.exceptions.HTTPError as http_err:
            msg = f"HTTP error when parsing requests json: {http_err}"
        except requests.exceptions.JSONDecodeError as decode_err:
            msg = f"Failed to parse response to json with error: {decode_err}"
        _logger.error(msg)
        raise validate.DFIResponseError(msg)
