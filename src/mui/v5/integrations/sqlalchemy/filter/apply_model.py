"""The apply_model module is responsible for applying a GridSortModel to a query."""

from typing import TypeVar

from sqlalchemy.orm import Query

from mui.v5.grid import GridFilterModel
from mui.v5.integrations.sqlalchemy.filter.apply_items import (
    apply_filter_items_to_query_from_items,
)
from mui.v5.integrations.sqlalchemy.resolver import Resolver

_Q = TypeVar("_Q")


def apply_filter_to_query_from_model(
    query: "Query[_Q]", model: GridFilterModel, resolver: Resolver
) -> "Query[_Q]":
    """Applies a GridFilterModel to a SQLAlchemy query.

    If the model is an empty list, the query is returned, as-is.

    Args:
        query (Query[_Q]): The query to apply the sort model to.
        model (GridFilterModel): The filter model to apply to the query.
        resolver (Resolver): The resolver is responsible for retrieving the column or
            other property on a SQLAlchemy model.

    Returns:
        Query[_Q]: The filtered query.
    """
    query = apply_filter_items_to_query_from_items(
        query=query, model=model, resolver=resolver
    )
    return query
