from hypothesis import given
from hypothesis import strategies as st

from mui.v5.grid.sort.direction import GridSortDirection
from mui.v5.grid.sort.item import GridSortItem, Sort, SortLiterals

valid_sort_values: list[Sort | SortLiterals] = [
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
def test_valid_grid_sort_item_parse(sort_item_dict: dict[str, object]) -> None:
    GridSortItem.parse_obj(sort_item_dict)
