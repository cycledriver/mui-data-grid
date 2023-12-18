"""The apply_model module is responsible for applying a GridSortModel to a query."""

from typing import TypeVar

from sqlalchemy.orm import Query

from mui.v6.grid.sort import GridSortModel
from mui.v6.integrations.sqlalchemy.resolver import Resolver
from mui.v6.integrations.sqlalchemy.sort.apply_item import get_sort_expression_from_item

_Q = TypeVar("_Q")


def apply_sort_to_query_from_model(
    query: "Query[_Q]", model: GridSortModel, resolver: Resolver
) -> "Query[_Q]":
    """Applies a GridSortModel to a SQLAlchemy query.

    If the model is an empty list, the query is returned, as-is.

    Args:
        query (Query[_Q]): The query to apply the sort model to.
        model (GridSortModel): The sort model to apply to the query. This contains zero
            or more GridSortItems.
        resolver (Resolver): The resolver is responsible for retrieving the column or
            other property on a SQLAlchemy model.

    Returns:
        Query[_Q]: The ordered query.
    """
    if len(model) == 0:
        return query

    query = query.order_by(
        # But, since this doesn't accept lists or kwargs, we unpack the list's values
        # using the splat (*) operator.
        #
        # Example:
        # >>> def print_each(*args: int) -> None:
        # ...     for arg in args:
        # ...         print(arg)
        # ...
        # >>> l = [1, 2, 3]
        # >>> print_each(*l)
        # 1
        # 2
        # 3
        *[
            get_sort_expression_from_item(item=item, resolver=resolver)
            for item in model
            # if we don't skip item.sort None here, multiple order bys will cause
            # an ORDER BY NULL, NULL clause instead of skipping the ORDER BY
            if item.sort is not None
        ]
    )
    return query
