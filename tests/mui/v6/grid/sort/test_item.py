from typing import Dict

from hypothesis import given
from hypothesis import strategies as st

from mui.v6.grid.sort.direction import GridSortDirection
from mui.v6.grid.sort.item import GridSortItem

valid_sort_values = [
    "asc",
    "desc",
    GridSortDirection.ASC,
    GridSortDirection.DESC,
    None,
]

GridSortItemData = st.fixed_dictionaries(
    mapping={"field": st.text(), "sort": st.sampled_from(valid_sort_values)}
)


@given(GridSortItemData)
def test_valid_grid_sort_item_parse(sort_item_dict: Dict[str, object]) -> None:
    GridSortItem.model_validate(sort_item_dict)
