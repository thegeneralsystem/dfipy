"""
Module with private validator methods used across classes.

Some will be improved and delegated to the DFI API.

:example:
```python
from dfi import validate

validate.df_records(df_records)
```

"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
import requests

from dfi import models

_logger = logging.getLogger(__name__)


class DFIDataFrameColumnsNameError(Exception):
    """Raised when the column names of a dataframe are not as expected"""


class DFIDataCSVConversionError(Exception):
    """Raised when the user tries to ingest into DFI a csv that is wrongly formatted"""


class DFIDataJSONConversionError(Exception):
    """Raised when the user tries to ingest into DFI a json that is wrongly formatted"""


class DFIInputDataError(Exception):
    """Raised when the user tries to ingest into DFI a piece of data wrongly formatted"""


class DFIInputValueError(Exception):
    """Raised when the user passes a wrong input value to the DFI query"""


class DFIInputValueOutOfBoundError(Exception):
    """Raised when the user passes a wrong input value to the DFI query"""


class DFIResponseError(Exception):
    """Raised when an error propagated back from the HTTP API"""


class DFIPolygonNameError(Exception):
    """Raised when the polygon name passed by the user does not conform to a non-empty string"""


class DFIResponseWarning(Warning):
    """Raised when some exceptional case is propagated back from the HTTP API"""


def bounding_box(list_bbox: Optional[List[float]]) -> None:
    """
    Check input list of coordinates correspond to a bounding box, with lon, lat within the range.

    :param list_bbox: a bbox
    :returns: `None`
    :raises `DFIInputValueError`: If `polygon` is ill-formed.
    :raises `DFIInputValueOutOfBoundError`: If not -180.0 < longitude <= 180.0 or not -90 < latitude <= 90.0.
    """
    if list_bbox is None:
        return
    if len(list_bbox) != 4:
        raise DFIInputValueError(f"Input bounding box parameters must be a list of 4 floats. User passed {list_bbox}")
    for value in list_bbox:
        if not isinstance(value, float):
            raise DFIInputValueError(f"Input value {value} of type {type(value)} must be a float.")

    min_lng, min_lat, max_lng, max_lat = list_bbox

    if not -180 < min_lng <= 180:
        raise DFIInputValueOutOfBoundError(f"Input min longitude {min_lng} is out of range.")
    if not -180 < max_lng <= 180:
        raise DFIInputValueOutOfBoundError(f"Input max longitude {max_lng} is out of range.")
    if not -90 < min_lat < 90:
        raise DFIInputValueOutOfBoundError(f"Input min latitude {min_lat} is out of range.")
    if not -90 < max_lat < 90:
        raise DFIInputValueOutOfBoundError(f"Input max latitude {max_lat} is out of range.")
    if not min_lng < max_lng:
        raise DFIInputValueOutOfBoundError(
            f"Input min longitude {min_lng} is greater than input max longitude {max_lng}."
        )
    if not min_lat < max_lat:
        raise DFIInputValueOutOfBoundError(
            f"Input min latitude {min_lat} is greater than input max latitude {max_lat}."
        )


def data(list_data: List[dict]) -> None:
    """
    Check that the input is a list of dict with correct keys.

    :param list_data: a list of dictionaries with keys "coordinate", "time", "id", "payload".
    :returns: `None`
    :raises `DFIInputDataError`: if the input dictionaries do not have the correct keys.
    :raises `DFIInputValueOutOfBoundError`: if the input coordinates are out of bound.

    """
    expected_keys = {"coordinate", "time", "id", "payload"}
    for dict_data in list_data:
        if not expected_keys.issubset(set(dict_data.keys())):
            raise DFIInputDataError(f"Keys expected {expected_keys}. Found instead {set(dict_data.keys())}")
        if not isinstance(dict_data["coordinate"], (list, tuple)):
            raise DFIInputDataError(f"Coordinates passed are {dict_data['coordinate']}. Expecting a tuple or a list.")
        if len(dict_data["coordinate"]) != 2:
            raise DFIInputDataError(
                f"Coordinates passed are {dict_data['coordinate']}. Expecting a tuple or a list with two elements."
            )
        lng, lat = dict_data["coordinate"]
        if not -180 < lng <= 180:
            raise DFIInputValueOutOfBoundError(f"Input max longitude {lng} is out of range.")
        if not -90 < lat < 90:
            raise DFIInputValueOutOfBoundError(f"Input min latitude {lat} is out of range.")


def df_hexes(df_h3: pd.DataFrame) -> None:
    """
    Check the column names are correct.

    :param df_h3: A dataframe with a `"hex_id"` column.
    :returns: `None`
    :raises `DFIDataFrameColumnsNameError`: If a column name is not in
        `["entity_id", "latitude", "longitude", "timestamp", "hex_id"]`
    """
    for col_name in ["entity_id", "latitude", "longitude", "timestamp", "hex_id"]:
        if col_name not in df_h3.columns:
            raise DFIDataFrameColumnsNameError(f"Column name {col_name} expected in df_records but not found.")


def df_hexes_heatmap(df_h3: pd.DataFrame) -> None:
    """
    Check the column names are correct.

    :param df_h3: A dataframe with a `"hex_id"` column.
    :returns: `None`
    :raises `DFIDataFrameColumnsNameError`: If a column name is not in
        `["entity_id", "latitude", "longitude", "timestamp", "hex_id", "period_start", "period end"]`
    """
    for col_name in ["entity_id", "latitude", "longitude", "timestamp", "hex_id", "period_start", "period end"]:
        if col_name not in df_h3.columns:
            raise DFIDataFrameColumnsNameError(f"Column name {col_name} expected in df_records but not found.")


def df_records(df_rec: pd.DataFrame) -> None:
    """
    Check the column names are correct.

    :param h3_res: A dataframe of records
    :returns `None`:
    :raises `DFIDataFrameColumnsNameError`: If a column name is not in
        `["entity_id", "latitude", "longitude", "timestamp"]`
    """
    for col_name in ["entity_id", "latitude", "longitude", "timestamp"]:
        if col_name not in df_rec.columns:
            raise DFIDataFrameColumnsNameError(f"Column name {col_name} expected in df_records but not found.")


def entities(input_entities: Optional[List[str]]) -> None:
    """
    Validate a given list of entities is a list of strings.

    :param `input_entities`: a list of entity ids
    :returns: `None`
    :raises `DFIInputValueError`: If `input_entities` is not a list of string or is empty or has duplicates.
    """
    if input_entities is None:
        return
    if not isinstance(input_entities, list):
        raise DFIInputValueError(f"Entities must be a list of strings. Received {input_entities}")
    if len(input_entities) == 0:
        raise DFIInputValueError("Entities must be a list of strings. Received an empty list")
    if len(set(input_entities)) < len(input_entities):
        duplicates_found = {x for x in input_entities if input_entities.count(x) > 1}
        raise DFIInputValueError(f"Entities list must not contain duplicates. Duplicates found {duplicates_found}")


def h3_resolution(h3_res: int) -> None:
    """
    check the input is within an Acceptable range.

    :param `h3_res`: An H3 resolution
    :returns: `None`
    :raises `DFIInputValueOutOfBoundError`:  If not 1<= h3_res <= 15
    """
    if (h3_res < 1) or (h3_res > 15):
        raise DFIInputValueOutOfBoundError(
            f"Resolution is incorrect. It must be between 1 and 15. User passed {h3_res}"
        )


def list_polygons_response(vert: Optional[models.Polygon], resp: requests.models.Response) -> None:
    """
    :param vert:
    :returns: `None`
    :raises `DFIResponseError`: If there was an error querying the DFI API.
    """
    if vert is None:
        msg = f"Polygon list can not be retrieved from the json response: {resp.json()}"
        _logger.error(msg)
        raise DFIResponseError(msg)


def polygon(poly: Optional[models.Polygon]) -> None:
    """
    Check input list of coordinates correspond to a list of vertices, or a bounding box.

    :param poly: A list of vertices or bbox.
    :returns `None`:
    :raises `DFIInputValueError`: If `polygon` is ill-formed.
    """
    if poly is None:
        return
    if not isinstance(poly, (list, tuple)):
        raise DFIInputValueError(f"Polygon {poly} must be of type list or tuple.")
    if len(poly) == 0:
        raise DFIInputValueError(f"Given polygon {poly} is empty.")
    if not isinstance(poly[0], (list, tuple, float)):
        raise DFIInputValueError(f"Polygon {poly} must be a list of tuples or floats.")
    if isinstance(poly[0], float):
        bounding_box(poly)
    if isinstance(poly[0], (list, tuple)):
        vertices(poly)


def polygon_name(poly_name: str) -> None:
    """
    Validate input polygon name is a non empty string.

    :param poly_name: a candidate name for a polygon.

    :returns: `None`

    :raises `DFIPolygonNameError`: if the polygon name passed by the user is not valid.
    """
    if not isinstance(poly_name, str):
        raise DFIPolygonNameError(
            f"The polygon name is expected to be a non-empty string. "
            f"User passed {poly_name} of type {type(poly_name)}"
        )
    if len(poly_name) == 0:
        raise DFIPolygonNameError("The polygon name is expected to be non-empty")
    if " " in poly_name:
        raise DFIPolygonNameError(f"The polygon name is expected to contain no spaces. User passed {poly_name}")


def response(
    resp: requests.models.Response,
    url: str,
    headers: dict,
    params: dict,
    payload: Optional[dict] = None,
) -> None:
    """
    Log the response of a request with the given parameters. Raise an error if status code is not 20x.

    :param resp: a response object
    :param url: the queried url
    :param headers: request headers
    :param params: request params
    :param payload: request payload

    :returns: `None`

    :raises `DFIResponseError`: If there was an error querying the DFI API.
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

    if int(resp.status_code / 10) != 20:
        _logger.error(msg)
        raise DFIResponseError(msg)

    _logger.debug(msg)


def time_interval(time_interv: Optional[models.TimeInterval] = None) -> None:
    """
    Validate input datetimes are both given and compatible.

    :param time_interv: - a tuple of start time and end time bounds e.g. `(start_time, end_time)`
    :returns: `None`
    :raises `DFIInputValueError`: If `time_interv` is ill-formed.
    """
    if time_interv is None:
        return
    if len(time_interv) != 2:
        msg = f"Time interval is not an interval with two dates. User passed {time_interv}"
        raise DFIInputValueError(msg)

    start_time, end_time = time_interv

    if start_time is None and end_time is None:
        return
    if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
        msg = (
            "start_time and end_time must be both initialised or both None. "
            f"User passed start_time={start_time}, end_time={end_time}"
        )
        raise DFIInputValueError(msg)

    if not isinstance(start_time, datetime):
        msg = f"Start time should be of type datetime. User passed {start_time}"
        raise DFIInputValueError(msg)

    if not isinstance(end_time, datetime):
        msg = f"End time should be of type datetime. User passed {end_time}"
        raise DFIInputValueError(msg)

    if not start_time < end_time:
        msg = f"Start time {start_time} happened after than end time {end_time}."
        raise DFIInputValueError(msg)


def url_s3(url_object: Union[str, List[str]]) -> None:
    """
    Validate input S3 URL, which can be a string or a list of strings.

    :param url_object: - a string with an S3 URL or a list or S3 UR:.
    :returns: `None`
    :raises `DFIInputValueError`: if the types are not as expected.
    """
    msg = f"Given URL can be either a list of strings or a list. User passed {url_object}"
    if not isinstance(url_object, (str, list)):
        raise DFIInputValueError(msg)
    if isinstance(url_object, list):
        for url_item in url_object:
            if not isinstance(url_item, str):
                raise DFIInputValueError(msg)


def vertices(input_vertices: Optional[List[List[float]]]) -> None:
    """
    Check input list of vertices correspond to a polygon.
    It does not check if the polygon is simple.

    :param input_vertices: a list of polygon vertices
    :returns: `None`
    :raises `DFIInputValueError`: If `input_vertices` is ill-formed.
    """
    if input_vertices is None:
        return
    if len(input_vertices) < 3:
        raise DFIInputValueError(f"A polygon can not have less than 3 vertices. User passed {input_vertices}.")
    for vertex in input_vertices:
        if not len(vertex) == 2:
            raise DFIInputValueError(f"Length of each vertex must be 2. User passed {vertex}")
        if not isinstance(vertex[0], float) or not isinstance(vertex[1], float):
            raise DFIInputValueError(
                f"Coordinates must be of type float."
                f" User passed {vertex} of types ({type(vertex[0])}, {type(vertex[1])})"
            )
        lng, lat = vertex
        if not -180 < lng <= 180:
            raise DFIInputValueOutOfBoundError(f"Input longitude {lng} is out of range.")
        if not -90 < lat < 90:
            raise DFIInputValueOutOfBoundError(f"Input  latitude {lat} is out of range.")

    if not input_vertices[0] == input_vertices[-1]:
        raise DFIInputValueError("First and last vertices are expected to be identical points.")


def vertices_response(vert: Optional[models.Polygon], resp: requests.models.Response) -> None:
    """
    :param vert:
    :returns: `None`
    :raises `DFIResponseError`: If there was an error querying the DFI API.
    """
    if vert is None:
        msg = f"Polygon vertices can not be retrieved from the json response: {resp.json()}"
        _logger.error(msg)
        raise DFIResponseError(msg)
