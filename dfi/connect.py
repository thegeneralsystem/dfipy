"""
Class to connect to the DFI server.
"""
import logging
from typing import Optional, Union

import requests

from dfi import validate

_logger = logging.getLogger(__name__)


class Connect:
    """
    Class instantiating the connectors to the DFI API.

    :param api_token: token provided by generalsystem.com to access the running DFI environments.
    :param dataset_id: the ID of the dataset to point to.
    :param base_url: Base url where the service is located
    :param query_timeout: Time after an unresponsive query will be dropped.
    :param progress_bar: Visualise a progress bar if True (slows down the execution, typically used for demos and tests).

    :example:
    ````python
    dfi_conn = dfi.Connect(api_token, dataset_id, base_url)

    dfi_conn.streaming_headers
    ````
    """

    def __init__(
        self,
        api_token: str,
        base_url: Optional[str] = None,
        dataset_id: Optional[str] = None,
        query_timeout: Optional[int] = 60,
        progress_bar: Optional[bool] = False,
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
        self.dataset_id = dataset_id
        self.progress_bar = progress_bar

    # The representation will expose the secret token
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.base_url}"

    def __str__(self) -> str:
        return f"""
                API connection instance
                base_url={self.base_url},
                dataset_id={self.dataset_id}
                """

    # get and post API wrappers
    def api_get(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
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
        params: Optional[dict] = None,
        payload: Optional[Union[dict, list]] = None,
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
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> requests.models.Response:
        """Helper wrapping requests.put method"""
        headers = self.streaming_headers if stream else self.synchronous_headers
        url = f"{self.base_url}/{endpoint}"

        response = requests.put(
            url,
            headers=headers,
            data=data,
            stream=stream,
            params=params,
            timeout=self.query_timeout,
        )
        validate.response(response, url, headers, params)
        return response

    def api_delete(
        self,
        endpoint: str,
        stream: bool = True,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
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
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
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
