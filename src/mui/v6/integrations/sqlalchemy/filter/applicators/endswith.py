"""The endswith applicator applies the endsWith method to the data.

endsWith is meant as in "Jonathan" ends with "than".
"""
from typing import Any


def apply_endswith_operator(column: Any, value: Any) -> Any:
    """Handles applying the endsWith x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the is any of filter using the provided value.
    """
    # https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.endswith # noqa
    # Per SQLAlchemy 1.4.43:
    # only '=', '!=', 'is_()', 'is_not()', 'is_distinct_from()',
    # 'is_not_distinct_from()' operators can be used with None/True/False
    # so below have to special case them.
    if value is None:
        return column.endswith("")
    return column.endswith(value)
