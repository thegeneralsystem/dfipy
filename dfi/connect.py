"""Class to connect to the DFI server.
"""

import logging

import requests

from dfi import validate

_logger = logging.getLogger(__name__)


class Connect:
    """Class instantiating the connectors to the DFI API.

    :param api_token: token provided by generalsystem.com to access the running DFI environments.
    :param base_url: Base url where the service is located
    :param query_timeout: Time after an unresponsive query will be dropped.
    :param progress_bar: Visualise a progress bar if True (slows down the execution, typically used for demos and tests).

    :example:
    ````python
    connection = dfi.Connect("<token>", "<base_url>")
    ````
    """

    def __init__(
        self,
        api_token: str,
        base_url: str | None = None,
        query_timeout: int | None = 60,
        progress_bar: bool | None = False,
    ) -> None:
        self.api_token = api_token
        self.base_url = base_url
        self.query_timeout = query_timeout
        self.streaming_headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "text/event-stream",
        }
        self.synchronous_headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.progress_bar = progress_bar

    # The representation will expose the secret token
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(api_token=<***>, base_url={self.base_url}, query_timeout={self.query_timeout}, progress_bar={self.progress_bar})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(api_token=<***>, base_url={self.base_url}, query_timeout={self.query_timeout}, progress_bar={self.progress_bar})"

    # get and post API wrappers
    def api_get(
        self,
        endpoint: str,
        stream: bool = True,
        params: dict | None = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.get method"""
        headers = self.streaming_headers if stream else self.synchronous_headers
        url = f"{self.base_url}/{endpoint}"
        _logger.debug(dict(url=url, headers=headers, stream=stream, params=params, timeout=self.query_timeout))
        response = requests.get(
            url,
            headers=headers,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )

        validate.response(response, url, headers, params)
        return response

    def api_post(
        self,
        endpoint: str,
        stream: bool = True,
        params: dict | None = None,
        payload: dict | list | None = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.post method"""
        headers = self.streaming_headers if stream else self.synchronous_headers
        url = f"{self.base_url}/{endpoint}"

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params, payload)
        return response

    def api_put(
        self,
        endpoint: str,
        stream: bool = True,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.put method
        :endpoint: The endpoint of the URL.  Will be added as a suffix to the base_url.
        :stream: Whether to use streaming headers or synchronous headers.
        :params: Dictionary, list of tuples or bytes to send in the query string for the request.
        :data: Dictionary, list of tuples, bytes, or file-like object to send in the body of the request
        :json: A JSON serializable Python object to send in the body of the request.  Will set the
            "Content-Type: application/json" in the header.
        """
        headers = self.streaming_headers if stream else self.synchronous_headers
        url = f"{self.base_url}/{endpoint}"

        response = requests.put(
            url,
            headers=headers,
            json=json,
            data=data,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params, json)
        return response

    def api_delete(
        self,
        endpoint: str,
        stream: bool = True,
        params: dict | None = None,
        payload: dict | None = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.delete method"""
        headers = self.streaming_headers if stream else self.synchronous_headers

        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(
            url,
            headers=headers,
            json=payload,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response

    def api_patch(
        self,
        endpoint: str,
        stream: bool = True,
        params: dict | None = None,
        payload: dict | None = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.patch method"""
        headers = self.streaming_headers if stream else self.synchronous_headers
        url = f"{self.base_url}/{endpoint}"

        response = requests.patch(
            url,
            headers=headers,
            json=payload,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params, payload)
        return response
