from typing import Dict
from urllib.parse import quote

from flask import Flask
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from mui.v5.grid.filter.model import GridFilterModel
from mui.v5.grid.pagination.model import GridPaginationModel
from mui.v5.grid.request import RequestGridModels
from mui.v5.grid.sort.item import GridSortItem
from mui.v5.integrations.flask.request import get_grid_models_from_request
from tests.mui.v5.grid.filter.test_model import (
    CamelCaseGridFilterModelData,
    SnakeCaseGridFilterModelData,
)
from tests.mui.v5.grid.pagination.test_model import (
    CamelCaseGridPaginationModelData,
    SnakeCaseGridPaginationModelData,
)
from tests.mui.v5.grid.sort.test_item import GridSortItemData

app = Flask(__name__)

CAMEL_SORT_MODEL_KEY = "sortModel[]"
CAMEL_FILTER_MODEL_KEY = "filterModel"
CAMEL_PAGINATION_MODEL_KEY = "paginationModel"
SNAKE_SORT_MODEL_KEY = "sort_model[]"
SNAKE_FILTER_MODEL_KEY = "filter_model"
SNAKE_PAGINATION_MODEL_KEY = "pagination_model"

EMPTY_DICT: Dict[str, SearchStrategy[object]] = {}

SnakeCaseFlatRequestGridModelsData = st.fixed_dictionaries(
    mapping=EMPTY_DICT,
    optional={
        SNAKE_FILTER_MODEL_KEY: st.one_of(
            CamelCaseGridFilterModelData, SnakeCaseGridFilterModelData
        ),
        SNAKE_SORT_MODEL_KEY: st.lists(GridSortItemData),
        "page_size": st.integers(min_value=1),
        "page": st.integers(min_value=1),
    },
)
SnakeCaseNestedRequestGridModelsData = st.fixed_dictionaries(
    mapping=EMPTY_DICT,
    optional={
        SNAKE_FILTER_MODEL_KEY: st.one_of(
            CamelCaseGridFilterModelData, SnakeCaseGridFilterModelData
        ),
        SNAKE_SORT_MODEL_KEY: st.lists(GridSortItemData),
        SNAKE_PAGINATION_MODEL_KEY: st.one_of(
            CamelCaseGridPaginationModelData, SnakeCaseGridPaginationModelData
        ),
    },
)

CamelCaseFlatRequestGridModelsData = st.fixed_dictionaries(
    mapping=EMPTY_DICT,
    optional={
        CAMEL_FILTER_MODEL_KEY: st.one_of(
            CamelCaseGridFilterModelData, SnakeCaseGridFilterModelData
        ),
        CAMEL_SORT_MODEL_KEY: st.lists(GridSortItemData),
        "pageSize": st.integers(min_value=1),
        "page": st.integers(min_value=1),
    },
)
CamelCaseNestedRequestGridModelsData = st.fixed_dictionaries(
    mapping=EMPTY_DICT,
    optional={
        CAMEL_FILTER_MODEL_KEY: st.one_of(
            CamelCaseGridFilterModelData, SnakeCaseGridFilterModelData
        ),
        CAMEL_SORT_MODEL_KEY: st.lists(GridSortItemData),
        CAMEL_PAGINATION_MODEL_KEY: st.one_of(
            CamelCaseGridPaginationModelData, SnakeCaseGridPaginationModelData
        ),
    },
)


@given(CamelCaseFlatRequestGridModelsData)
def test_parse_flat_camel_case_request_grid_models_from_flask_request(
    models_dict: Dict[str, object]
) -> None:
    with app.app_context():
        model = RequestGridModels.model_validate(models_dict)
        query_str = quote(model.model_dump_json())
        with app.test_request_context(
            path=(f"/?{query_str}"),
        ):
            model = get_grid_models_from_request(
                sort_model_key=CAMEL_SORT_MODEL_KEY,
                filter_model_key=CAMEL_FILTER_MODEL_KEY,
                pagination_model_key=CAMEL_PAGINATION_MODEL_KEY,
            )
            # grid filter model validation
            assert isinstance(model.filter_model, GridFilterModel)
            # grid sort model validation
            assert isinstance(model.sort_model, list)
            assert all(isinstance(item, GridSortItem) for item in model.sort_model)
            # grid pagination model validation
            assert isinstance(model.pagination_model, GridPaginationModel)


@given(CamelCaseNestedRequestGridModelsData)
def test_parse_nested_camel_case_request_grid_models_from_flask_request(
    models_dict: Dict[str, object]
) -> None:
    with app.app_context():
        model = RequestGridModels.model_validate(models_dict)
        query_str = quote(model.model_dump_json())
        with app.test_request_context(
            path=(f"/?{query_str}"),
        ):
            model = get_grid_models_from_request(
                sort_model_key=CAMEL_SORT_MODEL_KEY,
                filter_model_key=CAMEL_FILTER_MODEL_KEY,
                pagination_model_key=CAMEL_PAGINATION_MODEL_KEY,
            )
            # grid filter model validation
            assert isinstance(model.filter_model, GridFilterModel)
            # grid sort model validation
            assert isinstance(model.sort_model, list)
            assert all(isinstance(item, GridSortItem) for item in model.sort_model)
            # grid pagination model validation
            assert isinstance(model.pagination_model, GridPaginationModel)


@given(SnakeCaseFlatRequestGridModelsData)
def test_parse_flat_snake_case_request_grid_models_from_flask_request(
    models_dict: Dict[str, object]
) -> None:
    with app.app_context():
        model = RequestGridModels.model_validate(models_dict)
        query_str = quote(model.model_dump_json())
        with app.test_request_context(
            path=(f"/?{query_str}"),
        ):
            model = get_grid_models_from_request(
                sort_model_key=CAMEL_SORT_MODEL_KEY,
                filter_model_key=CAMEL_FILTER_MODEL_KEY,
                pagination_model_key=CAMEL_PAGINATION_MODEL_KEY,
            )
            # grid filter model validation
            assert isinstance(model.filter_model, GridFilterModel)
            # grid sort model validation
            assert isinstance(model.sort_model, list)
            assert all(isinstance(item, GridSortItem) for item in model.sort_model)
            # grid pagination model validation
            assert isinstance(model.pagination_model, GridPaginationModel)


@given(SnakeCaseNestedRequestGridModelsData)
def test_parse_nested_snake_case_request_grid_models_from_flask_request(
    models_dict: Dict[str, object]
) -> None:
    with app.app_context():
        model = RequestGridModels.model_validate(models_dict)
        query_str = quote(model.model_dump_json())
        with app.test_request_context(
            path=(f"/?{query_str}"),
        ):
            model = get_grid_models_from_request(
                sort_model_key=CAMEL_SORT_MODEL_KEY,
                filter_model_key=CAMEL_FILTER_MODEL_KEY,
                pagination_model_key=CAMEL_PAGINATION_MODEL_KEY,
            )
            # grid filter model validation
            assert isinstance(model.filter_model, GridFilterModel)
            # grid sort model validation
            assert isinstance(model.sort_model, list)
            assert all(isinstance(item, GridSortItem) for item in model.sort_model)
            # grid pagination model validation
            assert isinstance(model.pagination_model, GridPaginationModel)
