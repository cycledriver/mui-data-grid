from urllib.parse import quote

from flask import Flask
from hypothesis import given
from hypothesis import strategies as st

from mui.v6.grid.pagination.model import GridPaginationModel
from mui.v6.integrations.flask.pagination.model import (
    get_grid_pagination_model_from_request,
)

app = Flask(__name__)


@given(st.builds(GridPaginationModel))
def test_parse_grid_pagination_model_from_flask_request_no_key(
    instance: GridPaginationModel,
) -> None:
    model = None
    with app.app_context():
        query_str = quote(instance.model_dump_json())
        with app.test_request_context(
            path=(f"/?{query_str}"),
        ):
            model = get_grid_pagination_model_from_request()
    assert model is not None
    assert model.page >= 0
    assert model.page_size >= 1
    assert instance.page == instance.page
    assert model.page_size == instance.page_size


@given(st.builds(GridPaginationModel))
def test_parse_grid_pagination_model_from_flask_request_with_key(
    instance: GridPaginationModel,
) -> None:
    key = "pagination_model"
    with app.app_context():
        query_str = quote(instance.model_dump_json())
        with app.test_request_context(
            path=(f"/?{key}={query_str}"),
        ):
            model = get_grid_pagination_model_from_request(key=key)
            assert model is not None
            assert model.page >= 0
            assert model.page_size >= 1
            assert instance.page == instance.page
            assert model.page_size == instance.page_size
