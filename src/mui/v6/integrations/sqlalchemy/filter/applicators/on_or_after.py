"""The is on or after applicator applies the is on or after operator to the data.
"""
from datetime import datetime
from operator import ge
from typing import Any


def apply_on_or_after_operator(column: Any, value: Any) -> Any:
    """Handles applying the on or after x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the on or after filter using the provided value.
    """
    # if the column is on or after the received date, it will be greater than or equal
    # to the received date
    return ge(column, datetime.fromisoformat(value)) if value is not None else column
