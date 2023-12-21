import json
from datetime import datetime
from enum import Enum
from typing import Optional

from dfi import models, validate


class FilterOperator(str, Enum):
    lt = "lt"
    gt = "gt"
    gte = "gte"
    lte = "lte"
    eq = "eq"
    neq = "neq"
    between = "between"
    outside = "outside"


FILTERS = "filters"
TIME = "time"
MIN_TIME = "minTime"
MAX_TIME = "maxTime"
RETURN_MODEL = "return"
COORDINATES = "coordinates"
FILTER_FIELDS = "fields"
DATASET_ID = "datasetId"
GEO = "geo"


class QueryDocument(dict):

    """A high level interface for declaring a DFI API Query"""

    def __init__(self) -> None:
        self._internal_document = {FILTERS: {}, RETURN_MODEL: "records"}

    def set_dataset_id(self, id: str) -> None:
        self._internal_document[DATASET_ID] = id

    def get_dataset_id(self) -> Optional[str]:
        return self._internal_document.get(DATASET_ID)

    def set_time_range(self, time_interval: models.TimeInterval):
        validate.time_interval(time_interv=time_interval)
        if not self._internal_document.get(TIME):
            self._internal_document[FILTERS][TIME] = {}
        self._internal_document[FILTERS][TIME][MIN_TIME] = self._format_timestamp(time_interval[0])
        self._internal_document[FILTERS][TIME][MAX_TIME] = self._format_timestamp(time_interval[1])

    def get_min_time(self) -> Optional[datetime]:
        return self._internal_document[FILTERS].get(TIME).get(MIN_TIME)

    def get_max_time(self) -> Optional[datetime]:
        return self._internal_document[FILTERS].get(TIME).get(MAX_TIME)

    @staticmethod
    def _format_timestamp(dt: datetime) -> str:
        """
        Uses formatting in unpack_and_convert_time_interval under services.get
        """
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def set_polygon(self, vertices: models.Polygon) -> None:
        if isinstance(vertices[0], float):
            # The polygon is a bounding box
            raise ValueError("Bounding boxes are not able to be coerced to polygons")

        validate.polygon(poly=vertices)
        self._internal_document[FILTERS][GEO] = {"type": "Polygon", COORDINATES: vertices}

    def get_polygon(self) -> Optional[models.Polygon]:
        return self._internal_document[FILTERS].get(GEO).get(COORDINATES)

    def set_id_filter(self, ids: list) -> None:
        validate.entities(input_entities=ids)
        self._internal_document[FILTERS]["id"] = ids

    def add_filter_field(self, field_name: str, operation: FilterOperator, value) -> None:
        if not self._internal_document[FILTERS].get(FILTER_FIELDS):
            self._internal_document[FILTERS][FILTER_FIELDS] = dict()
        if list(FilterOperator).__contains__(operation):
            self._internal_document[FILTERS][FILTER_FIELDS][field_name] = {operation: value}
        else:
            raise validate.DFIInputValueError(f"{operation} not a valid filter operation")

    def add_filter_fields_from_dict(self, fields_dict: models.FilterFields) -> None:
        """
        Set multiple filter fields by passing in a dictionary with format
        {FIELD_NAME: {FILTER_OPERATION: VALUE}}
        """
        if not self._internal_document[FILTERS].get(FILTER_FIELDS):
            self._internal_document[FILTERS][FILTER_FIELDS] = dict()

        for k, v in fields_dict.items():
            if isinstance(v, dict):
                for k_2, v_2 in v.items():
                    self.add_filter_field(k, k_2, v_2)
            else:
                raise validate.DFIInputValueError()

    def get_document(self) -> dict:
        """
        Returns a query document that can be used to submit a query
        """
        return self._internal_document

    def filter_fields_url_encoding(self) -> dict:
        """
        While we are in a transition period we still need to encode filter field parameters as a URL parameter

        These can be tacked onto other stuff going into query params.
        """

        fields: dict = self._internal_document[FILTERS].get(FILTER_FIELDS, dict())
        query_fields = dict()

        for k, v in fields.items():
            for k_2, v_2 in v.items():
                query_fields[f"{k}[{k_2}]"] = json.dumps(v_2)

        return query_fields
