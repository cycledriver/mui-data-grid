"""The direction module contains the sort direction enumeration and types."""
from enum import unique

from typing_extensions import Literal, TypeAlias

from mui.compat import StrEnum

GridSortDirectionLiterals: TypeAlias = Literal["asc", "desc"]


@unique
class GridSortDirection(StrEnum):
    """The direction to sort a column.

    export declare type GridSortDirection = 'asc' | 'desc' | null | undefined;
    """

    ASC = "asc"
    DESC = "desc"
