"""The model module contains the grid filter model.

The grid filter model is responsible for modelling, or representing using
programming data structures, the state of the data grid.
"""

from typing import Any, ClassVar, List, Optional, Union

from pydantic import AliasChoices, Field
from typing_extensions import TypeAlias, TypedDict

from mui.v5.grid.base import GridBaseModel, OptionalKeys
from mui.v5.grid.filter.item import GridFilterItem, GridFilterItemDict
from mui.v5.grid.link.operator import GridLinkOperator, GridLinkOperatorLiterals

# type aliases require the use of `Optional` instead of `|` for use at
# runtime in Pydantic
# we provide copies of the literals for the tests package and for wrapping this
# library, they should not be used in pydantic models, generally speaking.
ItemsLiterals: TypeAlias = List[GridFilterItemDict]
Items: TypeAlias = List[GridFilterItem]

LinkOperatorLiterals: TypeAlias = Optional[GridLinkOperatorLiterals]
LinkOperator: TypeAlias = Optional[GridLinkOperator]

QuickFilterLogicOperatorLiterals: TypeAlias = Optional[GridLinkOperatorLiterals]
QuickFilterLogicOperator: TypeAlias = Optional[GridLinkOperator]

QuickFilterValues: TypeAlias = Optional[List[Any]]


class SnakeCaseGridFilterModelDict(TypedDict):
    """The dictionary representation of a valid snake case grid filter item.

    Documentation:
        https://mui.com/x/api/data-grid/grid-filter-model/

    Attributes:
        items (list[GridFilterItem]): The individual filters.
        link_operator (GridLinkOperator | "and" | "or" | None | not set):
            - "and": the row must pass all the filter items.
            - "or": the row must pass at least one filter item.
            - GridLinkOperator.And: the row must pass all the filter items.
            - GridLinkOperator.Or: the row must pass at least one filter item.
            - Alias: linkOperator
        quick_filter_logic_operator (GridLinkOperator | "and" | "or" | None | not set):
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
    link_operator: Union[LinkOperatorLiterals, LinkOperator]
    quick_filter_logic_operator: Union[
        QuickFilterLogicOperatorLiterals, QuickFilterLogicOperator
    ]
    quick_filter_values: QuickFilterValues


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
    linkOperator: Union[LinkOperatorLiterals, LinkOperator]
    quickFilterLogicOperator: Union[
        QuickFilterLogicOperatorLiterals, QuickFilterLogicOperator
    ]
    quickFilterValues: QuickFilterValues


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
        link_operator (GridLinkOperator | None | not set):
            - GridLinkOperator.And: the row must pass all the filter items.
            - GridLinkOperator.Or: the row must pass at least on filter item.
            - Alias: linkOperator
        quick_filter_logic_operator (GridLinkOperator | None | not set):
            - GridLinkOperator.And: the row must pass all the values.
            - GridLinkOperator.Or: the row must pass at least one value.
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
    link_operator: LinkOperator = Field(
        default=None,
        title="Link Operator",
        description="Whether the row row must pass all filter items.",
        validation_alias=AliasChoices("link_operator", "linkOperator"),
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
        ("linkOperator", "link_operator"),
        ("quickFilterLogicOperator", "quick_filter_logic_operator"),
        ("quickFilterValues", "quick_filter_values"),
    }
