from typing import Any, Callable, Optional

from pytest import mark
from sqlalchemy import asc, desc
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query, Session

from mui.v6.grid import GridSortDirection, GridSortItem, GridSortModel
from mui.v6.integrations.sqlalchemy.resolver import Resolver
from mui.v6.integrations.sqlalchemy.sort import apply_sort_to_query_from_model
from tests.conftest import PARENT_MODEL_RESOLVABLE_FIELDS
from tests.fixtures.sqlalchemy import ParentModel


def _no_operation(column: Any) -> None:
    """Returns the column, unsorted"""
    return None


def _get_direction_function(
    direction: Optional[GridSortDirection],
) -> Callable[..., Any]:
    if direction == GridSortDirection.ASC:
        return asc
    elif direction == GridSortDirection.DESC:
        return desc
    else:
        return _no_operation


def _get_direction_str(
    direction: Optional[GridSortDirection],
) -> Optional[str]:
    if direction == GridSortDirection.ASC:
        return "ASC"
    elif direction == GridSortDirection.DESC:
        return "DESC"
    else:
        return None


@mark.parametrize("direction", (GridSortDirection.ASC, GridSortDirection.DESC, None))
def test_apply_sort_to_query_from_model_single_field(
    direction: Optional[GridSortDirection],
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    item = GridSortItem(field="id", sort=direction)
    assert item.field in PARENT_MODEL_RESOLVABLE_FIELDS
    model: GridSortModel = [item]
    sorted_query = apply_sort_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = sorted_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    dir_str = _get_direction_str(direction=direction)
    if dir_str is not None:
        assert f"ORDER BY {ParentModel.__tablename__}.id {dir_str}" in compiled_str
    else:
        assert "ORDER BY" not in compiled_str

    sorted_results = sorted_query.all()
    row_count = sorted_query.count()

    direction_func = _get_direction_function(direction=direction)
    expected = session.query(ParentModel).order_by(direction_func(ParentModel.id))
    expected_row_count = expected.count()
    expected_results = expected.all()

    assert row_count == expected_row_count
    if direction is not None:
        for expected_item, sorted_item in zip(expected_results, sorted_results):
            assert expected_item.id == sorted_item.id


@mark.parametrize(
    "direction",
    (
        GridSortDirection.ASC,
        GridSortDirection.DESC,
        None,
    ),
)
def test_apply_sort_to_query_from_model_multiple_fields(
    direction: Optional[GridSortDirection],
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    # order matters with how we're using the fields!
    model: GridSortModel = [
        GridSortItem(field="grouping_id", sort=direction),
        GridSortItem(field="id", sort=direction),
    ]
    for item in model:
        assert item.field in PARENT_MODEL_RESOLVABLE_FIELDS

    sorted_query = apply_sort_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = sorted_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    tbl = ParentModel.__tablename__
    dir_str = _get_direction_str(direction=direction)
    if dir_str is not None:
        assert (
            f"ORDER BY {tbl}.grouping_id {dir_str}, {tbl}.id {dir_str}" in compiled_str
        )
    else:
        assert "ORDER BY" not in compiled_str

    sorted_results = sorted_query.all()
    row_count = sorted_query.count()

    direction_func = _get_direction_function(direction=direction)
    expected = session.query(ParentModel).order_by(
        direction_func(ParentModel.grouping_id), direction_func(ParentModel.id)
    )
    expected_row_count = expected.count()
    expected_results = expected.all()

    assert row_count == expected_row_count
    if direction is not None:
        for expected_item, sorted_item in zip(expected_results, sorted_results):
            assert expected_item.id == sorted_item.id
