"""
Class with DFI getters, wrappers of the DFI python API.
Composition of the class Connection.
"""
import json
import logging
from datetime import datetime
from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import requests
import sseclient
from tqdm import tqdm

from dfi import models, validate
from dfi.connect import Connect
from dfi.query_document import QueryDocument

_logger = logging.getLogger(__name__)

NUM_ATTEMPTS = 3


class Get:
    """
    Class responsible to call the HTTP API and submit queries to get data from DFI.

    It can be accessed via the a dfi.Client class instance or it must be instantiated
    with a dfi.Connect instance as argument.

    :param conn: Instance of a Connect.
    :example:
    ```python
    from dfi import Client

    dfi = Client(token, url)

    dataset_id = "1234"
    dfi.get.entities(dataset_id, time_interval=[start_time, end_time])
    ```
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def records_count(
        self,
        dataset_id: str,
        entities: Optional[List[str]] = None,
        polygon: Optional[models.Polygon] = None,
        time_interval: Optional[models.TimeInterval] = None,
        filter_fields: Optional[dict] = None,
    ) -> int:
        """
        Queries for the number of records within the bounds.

        If all the variables are None it returns the total number of records in the
        database. Start_time and end_time must be both valid datetime, with
        start_time < end_time or both None.

        :param dataset_id: the dataset to be queried.
        :param polyogn: List of vertices `[[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon1, lat1]]` or a list of four
            floats representing the bounding box extremes as `[lon_min, lat_min, lon_max, lat_max]`.
            Non-valid input will raise an error.
        :param time_interval: Tuple with the lower bound and the upper bound time constraints.
        :param filter_fields: Optional[dict]: {field_name: {FilterOperation: value}}
        :returns: The number of records stored in the DFI engine.
        :raises `DFIInputValueError`: If `time_interval` or `polygon` are ill-formed.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dataset_id = "1234"
        start_time = datetime.strptime("2022-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime("2022-01-01T08:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        entities = ["299eb59a-e47e-48c0-9ad5-89a9ce1303f4"]

        dfi.get.records_count(
            dataset_id,
            polygon = None,
            time_interval = (start_time, end_time),
            entities = entities,
        )
        ```
        """
        query_doc = _init_query_document(
            dataset_id=dataset_id, polygon=polygon, time_interval=time_interval, filter_fields=filter_fields
        )

        params = {"instance": dataset_id}
        payload = {}

        if polygon is None and entities is None:
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)
            params.update(query_doc.filter_fields_url_encoding())
            with self.conn.api_get("count", params=params) as response:
                return self._receive("count", response)

        if polygon is None and entities is not None:
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)
            sum_records = 0
            params.update(query_doc.filter_fields_url_encoding())
            for uid in entities:
                with self.conn.api_get(f"entities/{uid}/count", params=params) as response:
                    sum_records += self._receive("count", response)
            return sum_records

        if isinstance(polygon[0], list) or isinstance(polygon[0], tuple):
            payload = {}
            if time_interval is not None:
                payload["startTime"], payload["endTime"] = unpack_and_convert_time_interval(time_interval)
            if entities is not None:
                payload["include"] = entities
            if filter_fields:
                payload["fields"] = query_doc.get_document()["filters"]["fields"]
            payload["vertices"] = polygon
            with self.conn.api_post("polygon/count", payload=payload, params=params) as response:
                return self._receive("count", response)

        if isinstance(polygon[0], float):
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)
            if entities is not None:
                params["include"] = entities

            min_lng, min_lat, max_lng, max_lat = polygon
            params.update(query_doc.filter_fields_url_encoding())
            with self.conn.api_get(
                f"bounding-box/{min_lng}/{min_lat}/{max_lng}/{max_lat}/count", params=params
            ) as response:
                return self._receive("count", response)

    def records(
        self,
        dataset_id: str,
        entities: Optional[List[str]] = None,
        polygon: Optional[models.Polygon] = None,
        time_interval: Optional[models.TimeInterval] = None,
        add_payload_as_json: bool = False,
        filter_fields: dict = None,
    ) -> pd.DataFrame:
        """
        Get the records of the entities appearing within the given time, space and entity ids constraints.

        List of entities and polygon can not be left both to None.

        Start time and end time passed in the time_interval must be both valid datetime,
        with start_time < end_time or both None.

        :param dataset_id: the dataset to be queried.
        :param polygon: List of vertices [[lon1, lat1], [lon2, lat2], ...] or a list of four
            floats representing the bounding box extremes as [lon_min, lat_min, lon_max, lat_max].
            Non-valid input will raise an error.
        :param time_interval: Tuple with the Lower bound and the upper bound time constraints.
        :param entities: List of entity ids. It must be passed as list also for a single element.
        :param add_payload_as_json: If True it parses the payload as a JSON string into the column payload.
        :param filter_fields: Optional[dict]: {field_name: {FilterOperation: value}}
        :returns: Dataframe with the records of the entities found in polygon, given the input constraints.
        :raises `DFIInputValueError`: If `time_interval` or `polygon` are ill-formed.
        :raises `ValueError`: If no filter bound is specified.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dataset_id = "1234"
        start_time = datetime.strptime("2022-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime("2022-01-01T08:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        entities = ["299eb59a-e47e-48c0-9ad5-89a9ce1303f4"]

        dfi.get.records(
            dataset_id,
            time_interval = (start_time, end_time),
            entities = entities,
            add_payload_as_json=True
        )

        ```
        """
        query_doc = _init_query_document(
            dataset_id=dataset_id, polygon=polygon, time_interval=time_interval, filter_fields=filter_fields
        )

        params = {"instance": dataset_id}
        payload = {}

        if polygon is None:
            if entities is None:
                raise ValueError("You have to pass a list of entity ids or a polygon, or both.")
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)

            df_entities = []
            params.update(query_doc.filter_fields_url_encoding())
            for uid in entities:
                with self.conn.api_get(f"entities/{uid}/history", params=params) as response:
                    data = self._receive("history", response)
                    _logger.debug("Uid: %s \nHistory length: %i", uid, len(data))
                    data_formatted = []

                    for item in data:
                        payload = {}
                        if add_payload_as_json:
                            _logger.warning("Payload as JSON field is deprecated")
                        data_formatted.append(
                            [
                                item["id"],
                                datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                item["coordinate"][0],
                                item["coordinate"][1],
                                payload,
                            ]
                        )
                    df_single_entity = pd.DataFrame(
                        data_formatted, columns=["entity_id", "timestamp", "longitude", "latitude", "payload"]
                    )

                    if len(df_single_entity) > 0:
                        df_entities.append(df_single_entity)

            # Pandas is deprecating concatentation of empty dataframes, so we avoid adding empty
            # dataframes and check if the entire list of dataframes has data
            if len(df_entities) > 0:
                return pd.concat(df_entities).reset_index(drop=True)
            else:
                return pd.DataFrame(columns=["entity_id", "timestamp", "longitude", "latitude", "payload"])

        streamed_data = []

        if isinstance(polygon[0], (list, tuple)):
            # polygon passed by VERTICES - time and entity filters goes in the payload
            payload = {}
            if time_interval is not None:
                payload["startTime"], payload["endTime"] = unpack_and_convert_time_interval(time_interval)
            if entities is not None:
                payload["include"] = entities

            if filter_fields:
                payload["fields"] = query_doc.get_document()["filters"]["fields"]

            payload["vertices"] = polygon
            with self.conn.api_post("polygon/history", params=params, payload=payload) as response:
                streamed_data = self._receive("history", response)

        if isinstance(polygon[0], float):
            # polygon passed as a BOUNDING BOX - time and entity filters goes in the parameters
            if entities is not None:
                params["include"] = entities
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)

            min_lng, min_lat, max_lng, max_lat = polygon
            params.update(query_doc.filter_fields_url_encoding())
            with self.conn.api_get(
                f"bounding-box/{min_lng}/{min_lat}/{max_lng}/{max_lat}/history", params=params
            ) as response:
                streamed_data = self._receive("history", response)

        data_formatted = []
        for item in tqdm(streamed_data, disable=not self.conn.progress_bar, maxinterval=0.5, miniters=1):
            payload = {}
            if add_payload_as_json:
                if add_payload_as_json:
                    _logger.warning("Payload as JSON field is deprecated")
            data_formatted.append(
                [
                    item["id"],
                    datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    item["coordinate"][0],
                    item["coordinate"][1],
                    payload,
                ]
            )
        return pd.DataFrame(data_formatted, columns=["entity_id", "timestamp", "longitude", "latitude", "payload"])

    def entities(
        self,
        dataset_id: str,
        polygon: Optional[models.Polygon] = None,
        time_interval: Optional[models.TimeInterval] = None,
        filter_fields: Optional[dict] = None,
    ) -> List[Union[str, int]]:
        """
        Get the list of entity ids within a space and optional time constraint.

        If time constraints are not passed, the whole dataset is returned.
        Start time and end time passed in the time_interval must be both valid datetime, with
        start_time < end_time or both None.

        :param dataset_id: the dataset to be queried.
        :param polygon: List of vertices [[lon1, lat1], [lon2, lat2], ...] or a list of four
            floats representing the bounding box extremes as [lon_min, lat_min, lon_max, lat_max].
            Non valid input will raise an error.
        :param time_interval: Tuple with the Lower bound and the upper bound time constraints.
        :param filter_fields: Optional[dict]: {field_name: {FilterOperation: value}}
        :returns: List of unique entities in time interval and polygon.
        :raises `DFIInputValueError`: If `time_interval` or `polygon` are ill-formed.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dataset_id = "1234"
        start_time = datetime.strptime("2022-01-01T08:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime("2022-01-01T08:30:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        pimlico_tube_station =  [
            [-0.13410870522207574, 51.48932327401289],
            [-0.1355577905032419, 51.48887697878598],
            [-0.1339996342869938, 51.487266398812636],
            [-0.13279985400049554, 51.487508959676234],
            [-0.13230124401115972, 51.4875768764868],
            [-0.1319428680814667, 51.487955268294115],
            [-0.1322389177630896, 51.4883918703234],
            [-0.1322389177630896, 51.48887697878598],
            [-0.13301799587057417, 51.48930386996324],
            [-0.13410870522207574, 51.48932327401289],
        ]

        dfi.get.entities(
            dataset_id,
            polygon = pimlico_tube_station,
            time_interval = (start_time, end_time),
        )

        ```
        """

        query_doc = _init_query_document(
            dataset_id=dataset_id, polygon=polygon, time_interval=time_interval, filter_fields=filter_fields
        )

        params = {"instance": query_doc.get_dataset_id()}
        payload = {}

        if polygon is None:
            if time_interval is not None:
                payload["startTime"], payload["endTime"] = (query_doc.get_min_time(), query_doc.get_max_time())
            params.update(query_doc.filter_fields_url_encoding())
            with self.conn.api_get("entities", params=params, stream=True) as response:
                return self._receive("entities", response)

        if isinstance(polygon[0], list) or isinstance(polygon[0], tuple):
            # polygon passed by VERTICES
            if time_interval is not None:
                payload["startTime"], payload["endTime"] = (query_doc.get_min_time(), query_doc.get_max_time())

            payload["vertices"] = query_doc.get_polygon()

            if filter_fields:
                payload["fields"] = query_doc.get_document()["filters"]["fields"]

            with self.conn.api_post("polygon/entities", params=params, payload=payload) as response:
                return self._receive("entities", response)

        if isinstance(polygon[0], float):
            # polygon passed as a BOUNDING BOX
            params = {"instance": dataset_id}
            if time_interval is not None:
                params["startTime"], params["endTime"] = unpack_and_convert_time_interval(time_interval)
            min_lng, min_lat, max_lng, max_lat = polygon
            params.update(query_doc.filter_fields_url_encoding())
            with self.conn.api_get(
                f"bounding-box/{min_lng}/{min_lat}/{max_lng}/{max_lat}/entities", params=params, stream=True
            ) as response:
                return self._receive("entities", response)

    def _receive(self, response_type: str, response: requests.models.Response) -> Union[List[Any], int]:
        """
        Helper function to parse clients events as entities, and optionally show the progress bar.
        Client events are submitted as sequence of events with a parity check embedded in the last one.

        1. the event list is empty → raise response error - empty list

        2. the event list contains no finish message → raise response error - no final event reached

        3. the event list does contain a finish message, but it gives a different number than then
        number of messages event in the event list → raise response error - events missing

        4. The event list does contain a finish message and tells a number of messages corresponding
        to the number of message received → return the combined messages content as result.
        If no messages, return the correct empty data structure, based on the query type.

        :param response_type: str in the list of available options. It will raise a KeyError if the one provided
        is not defined.
        :param response: requests.models.Response for the given query.
        """

        dict_response_type_init = {
            "entities": [],
            "history": [],
            "count": 0,
        }

        try:
            # different initialization according to what the user want to query.
            results = dict_response_type_init[response_type]
        except KeyError as err:
            raise KeyError(f"Allowed options for what to receive are {dict_response_type_init.keys()}") from err

        client = sseclient.SSEClient(response)

        events_list_is_empty = True
        events_list_has_no_finish_message = True
        num_messages = 0

        for event in (pbar := tqdm(client.events(), disable=not self.conn.progress_bar, maxinterval=0.5, miniters=1)):
            events_list_is_empty = False

            if event.event == "keepAlive":
                continue

            elif event.event == "message":
                num_messages += 1
                # different concatenation according to the response type.
                if response_type == "entities":
                    results += [json.loads(event.data)]
                elif response_type in ["history", "count"]:
                    results += json.loads(event.data)
                else:
                    raise KeyError()

                # if self.conn.progress_bar:
                pbar.set_description(f"Collecting {_len_of(results):,} records")
                continue

            elif event.event == "finish":
                events_list_has_no_finish_message = False
                dict_data = json.loads(event.data)
                if "messageCount" not in dict_data:
                    _logger.warning("Please make sure the DFI API is up to date and higher than 1.6.0")
                else:
                    num_events_message_declared = dict_data.get("messageCount")
                    if num_messages != num_events_message_declared:  # 3
                        _raise_events_list_discrepancy(num_messages, num_events_message_declared)
                break

            elif event.event == "queryError":
                _raise_query_error_event(event)

            else:
                _raise_unexpected_event_found(event)

        if events_list_is_empty:  # 1
            _raise_events_list_empty()

        if events_list_has_no_finish_message:  # 2
            _raise_finish_event_not_reached()

        return results  # 4


def _len_of(list_or_int: Union[List, int]) -> int:
    if isinstance(list_or_int, int):
        return list_or_int
    else:
        return len(list_or_int)


def unpack_and_convert_time_interval(time_interval: models.TimeInterval) -> Tuple[str, str]:
    """from time interval to start_time, end_time in isoformat."""
    # The user can give None to one of the two values here.
    # The time interval validation manages the available options.
    start_time, end_time = time_interval
    if start_time is not None:
        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if end_time is not None:
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return start_time, end_time


def _raise_query_error_event(event: sseclient.Event) -> None:
    """helper to raise a QueryError response error"""
    msg = f"event returned QueryError: {event.data}"
    _logger.error(msg)
    raise validate.DFIResponseError(msg)


def _raise_unexpected_event_found(event: sseclient.Event) -> None:
    """helper to raise a an unexpected event was found"""
    msg = f"Unexpected event in bagging area: {event}"
    _logger.error(msg)
    raise validate.DFIResponseError(msg)


def _raise_events_list_empty() -> None:
    """helper to raise an error if the event list was empty."""
    msg = "DFI provided an empty events list."
    _logger.error(msg)
    raise validate.DFIResponseError(msg)


def _raise_events_list_discrepancy(num_event_messages_recorded: int, num_event_messages_declared: int) -> None:
    """
    Helper to raise an error if the number of messages-events does not correspond to the
    number of messages recorded in the finishing message.
    """
    msg = f"""
    DFI provided an event list with {num_event_messages_recorded} events of type 'message',
    but finish message declared {num_event_messages_declared} events of type 'message' were passed.
    """
    _logger.error(msg)
    raise validate.DFIResponseError(msg)


def _raise_finish_event_not_reached() -> None:
    """helper to raise a warning if the "finish" event was not reached."""
    msg = "DFI provided no 'finish' event in the event list."
    _logger.error(msg)
    raise validate.DFIResponseError(msg)


def _init_query_document(
    dataset_id: str,
    polygon: Optional[models.Polygon] = None,
    time_interval: Optional[models.TimeInterval] = None,
    filter_fields: Optional[dict] = None,
) -> QueryDocument:
    """Shim for initalising a query document to pass into other calls"""

    query_doc = QueryDocument()
    query_doc.set_dataset_id(dataset_id)
    if time_interval:
        query_doc.set_time_range(time_interval=time_interval)
    if polygon:
        query_doc.set_polygon(polygon)
    if filter_fields:
        query_doc.add_filter_fields_from_dict(fields_dict=filter_fields)

    return query_doc
