"""Tests for FilterField."""

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

UINT32_MIN = 0
UINT32_MAX = 4_294_967_295
INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        ("vegetables", "enum", "califlower", FilterOperator("eq"), None, pytest.raises(ValueError)),
        ("vegetables", FieldType("enum"), "califlower", "eq", None, pytest.raises(ValueError)),
    ],
)
def test_filter_field_argument_type_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,
    expectation: RaisesContext[ValueError],
) -> None:
    """Test FilterField errors are raised."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            {"fruits": {"type": "enum", "values": ["lychee", "durian", "tomato", "aubergine"]}},
            pytest.raises(FilterFieldNameNotInSchema),
        ),
    ],
)
def test_filter_field_name_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldNameNotInSchema],
) -> None:
    """Test FilterField errors are raised for names that don't exist in the schema."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,nullable,schema,expectation",
    [
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            True,
            {"vegetables": {"type": "enum", "values": []}},
            pytest.raises(FilterFieldInvalidNullability),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            True,
            {"vegetables": {"type": "enum", "nullable": False, "values": []}},
            pytest.raises(FilterFieldInvalidNullability),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            False,
            {"vegetables": {"type": "enum", "nullable": True, "values": []}},
            pytest.raises(FilterFieldInvalidNullability),
        ),
    ],
)
def test_filter_field_nullable_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    nullable: bool,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldInvalidNullability],
) -> None:
    """Test FilterField errors are raised for non-matching nullability."""
    with expectation:
        FilterField(name, field_type, value, operation, nullable, schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        (
            "ip",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("eq"),
            {"ip": {"type": "enum", "values": []}},
            pytest.raises(FilterFieldTypeError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            [-22, 0],
            FilterOperator("outside"),
            {"delta distance": {"type": "number", "signed": False}},
            pytest.raises(FilterFieldTypeError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            [-22, 0],
            FilterOperator("outside"),
            {"delta distance": {"type": "number"}},
            pytest.raises(FilterFieldTypeError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            [22, 30],
            FilterOperator("between"),
            {"absolute distance": {"type": "number", "signed": True}},
            pytest.raises(FilterFieldTypeError),
        ),
    ],
)
def test_filter_field_type_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldOperationValueError],
) -> None:
    """Test FilterField errors are raised for FieldType.ENUM fields."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("lt"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("lte"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("gt"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("gte"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("between"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("outside"),
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            {"vegetables": {"type": "enum", "values": ["broccoli", "carrot", "mustard"], "nullable": False}},
            pytest.raises(FilterFieldValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            {"vegetables": {"type": "enum", "values": "mustard", "nullable": False}},
            pytest.raises(TypeError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            {"vegetables": {"type": "enum", "values": None, "nullable": False}},
            pytest.raises(ValueError),
        ),
        (
            "vegetables",
            FieldType("enum"),
            1234,
            FilterOperator("eq"),
            {"vegetables": {"type": "enum", "values": ["broccoli", "carrot", "mustard"], "nullable": False}},
            pytest.raises(ValueError),
        ),
    ],
)
def test_filter_field_enum_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldOperationValueError | FilterFieldValueError],
) -> None:
    """Test FilterField errors are raised for FieldType.ENUM fields."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,nullable,schema,expectation",
    [
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("lt"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("lte"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("gt"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("gte"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("between"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("outside"),
            True,
            None,
            pytest.raises(FilterFieldOperationValueError),
        ),
        pytest.param(
            "ipv4",
            FieldType("ip"),
            "256.0.0.0",
            FilterOperator("eq"),
            True,
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
            id="address bytes out of range",
        ),
        pytest.param(
            "ipv4",
            FieldType("ip"),
            "-1.0.0.0",
            FilterOperator("eq"),
            True,
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
            id="address bytes out of range",
        ),
        pytest.param(
            "ipv4",
            FieldType("ip"),
            "0.0.0",
            FilterOperator("eq"),
            True,
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
            id="address <4 bytes",
        ),
        (
            "ipv4",
            FieldType("ip"),
            255,
            FilterOperator("eq"),
            True,
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(ValueError),
        ),
    ],
)
def test_filter_field_ip_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    nullable: bool,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldOperationValueError],
) -> None:
    """Test FilterField errors are raised for FieldType.IP fields."""
    with expectation:
        FilterField(name, field_type, value, operation, nullable, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        (
            "absolute distance",
            FieldType("unsigned number"),
            UINT32_MIN - 1,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            UINT32_MAX + 1,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            [UINT32_MIN - 1, 0],
            FilterOperator("between"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            [0, UINT32_MAX + 1],
            FilterOperator("between"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            0.0,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(ValueError),
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            None,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(ValueError),
        ),
    ],
)
def test_filter_field_unsigned_number_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldOperationValueError],
) -> None:
    """Test FilterField errors are raised for FieldType.IP fields."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expectation",
    [
        (
            "delta distance",
            FieldType("signed number"),
            INT32_MIN - 1,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            INT32_MAX + 1,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            [INT32_MIN - 1, 0],
            FilterOperator("between"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            [0, INT32_MAX + 1],
            FilterOperator("between"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(FilterFieldValueError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            0.0,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(ValueError),
        ),
        (
            "delta distance",
            FieldType("signed number"),
            None,
            FilterOperator("eq"),
            {
                "absolute distance": {"type": "number", "signed": False},
                "delta distance": {"type": "number", "signed": True},
                "ipv4": {"type": "ip", "nullable": True},
                "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
            },
            pytest.raises(ValueError),
        ),
    ],
)
def test_filter_field_signed_number_error_conditions(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expectation: RaisesContext[FilterFieldOperationValueError],
) -> None:
    """Test FilterField errors are raised for FieldType.IP fields."""
    with expectation:
        FilterField(name, field_type, value, operation, schema=schema).build()


#########################
# Normal Conditions
#########################
@pytest.mark.parametrize(
    "name,field_type,value,operation,schema,expected",
    [
        (
            "vegetables",
            FieldType("enum"),
            "cauliflower",
            FilterOperator("eq"),
            {"vegetables": {"type": "enum", "values": ["cauliflower", "carrot"]}},
            {"vegetables": {"eq": "cauliflower"}},
        ),
        (
            "ipv4",
            FieldType("ip"),
            "0.0.0.0",
            FilterOperator("eq"),
            {"ipv4": {"type": "ip"}},
            {"ipv4": {"eq": "0.0.0.0"}},
        ),
        (
            "absolute distance",
            FieldType("unsigned number"),
            [22, 30],
            FilterOperator("between"),
            {"absolute distance": {"type": "number", "signed": False}},
            {"absolute distance": {"between": [22, 30]}},
        ),
        (
            "delta distance",
            FieldType("signed number"),
            [-22, 0],
            FilterOperator("outside"),
            {"delta distance": {"type": "number", "signed": True}},
            {"delta distance": {"outside": [-22, 0]}},
        ),
    ],
)
def test_filter_field(
    name: str,
    field_type: FieldType,
    value: str | int | list[int],
    operation: FilterOperator,
    schema: dict | None,  # type: ignore[type-arg]
    expected: dict,  # type: ignore[type-arg]
) -> None:
    """Test FilterField can be built for different field types."""
    assert expected == FilterField(name, field_type, value, operation, schema=schema).build()


@pytest.mark.parametrize(
    "filter_fields,expected",
    [
        pytest.param(
            [
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                )
            ],
            {"delta distance": {"outside": [-22, 0]}},
            id="signed number",
        ),
        pytest.param(
            [
                FilterField(
                    name="absolute distance",
                    field_type=FieldType("unsigned number"),
                    value=[22, 30],
                    operation=FilterOperator("between"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                )
            ],
            {"absolute distance": {"between": [22, 30]}},
            id="unsigned number",
        ),
        pytest.param(
            [
                FilterField(
                    name="absolute distance",
                    field_type=FieldType("unsigned number"),
                    value=[22, 30],
                    operation=FilterOperator("between"),
                    schema={
                        "absolute distance": {"type": "number"},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                )
            ],
            {"absolute distance": {"between": [22, 30]}},
            id="unsigned number (unspecified)",
        ),
        pytest.param(
            [
                FilterField(
                    name="ipv4",
                    field_type=FieldType("ip"),
                    value="0.0.0.0",
                    operation=FilterOperator("eq"),
                    nullable=True,
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                )
            ],
            {"ipv4": {"eq": "0.0.0.0"}},
            id="ip",
        ),
        pytest.param(
            [
                FilterField(
                    name="vegetables",
                    field_type=FieldType("enum"),
                    value="mustard",
                    operation=FilterOperator("eq"),
                    nullable=True,
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                )
            ],
            {"vegetables": {"eq": "mustard"}},
            id="enum",
        ),
        pytest.param(
            [
                FilterField(
                    name="delta distance",
                    field_type=FieldType("signed number"),
                    value=[-22, 0],
                    operation=FilterOperator("outside"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                ),
                FilterField(
                    name="absolute distance",
                    field_type=FieldType("unsigned number"),
                    value=[22, 30],
                    operation=FilterOperator("between"),
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                ),
                FilterField(
                    name="ipv4",
                    field_type=FieldType("ip"),
                    value="0.0.0.0",
                    operation=FilterOperator("eq"),
                    nullable=True,
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                ),
                FilterField(
                    name="vegetables",
                    field_type=FieldType("enum"),
                    value="mustard",
                    operation=FilterOperator("eq"),
                    nullable=True,
                    schema={
                        "absolute distance": {"type": "number", "signed": False},
                        "delta distance": {"type": "number", "signed": True},
                        "ipv4": {"type": "ip", "nullable": True},
                        "vegetables": {"type": "enum", "nullable": True, "values": ["carrot", "mustard"]},
                    },
                ),
            ],
            {
                "absolute distance": {"between": [22, 30]},
                "delta distance": {"outside": [-22, 0]},
                "ipv4": {"eq": "0.0.0.0"},
                "vegetables": {"eq": "mustard"},
            },
            id="two field list",
        ),
    ],
)
def test_filter_fields_into_document(
    filter_fields: list[FilterField],
    expected: dict,  # type: ignore[type-arg]
) -> None:
    """Test that a FilterFields dictionary can be built from a list of FilterFields."""
    document = {}
    for field in filter_fields:
        document.update(field.build())
    assert expected == document
