from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query, Session

from mui.v6.grid import GridPaginationModel
from mui.v6.integrations.sqlalchemy.pagination import (
    apply_limit_offset_to_query_from_model,
)
from tests.conftest import GENERATED_PARENT_MODEL_COUNT
from tests.fixtures.sqlalchemy import ParentModel


@given(
    model=st.builds(
        GridPaginationModel,
        # https://www.sqlite.org/datatype3.html - maximum 8-byte integer value
        page=st.integers(min_value=0, max_value=GENERATED_PARENT_MODEL_COUNT),
        page_size=st.integers(min_value=1, max_value=GENERATED_PARENT_MODEL_COUNT),
    )
)
def test_apply_limit_offset_to_query_from_model(
    model: GridPaginationModel,
    session: Session,
    query: "Query[ParentModel]",
) -> None:
    paginated = apply_limit_offset_to_query_from_model(query=query, model=model)
    compiled = paginated.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert "LIMIT ?" in compiled_str
    assert "OFFSET ?" in compiled_str
    print(model, compiled.params)
    assert compiled.params["param_1"] == model.page_size
    assert compiled.params["param_2"] == model.offset
    row_count = paginated.count()
    expected_row_count = (
        session.query(ParentModel).limit(model.page_size).offset(model.offset).count()
    )
    assert row_count == expected_row_count
