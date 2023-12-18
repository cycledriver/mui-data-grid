"""The item module contains the representations of a grid filter model's individual
filter items.

Each filter item corresponds to a configured filter from the data grid's filter window.
"""

from typing import Any, ClassVar, Optional, Union

from pydantic import AliasChoices, Field
from typing_extensions import TypeAlias, TypedDict

from mui.v5.grid.base import GridBaseModel, OptionalKeys

ColumnField: TypeAlias = str
Id: TypeAlias = Optional[Union[int, str]]
# https://mui.com/x/react-data-grid/filtering/#customize-the-operators
# https://mui.com/x/api/data-grid/grid-filter-operator/
OperatorValue: TypeAlias = Optional[str]
Value: TypeAlias = Optional[Any]


class SnakeCaseGridFilterItemDict(TypedDict):
    """The dictionary representation of a valid snake case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-item/

    Attributes:
        column_field (str): The column from which we want to filter the rows.
            - Alias: columnField
        id (str | int | not set): Must be unique. Only useful when the model contains
            several items.
        operator_value (str | None | not set): The name of the operator we want to
            apply. Will become required on @mui/x-data-grid@6.X.
            - Alias: operatorValue
        value: (Any | None | not set): The filtering value.
            The operator filtering function will decide for each row if the row values
            is correct compared to this value.
    """

    column_field: ColumnField
    id: Id
    operator_value: OperatorValue
    value: Value


class CamelCaseGridFilterItemDict(TypedDict):
    """The dictionary representation of a valid camel case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-item/

    Attributes:
        columnField (str): The column from which we want to filter the rows.
            - Alias: columnField
        id (str | int | not set): Must be unique. Only useful when the model contains
            several items.
        operatorValue (str | None | not set): The name of the operator we want to
            apply. Will become required on @mui/x-data-grid@6.X.
            - Alias: operatorValue
        value: (Any | None | not set): The filtering value.
            The operator filtering function will decide for each row if the row values
            is correct compared to this value.
    """

    columnField: ColumnField
    id: Id
    operatorValue: OperatorValue
    value: Value


"""The GridFilterItemDict is an alias for either a snake or camel case grid filter item.

Both formats are supported by the GridFilterItem model.
"""
GridFilterItemDict: TypeAlias = Union[
    CamelCaseGridFilterItemDict, SnakeCaseGridFilterItemDict
]


class GridFilterItem(GridBaseModel):
    """A grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-item/

    Attributes:
        column_field (str): The column from which we want to filter the rows.
            - Alias: columnField
        id (str | int | not set): Must be unique. Only useful when the model contains
            several items.
        operator_value (str | None | not set): The name of the operator we want to
            apply. Will become required on @mui/x-data-grid@6.X. This is a string value
            because Material-UI supports arbitrary / custom operators.
            - Alias: operatorValue
        value: (Any | None | not set): The filtering value.
            The operator filtering function will decide for each row if the row values
            is correct compared to this value.
    """

    column_field: ColumnField = Field(
        default=...,
        title="Column Field",
        description="The column from which we want to filter the rows.",
        validation_alias=AliasChoices("column_field", "columnField"),
    )
    id: Id = Field(
        default=None,
        title="Identifier",
        description="A unique identifier if a model contains several items",
    )
    operator_value: OperatorValue = Field(
        default=None,
        title="Operator Value",
        description="The name of the operator we want to apply.",
        validation_alias=AliasChoices("operator_value", "operatorValue"),
    )
    value: Value = Field(default=None, title="Value", description="The filtering value")

    _optional_keys: ClassVar[OptionalKeys] = {
        # be careful, this is a tuple because of the trailing comma
        ("id",),
        ("operatorValue", "operator_value"),
        # be careful, this is a tuple because of the trailing comma
        ("value",),
    }
