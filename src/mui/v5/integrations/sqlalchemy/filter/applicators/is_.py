"""The is_ applicator applies the is operator to the data.

Meant as an equality check.
"""
from datetime import datetime, date, time
from operator import eq
from typing import Any


def apply_is_operator(column: Any, value: Any) -> Any:
    """Handles applying the is x-data-grid operator to a column.

    The is operator requires special handling when differentiating between data
    types.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the is filter using the provided value.
    """
    if column.type.python_type in {datetime, time, date} and value is not None:
        return eq(column, datetime.fromisoformat(value))
    return eq(column, value)
