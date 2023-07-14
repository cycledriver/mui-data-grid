from typing import Optional

from mui.v6.grid import GridSortDirection, GridSortItem
from mui.v6.integrations.sqlalchemy.sort.apply_item import get_operator
from pytest import mark


@mark.parametrize(
    "sort_direction", (GridSortDirection.ASC, GridSortDirection.DESC, None)
)
def test_get_operator(sort_direction: Optional[GridSortDirection]) -> None:
    item = GridSortItem.model_validate({"field": "id", "sort": sort_direction})
    f = get_operator(item=item)
    if sort_direction == GridSortDirection.ASC:
        assert f.__name__ == "asc"
    elif sort_direction == GridSortDirection.DESC:
        assert f.__name__ == "desc"
    elif sort_direction is None:
        assert f.__name__ == "_no_operation"
