"""The apply_model module is responsible for applying a GridSortModel to a query."""

from typing import Any, Callable, TypeVar

from sqlalchemy import and_, or_
from sqlalchemy.orm import Query

from mui.v6.grid import GridFilterItem, GridFilterModel, GridLogicOperator
from mui.v6.integrations.sqlalchemy.filter.applicators import (
    SUPPORTED_BASIC_OPERATORS,
    apply_after_operator,
    apply_basic_operator,
    apply_before_operator,
    apply_contains_operator,
    apply_endswith_operator,
    apply_is_any_of_operator,
    apply_is_empty_operator,
    apply_is_not_empty_operator,
    apply_is_operator,
    apply_not_operator,
    apply_on_or_after_operator,
    apply_on_or_before_operator,
    apply_startswith_operator,
)
from mui.v6.integrations.sqlalchemy.resolver import Resolver

_Q = TypeVar("_Q")


def _get_link_operator(
    model: GridFilterModel,
) -> Callable[[Any], Any]:
    """Retrieves the correct filter operator for a model.

    If the link operator is None, `AND` is used by default.

    Args:
        model (GridFilterModel): The grid filter model which is being applied to the
            SQLAlchemy query.

    Returns SQLAlchemy V14:

        Callable[[Any], BooleanClauseList[Any]]: The `or_` and `and_` operators for
            application to SQLAlchemy filters.

    Returns SQLAlchemy V2+:
        Callable[[Any], ColumnElement[bool]]: The `or_` and `and_` operators for
            application to SQLAlchemy filters.
    """
    if model.logic_operator is None or model.logic_operator == GridLogicOperator.And:
        return and_
    else:
        return or_


def apply_operator_to_column(item: GridFilterItem, resolver: Resolver) -> Any:
    """Applies the operator value represented by the GridFilterItem to the column.

    This function uses the provided resolver to retrieve the SQLAlchemy's column, or
    other filterable expression, and applies the appropriate SQLAlchemy or Python
    operator.

    This does not currently support custom operators.

    Support:
        * Equal to
            * =
            * ==
            * eq
            * equals
            * is
                * DateTime aware
                * Not Time, Date, or other temporal type aware.
        * Not equal to
            * !=
            * ne
        * Greater than
            * >
            * gt
        * Less than
            * <
            * lt
        * Greater than or equal to
            * >=
            * ge
        * Less than or equal to
            * <=
            * le
        * isEmpty (`IS NULL` query)
        * isNotEmpty (`IS NOT NULL` clause)
        * isAnyOf (`IN [?, ?, ?]` clause)
        * contains (`'%' || ? || '%'` clause)
        * startsWith (`? || '%'` clause)
        * endsWith (`'%' || ?` clause)

    Args:
        item (GridFilterItem): The item being applied to the column.
        resolver (Resolver): The resolver to use to locate the column or
            filterable expression.

    Returns:
        Any: The comparison operator for use in SQLAlchemy queries.
    """
    column = resolver(item.field)
    # we have 1:1 mappings of these operators in Python
    if item.operator in SUPPORTED_BASIC_OPERATORS:
        return apply_basic_operator(column, item)
    elif item.operator == "is":
        return apply_is_operator(column, item.value)
    elif item.operator == "isEmpty":
        return apply_is_empty_operator(column)
    elif item.operator == "isNotEmpty":
        return apply_is_not_empty_operator(column)
    elif item.operator == "isAnyOf":
        return apply_is_any_of_operator(column, item.value)
    elif item.operator == "contains":
        return apply_contains_operator(column, item.value)
    elif item.operator == "startsWith":
        return apply_startswith_operator(column, item.value)
    elif item.operator == "endsWith":
        return apply_endswith_operator(column, item.value)
    elif item.operator == "not":
        return apply_not_operator(column, item.value)
    elif item.operator == "before":
        return apply_before_operator(column, item.value)
    elif item.operator == "after":
        return apply_after_operator(column, item.value)
    elif item.operator == "onOrBefore":
        return apply_on_or_before_operator(column, item.value)
    elif item.operator == "onOrAfter":
        return apply_on_or_after_operator(column, item.value)
    else:
        raise ValueError(f"Unsupported operator {item.operator}")


def apply_filter_items_to_query_from_items(
    query: "Query[_Q]", model: GridFilterModel, resolver: Resolver
) -> "Query[_Q]":
    """Applies a grid filter model's items section to a SQLAlchemy query.

    Args:
        query (Query[_Q]): The query to be filtered.
        model (GridFilterModel): The filter model being applied.
        resolver (Resolver): A resolver to convert field names from the model to
            SQLAlchemy column's or expressions.

    Returns:
        Query[_Q]: The filtered query.
    """
    if len(model.items) == 0:
        return query

    link_operator = _get_link_operator(model=model)
    # this is a bit gross, but is the easiest way to ensure it's applied properly
    return query.filter(
        # the link operator is either the and_ or or_ sqlalchemy function to determine
        # how the boolean clause list is applied
        link_operator(
            # the get_operator_value returns a function which we immediately call.
            # The function is a comparison function supported by SQLAlchemy such as
            # eq, ne, le, lt, etc. which is applied to the model's resolved column
            # and the filter value.
            # Basically, it builds something like this, dynamically:
            # .filter(and_(gt(Request.id, 100), eq(Request.title, "Example"))
            *[
                apply_operator_to_column(item=item, resolver=resolver)
                for item in model.items
            ]
        )
    )
