"""FilterField filter model definition."""

import logging
from enum import Enum
from typing import TypeAlias, cast

from typing_extensions import Self

from dfi.errors import (
    FilterFieldInvalidNullability,
    FilterFieldNameNotInSchema,
    FilterFieldOperationValueError,
    FilterFieldTypeError,
    FilterFieldValueError,
    UnreachableError,
)

UINT8_MIN = 0
UINT8_MAX = 255
UINT32_MIN = 0
UINT32_MAX = 4_294_967_295
INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647
NUM_IPV4_BYTES = 4

FieldValue: TypeAlias = str | int | list[int | str] | None

_logger = logging.getLogger(__name__)


class FilterOperator(str, Enum):
    """Enumerates the valid operations on FilterFields."""

    LT = "lt"
    LG = "gt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"
    BETWEEN = "between"
    OUTSIDE = "outside"

    def __str__(self) -> str:
        """Return the value as a string rather than a string of the full enum."""
        return self.value

    def build(self) -> str:
        """Return a FilterOperator definition for QueryDocument."""
        return str(self)


class FieldType(str, Enum):
    """Enumerates the valid types for a FilterField."""

    SIGNED_NUMBER = "signed number"
    UNSIGNED_NUMBER = "unsigned number"
    IP = "ip"
    ENUM = "enum"


class FilterField:
    """Provides type deifnition and validation for defining how to filter on FilterFields in a dataset."""

    _name: str
    _field_type: FieldType
    _value: FieldValue
    _operation: FilterOperator
    _nullable: bool = False

    def __repr__(self) -> str:
        """Class representation."""
        return f"FilterField(name={self._name}, field_type={self._field_type.value}, operation={self._operation}, value={self._value})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"FilterField(name={self._name}, field_type={self._field_type.value}, operation={self._operation}, value={self._value})"

    def __init__(
        self,
        name: str,
        field_type: FieldType,
        value: FieldValue,
        operation: FilterOperator,
        nullable: bool = False,
        schema: dict | None = None,
    ) -> None:
        """Create a FilterField.

        Parameters
        ----------
        name:
            Name of the field.  This should match a name in the dataset schema.
        field_type:
            Type of the FilterField.
        value:
            The value to use as a comparison.
        operation:
            How to filter on the field. Default `False`
        nullable:
            If `True` the field can have null values, if `False` will error on null values.
        schema:
            Dataset schema, if present, will validate the Filter Field against the schema.
            Field validation does not cover all cases.  Some problems can only be caught by the DFI API.

        Examples
        --------
        ### FilterField
        ```python
        FilterField("vegetables", "enum")
        ```
        ```python
        FilterField([0.0, 0.0, 1.0, 1.0])
        ```
        """
        self._name = name
        self._field_type = field_type
        self._value = value
        self._operation = operation
        self._nullable = nullable

        self.validate(schema)

    @property
    def name(self) -> str:
        """The name property."""
        return self._name

    @property
    def field_type(self) -> FieldType:
        """The field_type property."""
        return self._field_type

    @property
    def value(self) -> FieldValue:
        """The value property."""
        return self._value

    @property
    def operation(self) -> FilterOperator:
        """The operation property."""
        return self._operation

    @property
    def nullable(self) -> bool:
        """The nullable property."""
        return self._nullable

    def validate(self, schema: dict | None) -> Self:
        """Validate the Filter Field.

        Parameters
        ----------
        schema:
            Dataset schema, if present, will validate the Filter Field against the schema.

        Returns
        -------
        Self

        Raises
        ------
        FilterFieldNameNotInSchema
        FilterFieldValueError
        FilterFieldOperationValueError
        """
        match self._field_type:
            case FieldType():
                pass
            case _:
                raise ValueError(f"Expected FilterType, found '{type(self._operation)}'")

        match self._operation:
            case FilterOperator():
                pass
            case _:
                raise ValueError(f"Expected FilterOperator, found '{type(self._operation)}'")

        self._filter_field_operation_is_valid(self._field_type, self._operation)

        if schema:
            _logger.info("No schema provided skipping validation on field name and nullability.")
            self._validate_filter_field_name_in_schema(self._name, schema)
            self._validate_filter_field_type_matches_schema(self._name, self._field_type, schema)
            self._validate_filter_field_nullability(self._name, self._nullable, schema)
            self._filter_field_value_is_valid(self._name, self._value, schema)

        return self

    def build(self) -> dict:
        """Format the FilterField for use in Query Document."""
        return {
            self._name: {
                self._operation.build(): self._value,
            }
        }

    @staticmethod
    def _validate_filter_field_name_in_schema(name: str, schema: dict) -> None:
        """Check if the name is a field registered in the dataset schema.

        Parameters
        ----------
        name:
            Name of the Filter Field.
        schema:
            Dataset schema to validate name against.

        Raises
        ------
        FilterFieldNameNotInSchema
        """
        if name not in schema:
            raise FilterFieldNameNotInSchema(f"'{name}' is not a field registered to the dataset schema.")

    @staticmethod
    def _validate_filter_field_type_matches_schema(name: str, field_type: FieldType, schema: dict) -> None:
        """Check if the filter field type matches type in the schema.

        Parameters
        ----------
        name:
            Name of the Filter Field.
        schema:
            Dataset schema to validate name against.

        Raises
        ------
        FilterFieldTypeError
        """
        field = schema[name]
        match field.get("type"), field_type.value:
            case ("ip", "ip") | ("enum", "enum"):
                pass
            case "number", ("signed number" | "unsigned number"):
                match signed := field.get("signed"), field_type.value:
                    case None | False, "unsigned number":
                        pass
                    case True, "signed number":
                        pass
                    case _, _:
                        raise FilterFieldTypeError(f"'{field_type}' does not match type in schema '{field} - {signed}'")
            case _:
                raise FilterFieldTypeError(f"'{field_type}' does not match type in schema '{field}'")

    @staticmethod
    def _validate_signed_number(value: int) -> None:
        if value < INT32_MIN or value > INT32_MAX:
            raise FilterFieldValueError(
                f"'{value}' is not a valid INT32 to filter with for a signed 'number' Filter Field."
            )

    @staticmethod
    def _validate_unsigned_number(value: int) -> None:
        if value < UINT32_MIN or value > UINT32_MAX:
            raise FilterFieldValueError(
                f"'{value}' is not a valid UINT32 to filter with for an unsigned 'number' Filter Field."
            )

    @staticmethod
    def _validate_ipv4(value: str) -> None:
        bytes = value.split(".")
        if len(bytes) != NUM_IPV4_BYTES:
            raise FilterFieldValueError(f"ip values should have 4 bytes, found {len(bytes)} in '{value}'.")

        for byte in bytes:
            if int(byte) < UINT8_MIN or int(byte) > UINT8_MAX:
                raise FilterFieldValueError(f"'{value}' is not a valid IPv4 to filter with for an 'ip' Filter Field.")

    @staticmethod
    def _validate_enum_value(value: str, enum_values: list[str] | tuple[str] | set[str], field_name: str) -> None:
        if value not in enum_values:
            raise FilterFieldValueError(
                f"'{value}' is not a valid enum value registered in the dataset to filter with for the '{field_name}' 'enum' Filter Field."
            )

    def _filter_field_value_is_valid(self, name: str, value: FieldValue, schema: dict) -> None:
        """Check if the filter value is valid for the field type.

        Parameters
        ----------
        name:
            Name of the Filter Field.
        value:
            Value to filter the field on.
        schema:
            Dataset schema to validate name against.

        Raises
        ------
        FilterFieldValueError
        ValueError
        TypeError
        """
        field = schema[name]
        match field["type"]:
            case "number":
                if ((signed := field.get("signed")) is None) or (signed is False):
                    match value:
                        case int():
                            self._validate_unsigned_number(value)
                        case list():
                            for number in value:
                                match number:
                                    case int():
                                        self._validate_unsigned_number(number)
                                    case _:
                                        raise ValueError(f"{value} is not a valid UINT32 number.")
                        case _:
                            raise ValueError(f"{value} is not a valid UINT32 number.")
                else:  # field["signed"] is True:
                    match value:
                        case int():
                            self._validate_signed_number(value)
                        case list():
                            for number in value:
                                match number:
                                    case int():
                                        self._validate_signed_number(number)
                                    case _:
                                        raise ValueError(f"{value} is not a valid UINT32 number.")
                        case _:
                            raise ValueError(f"{value} is not a valid INT32 number.")
            case "ip":
                match value:
                    case str():
                        self._validate_ipv4(value)
                    case _:
                        raise ValueError(f"{value} is not a valid ipv4 string.")
            case "enum":
                match value:
                    case str():
                        match enum_values := field.get("values", None):
                            case list() | tuple() | set():
                                enum_values = cast(list[str], enum_values)
                                self._validate_enum_value(value, enum_values, name)
                            case None:
                                raise ValueError("No enum value list provided to validate value against.")
                            case _:
                                raise TypeError(f"'{enum_values}' is not a valid list of enum values.")
                    case _:
                        raise ValueError(f"{value} is not a valid enum string.")
            case _:
                raise UnreachableError

    @staticmethod
    def _filter_field_operation_is_valid(field_type: FieldType, operation: FilterOperator) -> None:
        """Check if the filter value is valid for the field type.

        Parameters
        ----------
        operation:
            How to filter on the field.
        schema:
            Dataset schema to validate name against.

        Raises
        ------
        FilterFieldOperationValueError
        """
        match field_type:
            case FieldType.UNSIGNED_NUMBER | FieldType.SIGNED_NUMBER:
                # all operations are valid for all number Fields
                pass
            case FieldType.IP:
                if operation not in [FilterOperator.EQ, FilterOperator.NEQ]:
                    raise FilterFieldOperationValueError(
                        f"'{operation}' is not a valid operation to filter with for an 'ip' Filter Field."
                    )
            case FieldType.ENUM:
                if operation not in [FilterOperator.EQ, FilterOperator.NEQ]:
                    raise FilterFieldOperationValueError(
                        f"'{operation}' is not a valid operation to filter with for an 'enum' Filter Field."
                    )
            case _:
                raise UnreachableError

    @staticmethod
    def _validate_filter_field_nullability(name: str, nullable: bool, schema: dict) -> None:
        """Check if the FilterField nullability matches the schema.

        Parameters
        ----------
        name:
            Name of the Filter Field.
        nullable:
            Nullability of the field.
        schema:
            Dataset schema to validate name against.

        Raises
        ------
        FilterFieldInvalidNullability
        """
        null_setting = schema[name].get("nullable")
        match (nullable, null_setting):
            case (True, None):
                raise FilterFieldInvalidNullability(
                    f"Schema indicates field '{name}' is not nullable, found {nullable}"
                )
            case (True, False):
                raise FilterFieldInvalidNullability(
                    f"Schema indicates field '{name}' is not nullable, found {nullable}"
                )
            case (False, True):
                raise FilterFieldInvalidNullability(f"Schema indicates field '{name}' is nullable, found {nullable}")
            case _:
                pass
