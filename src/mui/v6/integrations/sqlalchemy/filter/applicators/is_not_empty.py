"""The is_not_empty applicator applies the isNotEmpty operator to the data.

isNotEmpty equates to IS NOT NULL comparisons
"""
from operator import ne
from typing import Any


def apply_is_not_empty_operator(column: Any) -> Any:
    """Handles applying the isNotEmpty x-data-grid operator to a column.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the isNotEmpty filter using the provided value.
    """
    return ne(column, None)
