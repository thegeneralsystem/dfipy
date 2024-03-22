"""Integration tests for count on Query V1 API.

Since these tests have side effects on the Import API service and some rely on the state
of the service, the order in which the tests are run matters.  We use pytest-order to specify
the order in qhich tests are run.

These tests don't test for correctness of the API, only for correctness of the python wrapper.
"""

import logging

import pytest
from _pytest.python_api import RaisesContext

from dfi.errors import (
    FilterFieldInvalidNullability,
    FilterFieldNameNotInSchema,
    FilterFieldOperationValueError,
    FilterFieldTypeError,
    FilterFieldValueError,
)
from dfi.models.filters import FieldType, FilterField, FilterOperator

_logger = logging.getLogger(__name__)


@pytest.mark.order(0)
@pytest.mark.parametrize(
    "name,field_type,value,operation,nullable,expectation",
    [
        ("ip", FieldType("ip"), "0.0.0.0", FilterOperator("eq"), True, pytest.raises(FilterFieldNameNotInSchema)),
        (
            "ipv4",
            FieldType("ip"),
            ["0.0.0.0", "127.0.0.1"],
            FilterOperator("between"),
            True,
            pytest.raises(FilterFieldOperationValueError),
        ),
        ("ipv4", FieldType("ip"), "0.0.0.0", FilterOperator("eq"), False, pytest.raises(FilterFieldInvalidNullability)),
        (
            "ipv4",
            FieldType("unsigned number"),
            "0.0.0.0",
            FilterOperator("eq"),
            False,
            pytest.raises(FilterFieldTypeError),
        ),
        (
            "transportation_mode",
            FieldType("enum"),
            "flying",
            FilterOperator("eq"),
            False,
            pytest.raises(FilterFieldValueError),
        ),
    ],
)
def test_filter_field_error_conditions(
    dataset_schema: dict,  # type: ignore[type-arg]
    name: str,
    field_type: FieldType,
    value: str | int | list[int | str],
    operation: FilterOperator,
    nullable: bool,
    expectation: RaisesContext[
        FilterFieldNameNotInSchema
        | FilterFieldTypeError
        | FilterFieldInvalidNullability
        | FilterFieldOperationValueError
    ],
) -> None:
    with expectation:
        _ = FilterField(
            name=name,
            field_type=field_type,
            value=value,  # type: ignore[arg-type]
            operation=operation,
            nullable=nullable,
            schema=dataset_schema,
        )


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "name,field_type,value,operation,nullable",
    [
        ("ipv4", FieldType("ip"), "0.0.0.0", FilterOperator("eq"), True),
        ("transportation_mode", FieldType("enum"), "cycling", FilterOperator("eq"), False),
    ],
)
def test_filter_field_pass_validation(
    dataset_schema: dict,  # type: ignore[type-arg]
    name: str,
    field_type: FieldType,
    value: str | int | list[int | str],
    operation: FilterOperator,
    nullable: bool,
) -> None:
    filter_field = FilterField(
        name=name,
        field_type=field_type,
        value=value,  # type: ignore[arg-type]
        operation=operation,
        nullable=nullable,
        schema=dataset_schema,
    )
    assert isinstance(filter_field, FilterField)
