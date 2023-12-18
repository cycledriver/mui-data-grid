"""The operator module is responsible for containing the GridLinkOperator enum."""

from enum import unique

from typing_extensions import Literal, TypeAlias

from mui.compat import StrEnum

GridLinkOperatorLiterals: TypeAlias = Literal["and", "or"]


@unique
class GridLinkOperator(StrEnum):
    """A grid link operator is responsible for describing how to link requirements.

    Attributes:
        And: The "and" value implies that refinements should be joined in an "and"
            fashion.
        Or: The "or" value implies that refinements should be joined in an "or" fashion.

    This enumeration most commonly
    """

    And = "and"
    Or = "or"
