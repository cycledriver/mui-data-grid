"""The apply_model module applies a GridPaginationModel to a query."""

from typing import TypeVar

from sqlalchemy.orm import Query

from mui.v5.grid import GridPaginationModel

T = TypeVar("T")


def apply_limit_offset_to_query_from_model(
    query: "Query[T]", model: GridPaginationModel
) -> "Query[T]":
    """Applies the limit and offset to a SQLAlchemy query from a pagination model.

    Args:
        query (Query[T]): The SQLAlchemy query to apply the pagination model to.
        model (GridPaginationModel): The GridPaginationModel to apply to the query.

    Returns:
        Query[T]: The SQLAlchemy query which has had the limit and offset applied.
    """
    return query.limit(model.page_size).offset(model.offset)
