"""The is not applicator applies the is not operator to the data.
"""

from datetime import date, datetime, time
from operator import ne
from typing import Any


def apply_not_operator(column: Any, value: Any) -> Any:
    """Handles applying the not x-data-grid operator to a column.

    The not operator exists on enum selections as well as datetimes. Care
    needs to be given as a result.

    Args:
        column (Any): The column the operator is being applied to, or equivalent
            property, expression, subquery, etc.
        value (Any): The value being filtered.

    Returns:
        Any: The column after applying the is filter using the provided value.
    """
    if column.type.python_type in {datetime, time, date} and value is not None:
        return ne(column, datetime.fromisoformat(value))
    return ne(column, value)
