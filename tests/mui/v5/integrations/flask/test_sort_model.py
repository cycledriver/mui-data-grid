from json import dumps
from urllib.parse import quote

from flask import Flask
from hypothesis import given
from hypothesis import strategies as st

from mui.v5.grid.sort import GridSortModel
from mui.v5.grid.sort.item import GridSortItem
from mui.v5.integrations.flask.sort.model import get_grid_sort_model_from_request

app = Flask(__name__)


@given(st.lists(st.builds(GridSortItem)))
def test_parse_grid_sort_model_from_flask_request(sort_model: GridSortModel) -> None:
    key = "sort_model[]"
    with app.app_context():
        json = dumps([item.dict() for item in sort_model])
        query_str = quote(json)
        with app.test_request_context(
            path=(f"/?{key}={query_str}"),
        ):
            parsed_model = get_grid_sort_model_from_request(key=key)
            assert isinstance(parsed_model, list)
            assert all(isinstance(item, GridSortItem) for item in parsed_model)
