from typing import Dict

from hypothesis import given
from hypothesis import strategies as st

from mui.v6.grid.filter.item import GridFilterItem
from mui.v6.grid.logic.operator import GridLogicOperator

valid_operators = [
    "and",
    "or",
    GridLogicOperator.And,
    GridLogicOperator.Or,
    None,
]

GridFilterItemData = st.fixed_dictionaries(  # type: ignore[misc]
    mapping={
        "field": st.text(),
        "operator": st.text(),
    },
    optional={
        "id": st.one_of(st.text(), st.integers(), st.none()),
        "value": st.one_of(st.text(), st.none(), st.booleans(), st.floats()),
    },
)


@given(filter_item_dict=GridFilterItemData)
def test_parse_valid_grid_filter_item_dict(filter_item_dict: Dict[str, object]) -> None:
    assert "columnField" in filter_item_dict
    parsed = GridFilterItem.parse_obj(filter_item_dict)
    assert isinstance(parsed.field, str)
    assert isinstance(parsed.id, (str, int)) or parsed.id is None
    assert isinstance(parsed.operator, str) or parsed.operator is None
    assert isinstance(parsed.value, (str, bool, float)) or parsed.value is None
