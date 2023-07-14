from datetime import timedelta
from itertools import product
from operator import ge, gt, le, lt
from typing import Any, Callable, Optional

from pytest import mark
from sqlalchemy import and_, or_
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Query, Session
from typing_extensions import Literal

from mui.v5.grid import GridFilterModel, GridLinkOperator
from mui.v5.integrations.sqlalchemy.filter import apply_filter_to_query_from_model
from mui.v5.integrations.sqlalchemy.resolver import Resolver
from tests.conftest import FIRST_DATE_DATETIME, calculate_grouping_id
from tests.fixtures.sqlalchemy import (
    Category,
    ChildModel,
    ParentModel,
    category_from_id,
)

# from itertools import product
LINK_OPERATOR_ARGVALUES = (GridLinkOperator.And, GridLinkOperator.Or, None)


def _sql_link_operator_from(
    link_operator: Optional[GridLinkOperator],
) -> Literal["AND", "OR"]:
    return "OR" if link_operator == GridLinkOperator.Or else "AND"


def _join_filter_from(
    link_operator: Optional[GridLinkOperator],
) -> Callable[..., Any]:
    return or_ if link_operator == GridLinkOperator.Or else and_


@mark.parametrize(
    argnames=("link_operator"),
    argvalues=LINK_OPERATOR_ARGVALUES,
)
def test_apply_eq_apply_filter_to_query_from_model_multiple_fields_and_model(
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = Category.CATEGORY_0
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": "==",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": "==",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "==",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.id = ?" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id = ?"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category = ?" in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
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
    argnames=("expected_id", "link_operator"),
    argvalues=((4, GridLinkOperator.And), (1, GridLinkOperator.Or), (1, None)),
)
def test_apply_is_datetime_apply_filter_to_query_from_model_multi_field_and_model(
    expected_id: int,
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    THIRD_DAY = FIRST_DATE_DATETIME + timedelta(days=3)
    # sqlite doesn't support the concept of timezones, so we get a naive datetime
    # back from the database
    ROW_THIRD_DAY = THIRD_DAY.replace(tzinfo=None)
    TARGET_CATEGORY = category_from_id(id=expected_id)
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "created_at",
                    "value": THIRD_DAY.isoformat(),
                    "operator_value": "is",
                },
                {
                    "column_field": "id",
                    "value": expected_id,
                    "operator_value": "is",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "==",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.created_at = ?" in compiled_str
    assert f"{sql_link_operator} {ParentModel.__tablename__}.id = ?" in compiled_str
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category = ?" in compiled_str
    )
    assert compiled.params["created_at_1"] == THIRD_DAY
    assert compiled.params["id_1"] == expected_id
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert row.parent.id == expected_id
            assert row.parent.created_at == ROW_THIRD_DAY
            assert row.category == TARGET_CATEGORY
        else:
            assert (
                row.parent.id == expected_id
                or row.parent.created_at == ROW_THIRD_DAY
                or row.category == TARGET_CATEGORY
            )


@mark.parametrize(argnames=("link_operator"), argvalues=LINK_OPERATOR_ARGVALUES)
def test_apply_ne_apply_filter_to_query_from_model_multiple_fields(
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": "!=",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": "!=",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "!=",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.id != ?" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id != ?"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category != ?" in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
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
    argnames=("operator", "link_operator"),
    argvalues=(tuple(product(("<", ">"), LINK_OPERATOR_ARGVALUES))),
)
def test_apply_gt_lt_apply_filter_to_query_from_model_multiple_fields(
    operator: str,
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": operator,
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": operator,
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": operator,
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
        in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
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
    argnames=("operator", "link_operator"),
    argvalues=(tuple(product(("<=", ">="), LINK_OPERATOR_ARGVALUES))),
)
def test_apply_ge_le_apply_filter_to_query_from_model_multiple_fields(
    operator: str,
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
    target_parent_id: int,
) -> None:
    TARGET_GROUP = calculate_grouping_id(model_id=target_parent_id)
    TARGET_CATEGORY = category_from_id(id=target_parent_id)
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": target_parent_id,
                    "operator_value": operator,
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": operator,
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": operator,
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category {operator} ?"
        in compiled_str
    )
    assert compiled.params["id_1"] == target_parent_id
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
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
    argnames=("field", "link_operator"),
    argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
)
def test_apply_is_empty_apply_filter_to_query_from_model_multiple_fields(
    field: str,
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": field,
                    "value": None,
                    "operator_value": "isEmpty",
                },
                {
                    "column_field": "grouping_id",
                    "value": None,
                    "operatorValue": "isEmpty",
                },
                {
                    "column_field": "category",
                    "value": None,
                    "operator_value": "isEmpty",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NULL" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IS NULL"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category IS NULL"
        in compiled_str
    )

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
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
    argnames=("field", "link_operator"),
    argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
)
def test_apply_is_not_empty_apply_filter_to_query_from_model_multiple_fields(
    field: str,
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": field,
                    "value": None,
                    "operator_value": "isNotEmpty",
                },
                {
                    "column_field": "grouping_id",
                    "value": None,
                    "operator_value": "isNotEmpty",
                },
                {
                    "column_field": "category",
                    "value": None,
                    "operator_value": "isNotEmpty",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE {ParentModel.__tablename__}.{field} IS NOT NULL" in compiled_str
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IS NOT NULL"
        in compiled_str
    )

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert getattr(row.parent, field) is not None
            assert row.parent.grouping_id is not None
            assert row.category is not None
        else:
            assert (
                getattr(row.parent, field) is not None
                or row.parent.grouping_id is not None
                or row.category is not None
            )


@mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_is_any_of_apply_filter_to_query_from_model_multiple_fields(
    link_operator: Optional[GridLinkOperator],
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

    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "id",
                    "value": TARGET_IDS,
                    "operator_value": "isAnyOf",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUPS,
                    "operator_value": "isAnyOf",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORIES,
                    "operator_value": "isAnyOf",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert (
        f"WHERE {ParentModel.__tablename__}.id IN (__[POSTCOMPILE_id_1])"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IN "
        + "(__[POSTCOMPILE_grouping_id_1])"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} {ChildModel.__tablename__}.category IN "
        + "(__[POSTCOMPILE_category_1])"
        in compiled_str
    )
    assert compiled.params["id_1"] == TARGET_IDS
    assert compiled.params["grouping_id_1"] == TARGET_GROUPS
    assert compiled.params["category_1"] == TARGET_CATEGORIES

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert row.parent.id in TARGET_IDS
            assert row.parent.grouping_id in TARGET_GROUPS
            assert row.category in TARGET_CATEGORIES
        else:
            assert (
                row.parent.id in TARGET_IDS
                or row.parent.grouping_id in TARGET_GROUPS
                or row.category in TARGET_CATEGORIES
            )


@mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_contains_apply_filter_to_query_from_model_multiple_fields(
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME = ParentModel.__name__
    TARGET_GROUP = 0
    TARGET_CATEGORY = Category.CATEGORY_0.value[:3]
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": TARGET_NAME,
                    "operator_value": "contains",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": "contains",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "contains",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert (
        f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ? || '%')"
        in compiled_str  # noqa
    )
    assert (
        f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE "
        + "'%' || ? || '%')"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} ({ChildModel.__tablename__}.category LIKE "
        + "'%' || ? || '%')"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert TARGET_NAME in row.parent.name
            assert row.parent.grouping_id == TARGET_GROUP
            assert TARGET_CATEGORY in row.category
        else:
            assert (
                TARGET_NAME in row.parent.name
                or row.parent.grouping_id == TARGET_GROUP
                or TARGET_CATEGORY in row.category
            )


@mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_starts_with_apply_filter_to_query_from_model_multiple_fields(
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME = ParentModel.__name__
    TARGET_GROUP = 0
    TARGET_CATEGORY = Category.CATEGORY_0.value[:3]
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": TARGET_NAME,
                    "operator_value": "startsWith",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_GROUP,
                    "operator_value": "startsWith",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "startsWith",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE ? || '%')" in compiled_str
    assert (
        f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE ? || '%')"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} ({ChildModel.__tablename__}.category LIKE ? || '%')"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME
    assert compiled.params["grouping_id_1"] == TARGET_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert row.parent.name.startswith(TARGET_NAME)
            assert str(row.parent.grouping_id).startswith(str(TARGET_GROUP))
            assert row.category.startswith(TARGET_CATEGORY)
        else:
            assert (
                row.parent.name.startswith(TARGET_NAME)
                or str(row.parent.grouping_id).startswith(str(TARGET_GROUP))
                or row.category.startswith(TARGET_CATEGORY)
            )


@mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
def test_apply_ends_with_apply_filter_to_query_from_model_multiple_fields(
    link_operator: Optional[GridLinkOperator],
    session: Session,
    joined_query: "Query[ChildModel]",
    resolver: Resolver,
) -> None:
    TARGET_NAME_AND_GROUP = "0"
    TARGET_CATEGORY = Category.CATEGORY_0.value[3:]
    model = GridFilterModel.model_validate(
        {
            "items": [
                {
                    "column_field": "name",
                    "value": TARGET_NAME_AND_GROUP,
                    "operator_value": "endsWith",
                },
                {
                    "column_field": "grouping_id",
                    "value": TARGET_NAME_AND_GROUP,
                    "operator_value": "endsWith",
                },
                {
                    "column_field": "category",
                    "value": TARGET_CATEGORY,
                    "operator_value": "endsWith",
                },
            ],
            "link_operator": link_operator,
            "quick_filter_logic_operator": None,
            "quick_filter_values": None,
        }
    )
    filtered_query = apply_filter_to_query_from_model(
        query=joined_query, model=model, resolver=resolver
    )
    compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
    compiled_str = str(compiled)
    sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
    assert f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ?)" in compiled_str
    assert (
        f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE '%' || ?)"
        in compiled_str
    )
    assert (
        f"{sql_link_operator} ({ChildModel.__tablename__}.category LIKE '%' || ?)"
        in compiled_str
    )
    assert compiled.params["name_1"] == TARGET_NAME_AND_GROUP
    assert compiled.params["grouping_id_1"] == TARGET_NAME_AND_GROUP
    assert compiled.params["category_1"] == TARGET_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = _join_filter_from(link_operator=link_operator)
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
        if link_operator == GridLinkOperator.And:
            assert row.parent.name.endswith(TARGET_NAME_AND_GROUP)
            assert str(row.parent.grouping_id).endswith(TARGET_NAME_AND_GROUP)
            assert row.category.endswith(TARGET_CATEGORY)
        else:
            assert (
                row.parent.name.endswith(TARGET_NAME_AND_GROUP)
                or str(row.parent.grouping_id).endswith(TARGET_NAME_AND_GROUP)
                or row.category.endswith(TARGET_CATEGORY)
            )
