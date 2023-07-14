from typing import Dict

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import builds

from mui.v6.grid import GridPaginationModel

CamelCaseGridPaginationModelData = st.fixed_dictionaries(
    mapping={
        "page": st.integers(min_value=0),
        "pageSize": st.integers(min_value=1),
    },
)
SnakeCaseGridPaginationModelData = st.fixed_dictionaries(
    mapping={
        "page": st.integers(min_value=0),
        "page_size": st.integers(min_value=1),
    },
)


@given(builds(GridPaginationModel))
def test_parse_valid_grid_pagination_model_generated(
    instance: GridPaginationModel,
) -> None:
    assert instance.page >= 0
    assert instance.page_size >= 1


@given(CamelCaseGridPaginationModelData)
def test_parse_valid_grid_pagination_model_camel_case_dict(
    model_dict: Dict[str, int]
) -> None:
    assert "page" in model_dict
    assert "pageSize" in model_dict
    parsed = GridPaginationModel.model_validate(model_dict)
    assert parsed.page >= 0
    assert parsed.page_size >= 1


@given(SnakeCaseGridPaginationModelData)
def test_parse_valid_grid_pagination_model_snake_case_dict(
    model_dict: Dict[str, int]
) -> None:
    assert "page" in model_dict
    assert "page_size" in model_dict
    parsed = GridPaginationModel.model_validate(model_dict)
    assert parsed.page >= 0
    assert parsed.page_size >= 1
