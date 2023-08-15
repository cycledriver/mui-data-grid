from datetime import timedelta
from urllib.parse import quote

from flask import Flask
from hypothesis import given, settings
from hypothesis import strategies as st

from mui.v6.grid.filter.item import GridFilterItem
from mui.v6.grid.filter.model import GridFilterModel
from mui.v6.grid.logic.operator import GridLogicOperator
from mui.v6.integrations.flask.filter.model import get_grid_filter_model_from_request

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
                isinstance(model.logic_operator, (GridLogicOperator))
                or model.logic_operator is None
            )
            assert (
                isinstance(model.quick_filter_logic_operator, (GridLogicOperator))
                or model.quick_filter_logic_operator is None
            )
            assert (
                isinstance(model.quick_filter_values, (str, bool, float))
                or model.quick_filter_values is None
            )
            assert model.logic_operator == instance.logic_operator
            assert (
                model.quick_filter_logic_operator
                == instance.quick_filter_logic_operator
            )
