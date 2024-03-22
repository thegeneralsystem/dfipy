"""Validation and error formatting for DFI responses."""

import json
import logging

import requests

from dfi.errors import DFIResponseError

_logger = logging.getLogger(__name__)

SUCCESS_CODES = 2


def response(
    resp: requests.models.Response,
    url: str,
    headers: dict,
    params: dict | None = None,
    payload: dict | list | None = None,
) -> None:
    """Log the response of a request with the given parameters. Raise an error if status code is not 20x.

    Parameters
    ----------
    resp:
        a response object
    url:
        the queried url
    headers:
        request headers
    params:
        request params
    payload:
        request payload

    Raises
    ------
    DFIResponseError
        If there was an error querying the DFI API.
    """
    # prevent from showing the user token to terminal and logs
    headers = headers.copy()
    headers["Authorization"] = "Bearer XXX"

    msg = f"""
STATUS CODE: {resp.status_code}
ERROR: {resp.text}
URL: {url}
HEADERS: {json.dumps(headers, sort_keys=True, indent=4)}
PARAMS: {json.dumps(params, sort_keys=True, indent=4)}
"""
    if payload is not None:
        msg += f"PAYLOAD: {json.dumps(payload, sort_keys=True, indent=4)}"
    else:
        msg += f"PAYLOAD: {json.dumps(None)}"

    if int(resp.status_code // 100) != SUCCESS_CODES:  # any code 2xx is a valid success response code
        _logger.error(msg)
        raise DFIResponseError(msg)

    _logger.debug(msg)
