from datetime import timedelta
from urllib.parse import quote

from flask import Flask
from hypothesis import given, settings
from hypothesis import strategies as st
from mui.v5.grid.filter.item import GridFilterItem
from mui.v5.grid.filter.model import GridFilterModel
from mui.v5.grid.link.operator import GridLinkOperator
from mui.v5.integrations.flask.filter.model import get_grid_filter_model_from_request

app = Flask(__name__)


@given(st.builds(GridFilterModel))
@settings(deadline=timedelta(milliseconds=400))
def test_parse_grid_filter_model_from_flask_request(instance: GridFilterModel) -> None:
    key = "filter_model"
    with app.app_context():
        query_str = quote(instance.model_dump_json())
        with app.test_request_context(
            path=(f"/?{key}={query_str}"),
        ):
            model = get_grid_filter_model_from_request(key=key)
            assert model is not None
            assert isinstance(model.items, list)
            assert all(isinstance(item, GridFilterItem) for item in model.items)
            assert (
                isinstance(model.link_operator, (GridLinkOperator))
                or model.link_operator is None
            )
            assert (
                isinstance(model.quick_filter_logic_operator, (GridLinkOperator))
                or model.quick_filter_logic_operator is None
            )
            assert (
                isinstance(model.quick_filter_values, (str, bool, float))
                or model.quick_filter_values is None
            )
            assert model.link_operator == instance.link_operator
            assert (
                model.quick_filter_logic_operator
                == instance.quick_filter_logic_operator
            )
