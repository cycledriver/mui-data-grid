from datetime import timedelta

from pytest import mark
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query, Session

from mui.v5.grid import GridFilterModel
from mui.v5.integrations.sqlalchemy.filter import apply_filter_to_query_from_model
from mui.v5.integrations.sqlalchemy.resolver import Resolver
from tests.conftest import FIRST_DATE_DATETIME
from tests.fixtures.sqlalchemy import ParentModel


@mark.parametrize("operator", ("==", "equals", "is"))
def test_apply_eq_apply_filter_to_query_from_model_single_field(
    operator: str,
    query: "Query[ParentModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": operator,
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.id = ?" in compiled_str
    assert compiled.params["id_1"] == target_parent_id

    row = filtered_query.first()
    assert row is not None
    assert row.id == target_parent_id


def test_apply_is_datetime_apply_filter_to_query_from_model_single_field(
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    THIRD_DAY = FIRST_DATE_DATETIME + timedelta(days=3)
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "created_at",
                    "value": THIRD_DAY.isoformat(),
                    "operator_value": "is",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.created_at = ?" in compiled_str
    assert compiled.params["created_at_1"] == THIRD_DAY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    assert row_count == 1
    row = rows[0]
    assert row is not None
    assert row.created_at == THIRD_DAY.replace(tzinfo=None)


def test_apply_ne_apply_filter_to_query_from_model_single_field(
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": "!=",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.id != ?" in compiled_str
    assert compiled.params["id_1"] == target_parent_id

    rows = filtered_query.all()
    row_count = filtered_query.count()
    expected_row_count = (
        session.query(ParentModel).filter(ParentModel.id != target_parent_id).count()
    )
    assert row_count == expected_row_count
    assert all(row.id != target_parent_id for row in rows)


@mark.parametrize("operator", ("<", ">"))
def test_apply_gt_lt_apply_filter_to_query_from_model_single_field(
    operator: str,
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": operator,
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert compiled.params["id_1"] == target_parent_id

    rows = filtered_query.all()
    row_count = filtered_query.count()
    if operator == ">":
        expected_row_count = (
            session.query(ParentModel).filter(ParentModel.id > target_parent_id).count()
        )
        assert row_count == expected_row_count
        assert all(row.id > target_parent_id for row in rows)  # pyright: ignore
    else:
        expected_row_count = (
            session.query(ParentModel).filter(ParentModel.id < target_parent_id).count()
        )
        assert row_count == expected_row_count
        assert all(row.id < target_parent_id for row in rows)  # pyright: ignore


@mark.parametrize("operator", (">=", "<="))
def test_apply_ge_le_apply_filter_to_query_from_model_single_field(
    operator: str,
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": operator,
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert compiled.params["id_1"] == target_parent_id

    rows = filtered_query.all()
    row_count = filtered_query.count()
    if operator == ">=":
        expected_row_count = (
            session.query(ParentModel)
            .filter(ParentModel.id >= target_parent_id)
            .count()
        )
        assert row_count == expected_row_count
        assert all(row.id >= target_parent_id for row in rows)
    else:
        expected_row_count = (
            session.query(ParentModel)
            .filter(ParentModel.id <= target_parent_id)
            .count()
        )
        assert row_count == expected_row_count
        assert all(row.id <= target_parent_id for row in rows)


@mark.parametrize("field", ("id", "null_field"))
def test_apply_is_empty_apply_filter_to_query_from_model_single_field(
    field: str,
    query: "Query[ParentModel]",
    resolver: Resolver,
    parent_model_count: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": field,
                    "value": None,
                    "operator_value": "isEmpty",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NULL" in compiled_str

    rows = filtered_query.all()
    row_count = filtered_query.count()
    if field == "null_field":
        assert row_count == parent_model_count
    elif field == "id":
        assert row_count == 0
    assert all(row.null_field is None for row in rows)


@mark.parametrize("field", ("id", "null_field"))
def test_apply_is_not_empty_apply_filter_to_query_from_model_single_field(
    field: str,
    query: "Query[ParentModel]",
    resolver: Resolver,
    parent_model_count: int,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": field,
                    "value": None,
                    "operator_value": "isNotEmpty",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NOT NULL" in compiled_str

    rows = filtered_query.all()
    row_count = filtered_query.count()
    if field == "id":
        assert row_count == parent_model_count
    elif field == "null_field":
        assert row_count == 0
    assert all(row.null_field is None for row in rows)


def test_apply_is_any_of_apply_filter_to_query_from_model_single_field(
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    TARGET_IDS = [1, 2, 3]
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": TARGET_IDS,
                    "operator_value": "isAnyOf",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert (
        f"WHERE {ParentModel.__tablename__}.id IN (__[POSTCOMPILE_id_1])"
        in compiled_str
    )
    assert compiled.params["id_1"] == TARGET_IDS

    rows = filtered_query.all()
    row_count = filtered_query.count()
    assert row_count == len(TARGET_IDS)
    assert all(row.id in TARGET_IDS for row in rows)


def test_apply_contains_apply_filter_to_query_from_model_single_field(
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": ParentModel.__name__,
                    "operator_value": "contains",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert (
        f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ? || '%')" in compiled_str
    )
    assert compiled.params["name_1"] == ParentModel.__name__

    rows = filtered_query.all()
    row_count = filtered_query.count()
    expected_row_count = (
        session.query(ParentModel)
        .filter(ParentModel.name.contains(ParentModel.__name__))
        .count()
    )
    assert row_count == expected_row_count
    assert all(ParentModel.__name__ in row.name for row in rows)


def test_apply_starts_with_apply_filter_to_query_from_model_single_field(
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": ParentModel.__name__,
                    "operator_value": "startsWith",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE ? || '%')" in compiled_str
    assert compiled.params["name_1"] == ParentModel.__name__

    rows = filtered_query.all()
    row_count = filtered_query.count()
    expected_row_count = (
        session.query(ParentModel)
        .filter(ParentModel.name.startswith(ParentModel.__name__))
        .count()
    )
    assert row_count == expected_row_count
    assert all(row.name.startswith(ParentModel.__name__) for row in rows)


def test_apply_ends_with_apply_filter_to_query_from_model_single_field(
    session: Session,
    query: "Query[ParentModel]",
    resolver: Resolver,
    parent_model_count: int,
) -> None:
    VALUE = "0"
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": VALUE,
                    "operator_value": "endsWith",
                },
            ],
            "link_operator": None,  # defaults to `or_`
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ?)" in compiled_str
    assert compiled.params["name_1"] == VALUE

    rows = filtered_query.all()
    row_count = filtered_query.count()
    expected_row_count = (
        session.query(ParentModel).filter(ParentModel.name.endswith(VALUE)).count()
    )
    assert row_count == expected_row_count
    assert all(row.name.endswith(VALUE) for row in rows)
