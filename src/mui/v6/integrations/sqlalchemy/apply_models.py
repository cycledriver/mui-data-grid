"""The apply_models module is used to apply the X-Data-Grid state models, such as the
GridFilterModel, GridSortModel, and GridPaginationModel to a SQLAlchemy ORM query.
"""

from typing import Optional, TypeVar

from sqlalchemy.orm import Query

from mui.v6.grid import (
    GridFilterModel,
    GridPaginationModel,
    GridSortModel,
    RequestGridModels,
)
from mui.v6.integrations.sqlalchemy.resolver import Resolver
from mui.v6.integrations.sqlalchemy.structures import DataGridQuery

T = TypeVar("T")


def apply_request_grid_models_to_query(
    query: "Query[T]",
    request_model: RequestGridModels,
    column_resolver: Resolver,
) -> "DataGridQuery[T]":
    """Applies a RequestGridModels object to a query.

    This is a utility function to ensure that the models are applied in a SQLAlchemy
    compatible order.

    Args:
        query (Query[T]): The base query which will be filtered, ordered,
            and paginated.
        request_model (RequestGridModels): The X-Data-Grid state models being applied
            to the query.
        column_resolver (Resolver): The resolver responsible for taking an X-Data-Grid
            field name (from the UI configuration) and resolving it to the appropriate
            SQLAlchemy model column.

    Returns:
        Query[T]: The query, after it's paginated, ordered, and paginated. The caller
            should call the .all(), .first(), .count(), or other method to retrieve the
            final result(s).
    """
    return apply_data_grid_models_to_query(
        query=query,
        column_resolver=column_resolver,
        filter_model=request_model.filter_model,
        sort_model=request_model.sort_model,
        pagination_model=request_model.pagination_model,
    )


def apply_data_grid_models_to_query(
    query: "Query[T]",
    column_resolver: Resolver,
    filter_model: Optional[GridFilterModel] = None,
    sort_model: Optional[GridSortModel] = None,
    pagination_model: Optional[GridPaginationModel] = None,
) -> "DataGridQuery[T]":
    """Applies the provided X-Data-Grid state models to the SQLAlchemy ORM Query.

    This method is provided to allow for implementing support for only specific
    server-side features rather than the trio of filter, sort, and pagination.

    Args:
        query (Query[T]): The base query which will be filtered, ordered,
            and paginated.
        column_resolver (Resolver): The resolver responsible for taking an X-Data-Grid
            field name (from the UI configuration) and resolving it to the appropriate
            SQLAlchemy model column.
        filter_model (Optional[GridFilterModel], optional): The filter model to apply
            to the query. If None, this stage will be skipped. Defaults to None.
        sort_model (Optional[GridSortModel], optional): The sort model to apply to the
            query. If None, this stage will be skipped. Defaults to None.
        pagination_model (Optional[GridPaginationModel], optional): The pagination
            model to apply to the query. If None, this stage will be skipped.
            Defaults to None.

    Returns:
        Query[T]: The query, with the filter, sort, and/or pagination models applied.
    """
    return DataGridQuery[T](
        query=query,
        column_resolver=column_resolver,
        filter_model=filter_model,
        sort_model=sort_model,
        pagination_model=pagination_model,
    )
