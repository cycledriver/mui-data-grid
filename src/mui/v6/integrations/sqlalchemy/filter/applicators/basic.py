"""The basic applicator applies literal operators.

Literal operators are literal representations of a built-in operator.
"""

from operator import eq, ge, gt, le, lt, ne
from typing import Any

from mui.v6.grid import GridFilterItem

EQUAL_OPERATOR_LITERALS = {"==", "=", "equals", "eq"}
NOT_EQUAL_OPERATOR_LITERALS = {"!=", "ne"}
GREATER_THAN_OPERATOR_LITERALS = {">", "gt"}
GREATER_THAN_OR_EQUAL_TO_OPERATOR_LITERALS = {">=", "ge"}
LESS_THAN_OPERATOR_LITERALS = {"<", "lt"}
LESS_THAN_OR_EQUAL_TO_OPERATOR_LITERALS = {"<=", "le"}

SUPPORTED_BASIC_OPERATORS = EQUAL_OPERATOR_LITERALS.union(
    NOT_EQUAL_OPERATOR_LITERALS,
    GREATER_THAN_OPERATOR_LITERALS,
    GREATER_THAN_OR_EQUAL_TO_OPERATOR_LITERALS,
    LESS_THAN_OPERATOR_LITERALS,
    LESS_THAN_OR_EQUAL_TO_OPERATOR_LITERALS,
)


def apply_basic_operator(column: Any, item: GridFilterItem) -> Any:
    """Retrieve the Python operator function from the filter item's operator value.

    As an example, this function converts strings such as "==", "!=", and ">=" to the
    functions operator.eq, operator.ne, operator.ge respectively.

    This has special support for the "equals" operator which is treated as an alias
    for the "==" operator.


    Args:
        item (GridFilterItem): The grid filter item being operated on.

    Raises:
        ValueError: Raised when the operator value is not supported by the integration.

    Returns:
        Callable[[Any, Any], Any]: The operator.
    """
    if item.operator in EQUAL_OPERATOR_LITERALS:
        # equal
        return eq(column, item.value)
    elif item.operator in NOT_EQUAL_OPERATOR_LITERALS:
        # not equal
        return ne(column, item.value)
    elif item.operator in GREATER_THAN_OPERATOR_LITERALS:
        # greater than
        return gt(column, item.value if item.value is not None else 0)
    elif item.operator in GREATER_THAN_OR_EQUAL_TO_OPERATOR_LITERALS:
        # greater than or equal to
        return ge(column, item.value if item.value is not None else 0)
    elif item.operator in LESS_THAN_OPERATOR_LITERALS:
        # greater than
        return lt(column, item.value if item.value is not None else 0)
    elif item.operator in LESS_THAN_OR_EQUAL_TO_OPERATOR_LITERALS:
        # greater than or equal to
        return le(column, item.value if item.value is not None else 0)
    else:
        raise ValueError(f"Unsupported operator {item.operator}")
