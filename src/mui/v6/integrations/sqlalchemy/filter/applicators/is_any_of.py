"""The is_any_of applicator applies the isAnyOf operator to the data.

isAnyOf as in "Jonathan" is any of ["Aubrey", "Jasmine", "Jonathan"]
"""
from typing import Any, Collection, cast


def apply_is_any_of_operator(column: Any, value: Any) -> Any:
    """Handles applying the isAnyOf x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the isAnyOf filter using the provided value.
    """
    # https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.in_ # noqa
    # Per SQLAlchemy 1.4.43:
    # only '=', '!=', 'is_()', 'is_not()', 'is_distinct_from()',
    # 'is_not_distinct_from()' operators can be used with None/True/False
    # so below have to special case them.
    if value is None or (
        isinstance(value, Collection) and len(cast(Collection[object], value)) == 0
    ):
        return column.in_(tuple())
    return column.in_(value)
