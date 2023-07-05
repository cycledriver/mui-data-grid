"""The startswith applicator applies the startsWith method to the data.

startsWith is meant as in "Jonathan" ends with "Jon".
"""
from typing import Any


def apply_startswith_operator(column: Any, value: Any) -> Any:
    """Handles applying the startsWith x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the startsWith filter using the provided value.
    """
    # https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.startswith # noqa
    # Per SQLAlchemy 1.4.43:
    # only '=', '!=', 'is_()', 'is_not()', 'is_distinct_from()',
    # 'is_not_distinct_from()' operators can be used with None/True/False
    # so below have to special case them.
    if value is None:
        return column.startswith("")
    return column.startswith(value)
