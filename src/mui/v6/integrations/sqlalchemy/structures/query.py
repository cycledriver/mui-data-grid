"""The query module contains the DataGridQuery data structure.

This structure is used to provide helpers related to pagination, such as
total row counts.
"""

from math import ceil
from typing import Generic, List, Optional, TypeVar, Union, overload

from sqlalchemy.orm import Query

from mui.v6.grid import GridFilterModel, GridPaginationModel, GridSortModel
from mui.v6.integrations.sqlalchemy.filter import apply_filter_to_query_from_model
from mui.v6.integrations.sqlalchemy.pagination import (
    apply_limit_offset_to_query_from_model,
)
from mui.v6.integrations.sqlalchemy.resolver import Resolver
from mui.v6.integrations.sqlalchemy.sort import apply_sort_to_query_from_model
from mui.v6.integrations.sqlalchemy.structures.factory import Factory

_T = TypeVar("_T")
_R = TypeVar("_R")


class DataGridQuery(Generic[_T]):
    """A data grid query handles utilities related to our query.

    Args:
        Generic (_type_): The model being retrieved by the query.
    """

    _query: "Query[_T]"
    column_resovler: Resolver
    filter_model: Optional[GridFilterModel]
    pagination_model: Optional[GridPaginationModel]
    query: "Query[_T]"
    sort_model: Optional[GridSortModel]

    def __init__(  # noqa: PLR0917
        self,
        query: "Query[_T]",
        column_resolver: Resolver,
        filter_model: Optional[GridFilterModel] = None,
        sort_model: Optional[GridSortModel] = None,
        pagination_model: Optional[GridPaginationModel] = None,
    ) -> None:
        """Initialize a new data grid query.

        Args:
            query (Query[_T]): The base query which the models will be applied to.
            column_resolver (Resolver): The field resolver which converts a UI field
                to the corresponding SQLAlchemy column, column property, etc.
            filter_model (Optional[GridFilterModel], optional): The filter model to
                apply, if provided. Defaults to None.
            sort_model (Optional[GridSortModel], optional): The sort model to apply,
                if provided. Defaults to None.
            pagination_model (Optional[GridPaginationModel], optional): The pagination
                model to apply, if provided. Defaults to None.
        """
        self.column_resovler = column_resolver
        self.filter_model = filter_model
        self.sort_model = sort_model
        self.pagination_model = pagination_model
        query = self._filter_query(query=query)
        # we filter it first, so that our total is accurate
        self._query = query
        # then we apply the order and pagination limits
        query = self._order_query(query=query)
        query = self._paginate_query(query=query)
        self.query = query

    def _filter_query(self, query: "Query[_T]") -> "Query[_T]":
        """Applies the filter model to the query.

        Args:
            query (Query[_T]): The query being filtered.

        Returns:
            Query[_T]: The filtered query.
        """
        if self.filter_model is None:
            return query
        return apply_filter_to_query_from_model(
            query=query, model=self.filter_model, resolver=self.column_resovler
        )

    def _order_query(self, query: "Query[_T]") -> "Query[_T]":
        """Applies the sort model to the query.

        Args:
            query (Query[_T]): The query being ordered / sorted.

        Returns:
            Query[_T]: The sorted / ordered query.
        """
        if self.sort_model is None:
            return query
        return apply_sort_to_query_from_model(
            query=query, model=self.sort_model, resolver=self.column_resovler
        )

    def _paginate_query(self, query: "Query[_T]") -> "Query[_T]":
        """Applies the pagination model to the query.

        Args:
            query (Query[_T]): The query being paginated (limit / offset).

        Returns:
            Query[_T]: The paginated (limited) query.
        """
        if self.pagination_model is None:
            return query
        return apply_limit_offset_to_query_from_model(
            query=query, model=self.pagination_model
        )

    def total(self) -> int:
        """Returns the total number of rows that exist with the filter.

        This disables ordering (sorting) to improve performance.

        Returns:
            int: The count of total items before pagination, but after filtering.
        """
        return self._query.order_by(None).count()

    @property
    def per_page(self) -> int:
        """Alias for page_size."""
        return self.page_size

    @property
    def page_size(self) -> int:
        """Returns the page size.

        Returns:
            int: 0 if no pagination model exists, otherwise the page size.
        """
        return self.pagination_model.page_size if self.pagination_model else 0

    @overload
    def items(self, factory: None = ...) -> List[_T]:
        """When a factory function is not provided, simply return the models.

        Args:
            factory (None, optional): This is not provided. Defaults to None.

        Returns:
            List[_T]: The list of models, without conversion.
        """

    @overload
    def items(self, factory: Factory[_T, _R]) -> List[_R]:
        """When a factory function is provided, return a list of items created by
        the factory.

        Args:
            factory (Callable[[_T], _R]): The factory to convert the type(s).

        Returns:
            List[_R]: The list of created items.
        """

    def items(
        self, factory: Optional[Factory[_T, _R]] = None
    ) -> Union[List[_T], List[_R]]:
        """Returns all results of the query, after all models have been applied.

        Args:
            factory (Optional[Callable[[_T], _R]]): The factory function to convert the
                model into a different type.

        Returns:
            List[_T]: The list of individual items located by the query after all
                models have been applied.
        """
        items = self.query.all()
        return [factory(item) for item in items] if factory is not None else items

    def pages(self, total: Optional[int] = None) -> int:
        """Returns the number of pages to display all results.

        Args:
            total (Optional[int], optional): The total number of results. This may
                be provided to avoid the overhead of an additional database query to
                retrieve the total. Defaults to None.

        Returns:
            int: The number of pages required to display all results at the current
                page size.
        """
        if not total:
            total = self.total()
        return int(ceil(total / float(self.per_page)))

    @property
    def page(self) -> int:
        """Returns the current page number.

        Returns:
            int: 0 if no pagination model exists, otherwise the page number.
        """
        return self.pagination_model.page if self.pagination_model else 0
