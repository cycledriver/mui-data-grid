from hypothesis import given
from hypothesis import strategies as st

from mui.v6.grid.sort.model import GridSortModel

from .test_item import GridSortItemData


@given(sort_model=st.lists(GridSortItemData))
def test_valid_grid_sort_model_parse(sort_model: GridSortModel) -> None:
    assert isinstance(sort_model, list)
