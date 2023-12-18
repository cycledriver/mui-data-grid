"""The item module contains the representations of a grid filter model's individual
filter items.

Each filter item corresponds to a configured filter from the data grid's filter window.
"""

from typing import Any, ClassVar, Optional, Union

from pydantic import Field as PydanticField
from typing_extensions import TypeAlias, TypedDict

from mui.v6.grid.base import GridBaseModel, OptionalKeys

Id: TypeAlias = Optional[Union[int, str]]
Field: TypeAlias = str
# https://mui.com/x/react-data-grid/filtering/#customize-the-operators
Value: TypeAlias = Optional[Any]
# https://mui.com/x/api/data-grid/grid-filter-operator/
Operator: TypeAlias = str


class GridFilterItemDict(TypedDict):
    """The dictionary representation of a valid snake case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-item/

    Attributes:
        column_field (str): The column from which we want to filter the rows.
        id (str | int | not set): Must be unique. Only useful when the model contains
            several items.
        operator_value (str | None): The name of the operator we want to
            apply. Will become required on @mui/x-data-grid@6.X.
        value: (Any | None | not set): The filtering value.
            The operator filtering function will decide for each row if the row values
            is correct compared to this value.
    """

    id: Id
    field: Field
    value: Value
    operator: Operator


class GridFilterItem(GridBaseModel):
    """A grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-item/

    Attributes:
        id (str | int | not set): Must be unique. Only useful when the model contains
            several items.
        field (str): The column from which we want to filter the rows.
        operator (str): The name of the operator we want to
            apply. This is a string value because Material-UI supports
            arbitrary / custom operators.
        operator: (Any | None | not set): The filtering value.
            The operator filtering function will decide for each row if the row values
            is correct compared to this value.
    """

    id: Id = PydanticField(
        default=None,
        title="Identifier",
        description="A unique identifier if a model contains several items",
    )
    field: Field = PydanticField(
        default=...,
        title="Field",
        description="The column from which we want to filter the rows.",
    )
    operator: Operator = PydanticField(
        default=...,
        title="Operator Value",
        description="The name of the operator we want to apply.",
    )
    value: Value = PydanticField(
        default=None, title="Value", description="The filtering value"
    )

    _optional_keys: ClassVar[OptionalKeys] = {
        # be careful, this is a tuple because of the trailing comma
        ("id",),
        # be careful, this is a tuple because of the trailing comma
        ("value",),
    }
