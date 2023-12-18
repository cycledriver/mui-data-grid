"""The apply_item module is responsible for building the item's UnaryExpression."""

from typing import Any, Callable, Optional

from sqlalchemy import asc, desc
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.types import NullType

from mui.v6.grid.sort import GridSortDirection
from mui.v6.grid.sort.item import GridSortItem
from mui.v6.integrations.sqlalchemy.resolver import Resolver


def _no_operation(column: Any) -> None:  # noqa: ARG001
    """Used when an unsorted operation is requested.

    Returns:
        None
    """
    return None


def get_operator(
    item: GridSortItem,
) -> Callable[[Any], Optional[UnaryExpression[NullType]]]:
    """Retrieves the correct sort operator for an item.

    Args:
        item (GridSortItem): The grid sort item to retrieve the sort direction from.

    Returns:
        Callable[[Any], UnaryExpression[NullType]]: The `asc` or `desc` operator from
            SQLAlchemy. `desc` when the direction is None (default value) or
            GridSortDirection.DESC, otherwise `asc`.
    """
    if item.sort is None:
        return _no_operation
    elif item.sort == GridSortDirection.DESC:
        return desc
    else:
        return asc


def _get_column(item: GridSortItem, resolver: Resolver) -> Any:
    """Retrieves the column or appropriate property to order by.

    This is typed as `Any` for the return because that's how desc and asc are typed.
    They accept more than just `Column[_C]` types though, such as deferred and
    column_property.

    https://stackoverflow.com/questions/19569448/sqlalchemy-order-by-a-relationship-field-in-a-relationship

    Args:
        item (GridSortItem): The grid sort item whose field will be retrieved using
            the resolver.
        resolver (Resolver): The resolver is responsible for retrieving the column or
            other property on a SQLAlchemy model, indicated by the resolver.

    Returns:
        Any: The column, property, or other allowed attribute representing an orderable
            column.
    """
    return resolver(item.field)


def get_sort_expression_from_item(
    item: GridSortItem, resolver: Resolver
) -> Optional[UnaryExpression[NullType]]:
    """Resolves the operator and column, returning the generated unary expression.

    This is meant to be used within an order_by call in SQLAlchemy:
        paginated_query = query.order_by(
            get_sort_expression_from_item(item, resolver)
            for item in grid_sort_model
        )

    This is to prevent early evaluation which can fail.

    Args:
        item (GridSortItem): The grid sort item to generate a unary expression for.
        resolver (Resolver): The resolver is responsible for retrieving the column or
            other property on a SQLAlchemy model, indicated by the resolver.

    Returns:
        UnaryExpression[NullType]: _description_
    """
    operator = get_operator(item=item)
    column = _get_column(item=item, resolver=resolver)
    return operator(column)
