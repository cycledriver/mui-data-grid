from datetime import timedelta
from itertools import product
from operator import ge, gt, le, lt
from typing import Any, Callable, Optional

from pytest import mark
from sqlalchemy import and_, or_
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query, Session
from typing_extensions import Literal

from mui.v6.grid import GridFilterModel, GridLogicOperator
from mui.v6.integrations.sqlalchemy.filter import apply_filter_to_query_from_model
from mui.v6.integrations.sqlalchemy.resolver import Resolver
from tests.conftest import FIRST_DATE_DATETIME, calculate_grouping_id
from tests.fixtures.sqlalchemy import (
    Category,
    ChildModel,
    ParentModel,
    category_from_id,
)

# from itertools import product
LINK_OPERATOR_ARGVALUES = (GridLogicOperator.And, GridLogicOperator.Or, None)


def _sql_logic_operator_from(
    logic_operator: Optional[GridLogicOperator],
) -> Literal["AND", "OR"]:
    return "OR" if logic_operator == GridLogicOperator.Or else "AND"


def _join_filter_from(
    logic_operator: Optional[GridLogicOperator],
) -> Callable[..., Any]:
    return or_ if logic_operator == GridLogicOperator.Or else and_


@mark.parametrize(
    argnames=("logic_operator"),
    argvalues=LINK_OPERATOR_ARGVALUES,
)
def test_apply_eq_apply_filter_to_query_from_model_multiple_fields_and_model(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = Category.CATEGORY_0
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "id",
                    "value": target_parent_id,
                    "operator": "==",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": "==",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "==",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.id = ?" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id = ?"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category = ?" in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.id == target_parent_id,
                ParentModel.grouping_id == TARGET_GROUP,
                ChildModel.category == TARGET_CATEGORY,
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.id == target_parent_id
            assert row.parent.grouping_id == TARGET_GROUP
            assert row.category == TARGET_CATEGORY
        else:
            assert (
                row.parent.id == target_parent_id
                or row.parent.grouping_id == TARGET_GROUP
                or row.category == TARGET_CATEGORY
            )


@mark.parametrize(
    argnames=("expected_id", "logic_operator"),
    argvalues=((4, GridLogicOperator.And), (1, GridLogicOperator.Or), (1, None)),
)
def test_apply_is_datetime_apply_filter_to_query_from_model_multi_field_and_model(
    expected_id: int,
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    THIRD_DAY = FIRST_DATE_DATETIME + timedelta(days=3)
    # sqlite doesn't support the concept of timezones, so we get a naive datetime
    # back from the database
    ROW_THIRD_DAY = THIRD_DAY.replace(tzinfo=None)
    TARGET_CATEGORY = category_from_id(id=expected_id)
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "created_at",
                    "value": THIRD_DAY.isoformat(),
                    "operator": "is",
                },
                {
                    "field": "id",
                    "value": expected_id,
                    "operator": "is",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "==",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.created_at = ?" in compiled_str
    assert f"{sql_logic_operator} {ParentModel.__tablename__}.id = ?" in compiled_str
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category = ?" in compiled_str
    )
    assert compiled.params["created_at_1"] == THIRD_DAY
    assert compiled.params["id_1"] == expected_id
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.created_at == THIRD_DAY,
                ParentModel.id == expected_id,
                ChildModel.category == TARGET_CATEGORY,
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.id == expected_id
            assert row.parent.created_at == ROW_THIRD_DAY
            assert row.category == TARGET_CATEGORY
        else:
            assert (
                row.parent.id == expected_id
                or row.parent.created_at == ROW_THIRD_DAY
                or row.category == TARGET_CATEGORY
            )


@mark.parametrize(argnames=("logic_operator"), argvalues=LINK_OPERATOR_ARGVALUES)
def test_apply_ne_apply_filter_to_query_from_model_multiple_fields(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "id",
                    "value": target_parent_id,
                    "operator": "!=",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": "!=",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "!=",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.id != ?" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id != ?"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category != ?" in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.id != target_parent_id,
                ParentModel.grouping_id != TARGET_GROUP,
                ChildModel.category != TARGET_CATEGORY,
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.id != target_parent_id
            assert row.parent.grouping_id != TARGET_GROUP
            assert row.category != TARGET_CATEGORY
        else:
            # because it's an `OR` clause, the != id ends up being the only
            # thing that evaluates, as it has both the ID and the group, while
            # the others at least have a differing ID.
            assert (
                row.parent.id != target_parent_id
                or row.parent.grouping_id != TARGET_GROUP
                or row.category != TARGET_CATEGORY
            )


@mark.parametrize(
    argnames=("operator", "logic_operator"),
    argvalues=(tuple(product(("<", ">"), LINK_OPERATOR_ARGVALUES))),
)
def test_apply_gt_lt_apply_filter_to_query_from_model_multiple_fields(
    operator: str,
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "id",
                    "value": target_parent_id,
                    "operator": operator,
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": operator,
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": operator,
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
        in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    base_query = session.query(ChildModel).join(ParentModel)
    op = gt if operator == ">" else lt
    expected_row_count = base_query.filter(
        join_filter(
            op(ParentModel.id, target_parent_id),
            op(ParentModel.grouping_id, TARGET_GROUP),
            op(ChildModel.category, TARGET_CATEGORY),
        )
    ).count()
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert op(row.parent.id, target_parent_id)
            assert op(row.parent.grouping_id, TARGET_GROUP)
            assert op(row.category, TARGET_CATEGORY)
        else:
            assert (
                op(row.parent.id, target_parent_id)
                or op(row.parent.grouping_id, TARGET_GROUP)
                or op(row.category, TARGET_CATEGORY)
            )


@mark.parametrize(
    argnames=("operator", "logic_operator"),
    argvalues=(tuple(product(("<=", ">="), LINK_OPERATOR_ARGVALUES))),
)
def test_apply_ge_le_apply_filter_to_query_from_model_multiple_fields(
    operator: str,
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "id",
                    "value": target_parent_id,
                    "operator": operator,
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": operator,
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": operator,
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category {operator} ?"
        in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    op = ge if operator == ">=" else le
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                op(ParentModel.id, target_parent_id),
                op(ParentModel.grouping_id, TARGET_GROUP),
                op(ChildModel.category, TARGET_CATEGORY),
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert op(row.parent.id, target_parent_id)
            assert op(row.parent.grouping_id, TARGET_GROUP)
            assert op(row.category, TARGET_CATEGORY)
        else:
            assert (
                op(row.parent.id, target_parent_id)
                or op(row.parent.grouping_id, TARGET_GROUP)
                or op(row.category, TARGET_CATEGORY)
            )


@mark.parametrize(
    argnames=("field", "logic_operator"),
    argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
)
def test_apply_is_empty_apply_filter_to_query_from_model_multiple_fields(
    field: str,
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": field,
                    "value": None,
                    "operator": "isEmpty",
                },
                {
                    "field": "grouping_id",
                    "value": None,
                    "operatorValue": "isEmpty",
                },
                {
                    "field": "category",
                    "value": None,
                    "operator": "isEmpty",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NULL" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id IS NULL"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category IS NULL"
        in compiled_str
    )

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                getattr(ParentModel, field) == None,  # noqa: E711
                ParentModel.grouping_id == None,  # noqa: E711
                ChildModel.category == None,  # noqa: E711
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert getattr(row.parent, field) is None
            assert row.parent.grouping_id is None
            assert row.category is None
        else:
            assert (
                getattr(row.parent, field) is None
                or row.parent.grouping_id is None
                or row.category is None
            )


@mark.parametrize(
    argnames=("field", "logic_operator"),
    argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
)
def test_apply_is_not_empty_apply_filter_to_query_from_model_multiple_fields(
    field: str,
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": field,
                    "value": None,
                    "operator": "isNotEmpty",
                },
                {
                    "field": "grouping_id",
                    "value": None,
                    "operator": "isNotEmpty",
                },
                {
                    "field": "category",
                    "value": None,
                    "operator": "isNotEmpty",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NOT NULL" in compiled_str
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id IS NOT NULL"
        in compiled_str
    )

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                getattr(ParentModel, field) != None,  # noqa: E711
                ParentModel.grouping_id != None,  # noqa: E711
                ChildModel.category != None,  # noqa: E711
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert getattr(row.parent, field) is not None
            assert row.parent.grouping_id is not None
            assert row.category is not None
        else:
            assert (
                getattr(row.parent, field) is not None
                or row.parent.grouping_id is not None
                or row.category is not None
            )


@mark.parametrize(argnames=("logic_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_is_any_of_apply_filter_to_query_from_model_multiple_fields(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_IDS = [1, 2, 3]
    TARGET_GROUPS = list(
        {calculate_grouping_id(model_id=TARGET_ID) for TARGET_ID in TARGET_IDS}
    )
    TARGET_CATEGORIES = list(
        {category_from_id(id=TARGET_ID) for TARGET_ID in TARGET_IDS}
    )

    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "id",
                    "value": TARGET_IDS,
                    "operator": "isAnyOf",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUPS,
                    "operator": "isAnyOf",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORIES,
                    "operator": "isAnyOf",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert (
        f"WHERE {ParentModel.__tablename__}.id IN (__[POSTCOMPILE_id_1])"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ParentModel.__tablename__}.grouping_id IN "
        + "(__[POSTCOMPILE_grouping_id_1])"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} {ChildModel.__tablename__}.category IN "
        + "(__[POSTCOMPILE_category_1])"
        in compiled_str
    )
    assert compiled.params["id_1"] == TARGET_IDS
    assert compiled.params["grouping_id_1"] == TARGET_GROUPS
    assert compiled.params["category_1"] == TARGET_CATEGORIES

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.id.in_(TARGET_IDS),
                ParentModel.grouping_id.in_(TARGET_GROUPS),
                ChildModel.category.in_(TARGET_CATEGORIES),
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.id in TARGET_IDS
            assert row.parent.grouping_id in TARGET_GROUPS
            assert row.category in TARGET_CATEGORIES
        else:
            assert (
                row.parent.id in TARGET_IDS
                or row.parent.grouping_id in TARGET_GROUPS
                or row.category in TARGET_CATEGORIES
            )


@mark.parametrize(argnames=("logic_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_contains_apply_filter_to_query_from_model_multiple_fields(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME = ParentModel.__name__
    TARGET_GROUP = 0
    TARGET_CATEGORY = Category.CATEGORY_0.value[:3]
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "name",
                    "value": TARGET_NAME,
                    "operator": "contains",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": "contains",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "contains",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert (
        f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ? || '%')"
        in compiled_str  # noqa
    )
    assert (
        f"{sql_logic_operator} ({ParentModel.__tablename__}.grouping_id LIKE "
        + "'%' || ? || '%')"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} ({ChildModel.__tablename__}.category LIKE "
        + "'%' || ? || '%')"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.name.contains(TARGET_NAME),
                ParentModel.grouping_id.contains(TARGET_GROUP),
                ChildModel.category.contains(TARGET_CATEGORY),
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert TARGET_NAME in row.parent.name
            assert row.parent.grouping_id == TARGET_GROUP
            assert TARGET_CATEGORY in row.category
        else:
            assert (
                TARGET_NAME in row.parent.name
                or row.parent.grouping_id == TARGET_GROUP
                or TARGET_CATEGORY in row.category
            )


@mark.parametrize(argnames=("logic_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_starts_with_apply_filter_to_query_from_model_multiple_fields(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME = ParentModel.__name__
    TARGET_GROUP = 0
    TARGET_CATEGORY = Category.CATEGORY_0.value[:3]
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "name",
                    "value": TARGET_NAME,
                    "operator": "startsWith",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator": "startsWith",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "startsWith",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE ? || '%')" in compiled_str
    assert (
        f"{sql_logic_operator} ({ParentModel.__tablename__}.grouping_id LIKE ? || '%')"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} ({ChildModel.__tablename__}.category LIKE ? || '%')"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.name.startswith(TARGET_NAME),
                ParentModel.grouping_id.startswith(TARGET_GROUP),
                ChildModel.category.startswith(TARGET_CATEGORY),
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.name.startswith(TARGET_NAME)
            assert str(row.parent.grouping_id).startswith(str(TARGET_GROUP))
            assert row.category.startswith(TARGET_CATEGORY)
        else:
            assert (
                row.parent.name.startswith(TARGET_NAME)
                or str(row.parent.grouping_id).startswith(str(TARGET_GROUP))
                or row.category.startswith(TARGET_CATEGORY)
            )


@mark.parametrize(argnames=("logic_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_ends_with_apply_filter_to_query_from_model_multiple_fields(
    logic_operator: Optional[GridLogicOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME_AND_GROUP = "0"
    TARGET_CATEGORY = Category.CATEGORY_0.value[3:]
    model = GridFilterModel.parse_obj(
        {
            "items": [
                {
                    "field": "name",
                    "value": TARGET_NAME_AND_GROUP,
                    "operator": "endsWith",
                },
                {
                    "field": "grouping_id",
                    "value": TARGET_NAME_AND_GROUP,
                    "operator": "endsWith",
                },
                {
                    "field": "category",
                    "value": TARGET_CATEGORY,
                    "operator": "endsWith",
                },
            ],
            "logic_operator": logic_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_logic_operator = _sql_logic_operator_from(logic_operator=logic_operator)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ?)" in compiled_str
    assert (
        f"{sql_logic_operator} ({ParentModel.__tablename__}.grouping_id LIKE '%' || ?)"
        in compiled_str
    )
    assert (
        f"{sql_logic_operator} ({ChildModel.__tablename__}.category LIKE '%' || ?)"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME_AND_GROUP
    assert compiled.params["grouping_id_1"] == TARGET_NAME_AND_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(logic_operator=logic_operator)
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.name.endswith(TARGET_NAME_AND_GROUP),
                ParentModel.grouping_id.endswith(TARGET_NAME_AND_GROUP),
                ChildModel.category.endswith(TARGET_CATEGORY),
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if logic_operator == GridLogicOperator.And:
            assert row.parent.name.endswith(TARGET_NAME_AND_GROUP)
            assert str(row.parent.grouping_id).endswith(TARGET_NAME_AND_GROUP)
            assert row.category.endswith(TARGET_CATEGORY)
        else:
            assert (
                row.parent.name.endswith(TARGET_NAME_AND_GROUP)
                or str(row.parent.grouping_id).endswith(TARGET_NAME_AND_GROUP)
                or row.category.endswith(TARGET_CATEGORY)
            )
