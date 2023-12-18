"""The model module holds the GridSortModel, a type alias."""

from typing import List

from typing_extensions import TypeAlias

from mui.v6.grid.sort.item import GridSortItem

"""The model describing how to sort the data grid.

Documentation:
    N/A
Code:
    https://github.com/mui/mui-x/blob/0cdee3369bbf6df792c9228ef55ea1a61a246ff3/packages/grid/x-data-grid/src/models/gridSortModel.ts#L44
"""
GridSortModel: TypeAlias = List[GridSortItem]
