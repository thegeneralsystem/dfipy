"""A QueryDocument describes a query."""

from typing import Any

from typing_extensions import Self

from dfi.errors import InvalidQueryDocument
from dfi.models.filters import FilterField, Only, TimeRange
from dfi.models.filters.geometry import BBox, Polygon
from dfi.models.returns import Count, Records

FILTERS = "filters"
TIME = "time"
MIN_TIME = "minTime"
MAX_TIME = "maxTime"
RETURN_MODEL = "return"
COORDINATES = "coordinates"
FILTER_FIELDS = "fields"
DATASET_ID = "datasetId"
IDS = "id"
GEOMETRY = "geo"
ONLY = "only"


class QueryDocument:
    """A high level interface for declaring a DFI API Query."""

    def __init__(
        self,
        dataset_id: str,
        return_model: Records | Count,
        uids: list[str | int] | None = None,
        geometry: Polygon | BBox | None = None,
        time_range: TimeRange | None = None,
        filter_fields: list[FilterField] | None = None,
        only: Only | str | None = None,
    ) -> None:
        """Initialize a QueryDocument."""
        self._dataset_id: str
        self._return_model: Records | Count
        self._uids: list[str | int] | None = None
        self._geometry: Polygon | BBox | None = None
        self._time_range: TimeRange | None = None
        self._only: Only | None = None
        self._filter_fields: list[FilterField] | None = None

        self._document: dict[str, Any] = {"filters": {}}
        self.set_dataset_id(dataset_id)
        self.set_return_model(return_model)
        self.set_uids(uids)
        self.set_geometry(geometry)
        self.set_time_range(time_range)
        self.set_only(only)
        self.set_filter_fields(filter_fields)

        self.validate()

    def __repr__(self) -> str:
        """Class representation."""
        return f"""QueryDocument(
                dataset_id={self._dataset_id},
                uids={self._uids},
                geometry={self._geometry},
                time_range={self._time_range},
                filter_fields={self._filter_fields},
                only={self._only},
                return_model={self._return_model},
            )"""

    def __str__(self) -> str:
        """Class string formatting."""
        return f"""QueryDocument(
                dataset_id={self._dataset_id},
                uids={self._uids},
                geometry={self._geometry},
                time_range={self._time_range},
                filter_fields={self._filter_fields},
                only={self._only},
                return_model={self._return_model},
            )"""

    def validate(self) -> Self:
        """Validate the QueryDocument.

        Raises
        ------
        InvalidQueryDocument
        """
        self._validate_dataset_id(self._dataset_id)
        self._validate_return_model(self._return_model)
        self._validate_only_filter(self._only, self._return_model)

        return self

    @staticmethod
    def _validate_dataset_id(dataset_id: str) -> None:
        """Check that a dataset_id is set and is a string.

        Parameters
        ----------
        dataset_id:
            a dataset id.
        """
        match dataset_id:
            case str():
                pass
            case _:
                raise InvalidQueryDocument("QueryDocument must have a dataset_id.")

    @staticmethod
    def _validate_return_model(return_model: Records | Count) -> None:
        """Check that a return_model is set and is a Records | Count.

        Parameters
        ----------
        return model:
            How results should be returned.
        """
        match return_model:
            case Records() | Count():
                pass
            case _:
                raise InvalidQueryDocument("QueryDocument must have a return_model.")

    @staticmethod
    def _validate_only_filter(only: Only | str | None, return_model: Records | Count) -> None:
        """Check that an only filter and return_model combination is valid.

        Parameters
        ----------
        only:
            Only filter.
        return model:
            How results should be returned.

        Returns
        -------
        None
        """
        match only, return_model:
            case None, Records() | Count():
                pass
            case Only() | str(), Records():
                pass
            case Only() | str(), Count():
                raise InvalidQueryDocument(f"'{only}' filter is only valid combined with a 'records' return_model.")
            case _, Records() | Count():
                raise InvalidQueryDocument(f"'{only}' is not a valid 'Only' filter.")
            case _:
                raise InvalidQueryDocument(f"'{only}' filter is only valid combined with a 'records' return_model.")

    def build(self) -> dict:
        """Return a formatted Query Document.

        Returns
        -------
        document:
            formatted  Query Document
        """
        self.validate()
        return dict(sorted(self._document.items(), key=lambda x: x[0]))

    @property
    def dataset_id(self) -> str | None:
        """The dataset_id property."""
        return self._dataset_id

    def set_dataset_id(self, dataset_id: str) -> Self:
        """Set the dataset_id property."""
        self._validate_dataset_id(dataset_id)

        match dataset_id:
            case str():
                self._dataset_id = dataset_id
                self._document[DATASET_ID] = dataset_id
            case _:
                raise ValueError("dataset_id must be of type str.")

        return self

    @property
    def return_model(self) -> Records | Count:
        """The return_model property."""
        return self._return_model

    def set_return_model(self, return_model: Records | Count) -> Self:
        """Set the return_model property."""
        self._validate_return_model(return_model)
        self._validate_only_filter(self._only, return_model)

        match return_model:
            case Records() | Count():
                self._return_model = return_model
                self._document[RETURN_MODEL] = return_model.build()
            case _:
                raise ValueError("return_model must be of type ReturnModel.")

        return self

    @property
    def uids(self) -> list[str | int] | None:
        """The uids property."""
        return self._uids

    def set_uids(self, uids: list[str | int] | None) -> Self:
        """Set the uids property."""
        match uids:
            case list():
                self._uids = uids
                self._document[FILTERS][IDS] = uids
            case None:
                self._uids = uids
                self._document[FILTERS].pop(IDS, None)
            case _:
                raise ValueError("uids must be of type list[str | int].")

        return self

    @property
    def only(self) -> Only | None:
        """The only property."""
        return self._only

    def set_only(self, only: Only | str | None) -> Self:
        """Set the only property."""
        self._validate_only_filter(only, self._return_model)

        match only:
            case Only():
                self._only = only
                self._document[FILTERS][ONLY] = self._only.build()
            case str():
                self._only = Only(only)
                self._document[FILTERS][ONLY] = self._only.build()
            case None:
                self._only = only
                self._document[FILTERS].pop(ONLY, None)
            case _:
                raise ValueError("only must be of type Only | None.")

        return self

    @property
    def time_range(self) -> TimeRange | None:
        """The time_range property."""
        return self._time_range

    def set_time_range(self, time_range: TimeRange | None) -> Self:
        """Set the time_range property."""
        match time_range:
            case TimeRange():
                self._time_range = time_range
                self._document[FILTERS][TIME] = time_range.build()
            case None:
                self._time_range = time_range
                self._document[FILTERS].pop(TIME, None)
            case _:
                raise ValueError("time_range must be of type TimeRange | None.")

        return self

    @property
    def geometry(self) -> Polygon | BBox | None:
        """The geometry property."""
        return self._geometry

    def set_geometry(self, geometry: Polygon | BBox | None) -> Self:
        """Set the geometry property."""
        match geometry:
            case Polygon() | BBox():
                self._geometry = geometry
                self._document[FILTERS][GEOMETRY] = geometry.build()
            case None:
                self._geometry = geometry
                self._document[FILTERS].pop(GEOMETRY, None)
            case _:
                raise ValueError("geometry must be of type Polygon | BBox | None.")

        return self

    @property
    def filter_fields(self) -> list[FilterField] | None:
        """The filter_fields property."""
        return self._filter_fields

    def set_filter_field(self, filter_field: FilterField) -> Self:
        """Set a filter field.

        - An existing FilterField will be overwritten by a new FilterField with the same name.
        - Possibility that more fields can be set than are allowed.  The API will catch this error.
        """
        match filter_field:
            case FilterField():
                if self._document[FILTERS].get(FILTER_FIELDS) is None:
                    self._document[FILTERS][FILTER_FIELDS] = {}

                self._document[FILTERS][FILTER_FIELDS].update(filter_field.build())
            case _:
                raise ValueError("filter_field must be of type FilterField.")

        return self

    def set_filter_fields(self, filter_fields: list[FilterField] | None) -> Self:
        """Set a filter field.

        - An existing FilterField will be overwritten by a new FilterField with the same name.
        - Possibility that more fields can be set than are allowed.  The API will catch this error.

        Parameters
        ----------
        filter_fields:

            - If `list[FilterField]`, will iteratively add each field.
            - If `None`, will delete all existing filter fields.
        """
        match filter_fields:
            case list():
                for field in filter_fields:
                    self.set_filter_field(field)
            case None:
                self._filter_fields = None
                self._document[FILTERS].pop(FILTER_FIELDS, None)
            case _:
                raise ValueError("filter_field must be of type list[FilterField] | None.")

        return self
