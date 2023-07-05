from typing import Dict

from hypothesis import given
from hypothesis import strategies as st

from mui.v6.grid.filter.item import GridFilterItem
from mui.v6.grid.filter.model import GridFilterModel
from mui.v6.grid.logic.operator import GridLogicOperator

from .test_item import GridFilterItemData

valid_operators = [
    "and",
    "or",
    GridLogicOperator.And,
    GridLogicOperator.Or,
    None,
]

CamelCaseGridFilterModelData = st.fixed_dictionaries(  # type: ignore[misc]
    {
        "items": st.lists(GridFilterItemData),
    },
    optional={
        "logicOperator": st.sampled_from(valid_operators),
        "quickFilterLogicOperator": st.sampled_from(valid_operators),
        "quickFilterValues": st.one_of(
            st.lists(st.one_of(st.text(), st.none(), st.booleans(), st.floats())),
            st.none(),
        ),
    },
)
SnakeCaseGridFilterModelData = st.fixed_dictionaries(  # type: ignore[misc]
    {
        "items": st.lists(GridFilterItemData),
    },
    optional={
        "logic_operator": st.sampled_from(valid_operators),
        "quick_filter_logic_operator": st.sampled_from(valid_operators),
        "quickFilterValues": st.one_of(
            st.lists(st.one_of(st.text(), st.none(), st.booleans(), st.floats())),
            st.none(),
        ),
    },
)


@given(CamelCaseGridFilterModelData)
def test_valid_grid_filter_model_camel_case_parse(
    filter_item_dict: Dict[str, object]
) -> None:
    parsed = GridFilterModel.parse_obj(filter_item_dict)
    assert isinstance(parsed.items, list)
    assert all(isinstance(item, GridFilterItem) for item in parsed.items)
    assert (
        isinstance(parsed.logic_operator, GridLogicOperator)
        or parsed.logic_operator is None
    )
    assert (
        isinstance(parsed.quick_filter_logic_operator, GridLogicOperator)
        or parsed.quick_filter_logic_operator is None
    )
    assert (
        isinstance(parsed.quick_filter_values, list)
        or parsed.quick_filter_values is None
    )


@given(SnakeCaseGridFilterModelData)
def test_valid_grid_filter_model_snake_case_parse(
    filter_item_dict: Dict[str, object]
) -> None:
    parsed = GridFilterModel.parse_obj(filter_item_dict)
    assert isinstance(parsed.items, list)
    assert all(isinstance(item, GridFilterItem) for item in parsed.items)
    assert (
        isinstance(parsed.logic_operator, GridLogicOperator)
        or parsed.logic_operator is None
    )
    assert (
        isinstance(parsed.quick_filter_logic_operator, GridLogicOperator)
        or parsed.quick_filter_logic_operator is None
    )
    assert (
        isinstance(parsed.quick_filter_values, list)
        or parsed.quick_filter_values is None
    )
