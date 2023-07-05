"""The is_empty applicator applies the isEmpty operator to the data.

isEmpty equates to IS NULL comparisons
"""
from operator import eq
from typing import Any


def apply_is_empty_operator(column: Any) -> Any:
    """Handles applying the isEmpty x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the isEmpty filter using the provided value.
    """
    return eq(column, None)
