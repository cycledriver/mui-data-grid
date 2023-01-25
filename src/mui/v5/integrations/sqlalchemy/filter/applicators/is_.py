"""The is_ applicator applies the is operator to the data.

Meant as an equality check.
"""
from datetime import datetime
from operator import eq
from typing import Any

from sqlalchemy import Date, DateTime, Time


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
    # TODO: convert to column.type.python_type like isNot
    if isinstance(column.type, (DateTime, Time, Date)) and value is not None:
        return eq(column, datetime.fromisoformat(value))
    else:
        return eq(column, value)
