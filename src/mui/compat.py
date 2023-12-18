"""The compat module is a compatibility module for backporting future features."""

from enum import Enum
from typing import Any, List, Tuple


class StrEnum(str, Enum):
    """Enum where members are also (and must be) strings

    Backport of Python 3.11 feature

    Taken at:
    https://github.com/python/cpython/blob/b44372e03c5461b6ad3d89763a9eb6cb82df07a4/Lib/enum.py#L1221

    Future?:
    https://github.com/python/cpython/blob/main/Lib/enum.py#L1221
    """

    def __new__(cls, *values: Tuple[str, ...]) -> "StrEnum":
        "values must already be of type `str`"
        if len(values) > 3:  # noqa: PLR2004
            raise TypeError(f"too many arguments for str(): {values!r}")
        if len(values) == 1 and not isinstance(values[0], str):
            raise TypeError(f"{values[0]!r} is not a string")
        if len(values) >= 2 and not isinstance(values[1], str):  # noqa: PLR2004
            raise TypeError(f"encoding must be a string, not {values[1]!r}")
        if len(values) == 3 and not isinstance(values[2], str):  # noqa: PLR2004
            raise TypeError(f"errors must be a string, not {values[2]!r}")
        value = str(*values)
        member = str.__new__(cls, value)
        member._value_ = value
        return member

    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,  # noqa: ARG004
        count: int,  # noqa: ARG004
        last_values: List[Any],  # noqa: ARG004
    ) -> Any:
        """Return the lower-cased version of the member name."""
        return name.lower()
