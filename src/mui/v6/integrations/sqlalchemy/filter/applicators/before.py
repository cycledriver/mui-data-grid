"""The is before applicator applies the is before operator to the data.
"""
from datetime import datetime
from operator import lt
from typing import Any


def apply_before_operator(column: Any, value: Any) -> Any:
    """Handles applying the before x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the before filter using the provided value.
    """
    # if the column is before the received date, it will be less than the
    # received date
    return lt(column, datetime.fromisoformat(value)) if value is not None else column
