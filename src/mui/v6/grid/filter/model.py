"""The model module contains the grid filter model.

The grid filter model is responsible for modelling, or representing using
programming data structures, the state of the data grid.
"""

from typing import Any, ClassVar, List, Optional, Union

from pydantic import AliasChoices, Field
from typing_extensions import TypeAlias, TypedDict

from mui.v6.grid.base import GridBaseModel, OptionalKeys
from mui.v6.grid.filter.item import GridFilterItem, GridFilterItemDict
from mui.v6.grid.logic.operator import GridLogicOperator, GridLogicOperatorLiterals

# type aliases require the use of `Optional` instead of `|` for use at
# runtime in Pydantic
# we provide copies of the literals for the tests package and for wrapping this
# library, they should not be used in pydantic models, generally speaking.
ItemsLiterals: TypeAlias = List[GridFilterItemDict]
Items: TypeAlias = List[GridFilterItem]

LogicOperatorLiterals: TypeAlias = Optional[GridLogicOperatorLiterals]
LogicOperator: TypeAlias = Optional[GridLogicOperator]

QuickFilterLogicOperatorLiterals: TypeAlias = Optional[GridLogicOperatorLiterals]
QuickFilterLogicOperator: TypeAlias = Optional[GridLogicOperator]

QuickFilterValues: TypeAlias = Optional[List[Any]]


class SnakeCaseGridFilterModelDict(TypedDict):
    """The dictionary representation of a valid snake case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-model/

    Attributes:
        items (list[GridFilterItem]): The individual filters.
        logic_operator (GridLogicOperator | "and" | "or" | None | not set):
            - "and": the row must pass all the filter items.
            - "or": the row must pass at least one filter item.
            - GridLogicOperator.And: the row must pass all the filter items.
            - GridLogicOperator.Or: the row must pass at least one filter item.
            - Alias: logicOperator
        quick_filter_logic_operator (GridLogicOperator | "and" | "or" | None | not set):
            - "and": the row must pass all the values.
            - "or": the row must pass at least one value.
            - GridLinkOperator.And: the row must pass all the values.
            - GridLinkOperator.Or: the row must pass at least one value.
            - Alias: quickFilteringLogicOperator
        quick_filter_values (list[Any] | None | not set): values used to quick
            filter rows.
            - Alias: quickFilterValues
    """

    items: Union[ItemsLiterals, Items]
    logic_operator: Union[LogicOperatorLiterals, LogicOperator]
    quick_filter_values: QuickFilterValues
    quick_filter_logic_operator: Union[
        QuickFilterLogicOperatorLiterals, QuickFilterLogicOperator
    ]


class CamelCaseGridFilterModelDict(TypedDict):
    """The dictionary representation of a valid camel case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-model/

    Attributes:
        items (list[GridFilterItem]): The individual filters.
        linkOperator (GridLinkOperator | "and" | "or" | None | not set):
            - "and": the row must pass all the filter items.
            - "or": the row must pass at least one filter item.
            - GridLinkOperator.And: the row must pass all the filter items.
            - GridLinkOperator.Or: the row must pass at least one filter item.
            - Alias: linkOperator
        quickFilterLogicOperator (GridLinkOperator | "and" | "or" | None | not set):
            - "and": the row must pass all the values.
            - "or": the row must pass at least one value.
            - GridLinkOperator.And: the row must pass all the values.
            - GridLinkOperator.Or: the row must pass at least one value.
            - Alias: quickFilteringLogicOperator
        quickFilterValues (list[Any] | None | not set): values used to quick
            filter rows.
            - Alias: quickFilterValues
    """

    items: Union[ItemsLiterals, Items]
    logicOperator: Union[LogicOperatorLiterals, LogicOperator]
    quickFilterValues: QuickFilterValues
    quickFilterLogicOperator: Union[
        QuickFilterLogicOperatorLiterals, QuickFilterLogicOperator
    ]


"""The GridFilterModelDict is an alias for either a snake or camel case grid
filter model.

Both formats are supported by the GridFilterModel model.
"""
GridFilterModelDict: TypeAlias = Union[
    SnakeCaseGridFilterModelDict, CamelCaseGridFilterModelDict
]


class GridFilterModel(GridBaseModel):
    """A grid filter model.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-model/

    Attributes:
        items (list[GridFilterItem]): The individual filters.
        logic_operator (GridLogicOperator | None | not set):
            - GridLogicOperator.And: the row must pass all the filter items.
            - GridLogicOperator.Or: the row must pass at least on filter item.
            - Alias: logicOperator
        quick_filter_logic_operator (GridLogicOperator | None | not set):
            - GridLogicOperator.And: the row must pass all the values.
            - GridLogicOperator.Or: the row must pass at least one value.
            - Alias: quickFilteringLogicOperator
        quick_filter_values (list[Any] | None | not set): values used to quick
            filter rows.
            - Alias: quickFilterValues
    """

    items: Items = Field(
        default_factory=list,
        title="Items",
        description="The individual filters to apply",
    )
    logic_operator: LogicOperator = Field(
        default=None,
        title="Logic Operator",
        description="Whether the row row must pass all filter items.",
        validation_alias=AliasChoices("logic_operator", "logicOperator"),
    )
    quick_filter_logic_operator: QuickFilterLogicOperator = Field(
        default=None,
        title="Quick Filter Logic Operator",
        description="Whether the row must pass all values or at least one value.",
        validation_alias=AliasChoices(
            "quick_filter_logic_operator", "quickFilterLogicOperator"
        ),
    )
    quick_filter_values: QuickFilterValues = Field(
        default=None,
        title="Quick Filter Values",
        description="Values used to quick filter rows.",
        validation_alias=AliasChoices("quick_filter_values", "quickFilterValues"),
    )

    _optional_keys: ClassVar[OptionalKeys] = {
        ("logicOperator", "logic_operator"),
        ("quickFilterLogicOperator", "quick_filter_logic_operator"),
        ("quickFilterValues", "quick_filter_values"),
    }
