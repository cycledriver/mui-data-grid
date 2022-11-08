from datetime import timedelta
from typing import Optional

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
    return "AND" if link_operator == GridLinkOperator.And else "OR"


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
    model = GridFilterModel.parse_obj(
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
    join_filter = and_ if link_operator == GridLinkOperator.And else or_
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
    EXPECTED_CATEGORY = category_from_id(id=expected_id)
    model = GridFilterModel.parse_obj(
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
                    "value": EXPECTED_CATEGORY,
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
    assert compiled.params["category_1"] == EXPECTED_CATEGORY

    rows = filtered_query.all()
    row_count = filtered_query.count()
    join_filter = and_ if link_operator == GridLinkOperator.And else or_
    expected_row_count = (
        session.query(ChildModel)
        .join(ParentModel)
        .filter(
            join_filter(
                ParentModel.created_at == THIRD_DAY,
                ParentModel.id == expected_id,
                ChildModel.category == EXPECTED_CATEGORY,
            )
        )
        .count()
    )
    assert row_count == expected_row_count
    for row in rows:
        if link_operator == GridLinkOperator.And:
            assert row.parent.id == expected_id
            assert row.parent.created_at == ROW_THIRD_DAY
            assert row.category == EXPECTED_CATEGORY
        else:
            assert (
                row.parent.id == expected_id
                or row.parent.created_at == ROW_THIRD_DAY
                or row.category == EXPECTED_CATEGORY
            )


# @mark.parametrize(argnames=("link_operator"), argvalues=LINK_OPERATOR_ARGVALUES)
# def test_apply_ne_apply_filter_to_query_from_model_multiple_fields(
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     TARGET_ID = 300
#     TARGET_GROUP = calculate_grouping_id(model_id=TARGET_ID)
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "id",
#                     "value": TARGET_ID,
#                     "operator_value": "!=",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": TARGET_GROUP,
#                     "operator_value": "!=",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE {ParentModel.__tablename__}.id != ?" in compiled_str
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id != ?"
#         in compiled_str
#     )
#     assert compiled.params["id_1"] == TARGET_ID
#     assert compiled.params["grouping_id_1"] == TARGET_GROUP

#     rows = filtered_query.all()
#     if link_operator == GridLinkOperator.And:
#         assert len(rows) == 900
#         assert all(row.id != TARGET_ID for row in rows)
#         assert all(row.grouping_id != TARGET_GROUP for row in rows)
#     else:
#         # because it's an `OR` clause, the != id ends up being the only
#         # thing that evaluates, as it has both the ID and the group, while
#         # the others at least have a differing ID.
#         assert len(rows) == 999
#         assert all(
#             row.id != TARGET_ID or row.grouping_id != TARGET_GROUP for row in rows
#         )


# @mark.parametrize(
#     argnames=("operator", "link_operator"),
#     argvalues=(tuple(product(("<", ">"), LINK_OPERATOR_ARGVALUES))),
# )
# def test_apply_gt_lt_apply_filter_to_query_from_model_multiple_fields(
#     operator: str,
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     TARGET_ID = 500
#     TARGET_GROUP = calculate_grouping_id(model_id=TARGET_ID)
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "id",
#                     "value": TARGET_ID,
#                     "operator_value": operator,
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": TARGET_GROUP,
#                     "operator_value": operator,
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
#         in compiled_str
#     )
#     assert compiled.params["id_1"] == TARGET_ID
#     assert compiled.params["grouping_id_1"] == TARGET_GROUP

#     rows = filtered_query.all()
#     if operator == ">":
#         if link_operator == GridLinkOperator.And:
#             assert len(rows) == 401
#             assert all(row.id > TARGET_ID for row in rows)  # pyright: ignore
#             assert all(
#                 row.grouping_id > TARGET_GROUP for row in rows
#             )  # pyright: ignore
#         else:
#             assert len(rows) == 500
#             assert all(
#                 row.id > TARGET_ID or row.grouping_id > TARGET_GROUP for row in rows
#             )  # pyright: ignore
#     else:
#         assert len(rows) == 499
#         if link_operator == GridLinkOperator.And:
#             assert all(row.id < TARGET_ID for row in rows)  # pyright: ignore
#             assert all(
#                 row.grouping_id < TARGET_GROUP for row in rows
#             )  # pyright: ignore
#         else:
#             assert all(
#                 row.id < TARGET_ID or row.grouping_id < TARGET_GROUP for row in rows
#             )  # pyright: ignore


# @mark.parametrize(
#     argnames=("operator", "link_operator"),
#     argvalues=(tuple(product(("<=", ">="), LINK_OPERATOR_ARGVALUES))),
# )
# def test_apply_ge_le_apply_filter_to_query_from_model_multiple_fields(
#     operator: str,
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     TARGET_ID = 500
#     TARGET_GROUP = calculate_grouping_id(model_id=TARGET_ID)
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "id",
#                     "value": TARGET_ID,
#                     "operator_value": operator,
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": TARGET_GROUP,
#                     "operator_value": operator,
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE {ParentModel.__tablename__}.id {operator} ?" in compiled_str
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id {operator} ?"
#         in compiled_str
#     )
#     assert compiled.params["id_1"] == TARGET_ID
#     assert compiled.params["grouping_id_1"] == TARGET_GROUP

#     rows = filtered_query.all()
#     row_count = len(rows)
#     if operator == ">=":
#         assert row_count == 501
#         if link_operator == GridLinkOperator.And:
#             assert all(row.id >= TARGET_ID for row in rows)
#             assert all(
#                 row.grouping_id >= TARGET_GROUP for row in rows
#             )  # pyright: ignore
#         else:
#             assert all(
#                 row.id >= TARGET_ID or row.grouping_id >= TARGET_GROUP for row in rows
#             )
#     else:
#         if link_operator == GridLinkOperator.And:
#             assert row_count == 500
#             assert all(row.id <= TARGET_ID for row in rows)
#             assert all(
#                 row.grouping_id <= TARGET_GROUP for row in rows
#             )  # pyright: ignore
#         else:
#             assert row_count == 599
#             assert all(
#                 row.id <= TARGET_ID or row.grouping_id <= TARGET_GROUP for row in rows
#             )  # pyright: ignore


# @mark.parametrize(
#     argnames=("field", "link_operator"),
#     argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
# )
# def test_apply_is_empty_apply_filter_to_query_from_model_multiple_fields(
#     field: str,
#     link_operator: Optional[GridLinkOperator],
#     parent_model_count: int,
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": field,
#                     "value": None,
#                     "operator_value": "isEmpty",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": None,
#                     "operatorValue": "isEmpty",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE {ParentModel.__tablename__}.{field} IS NULL" in compiled_str
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IS NULL"
#         in compiled_str
#     )

#     rows = filtered_query.all()
#     row_count = len(rows)
#     if link_operator == GridLinkOperator.And:
#         # always zero because grouping_id is never empty
#         assert row_count == 0
#         assert all(row.null_field is None for row in rows)
#         assert all(row.grouping_id is None for row in rows)
#     else:
#         if field == "null_field":
#             assert row_count == parent_model_count
#         else:
#             assert row_count == 0
#         assert all(row.null_field is None or row.grouping_id is None for row in rows)


# @mark.parametrize(
#     argnames=("field", "link_operator"),
#     argvalues=tuple(product(("id", "null_field"), LINK_OPERATOR_ARGVALUES)),
# )
# def test_apply_is_not_empty_apply_filter_to_query_from_model_multiple_fields(
#     field: str,
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     parent_model_count: int,
#     resolver: Resolver,
# ) -> None:
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": field,
#                     "value": None,
#                     "operator_value": "isNotEmpty",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": None,
#                     "operator_value": "isNotEmpty",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE {ParentModel.__tablename__}.{field} IS NOT NULL" in compiled_str
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IS NOT NULL"
#         in compiled_str
#     )

#     rows = filtered_query.all()
#     row_count = len(rows)
#     if link_operator == GridLinkOperator.And:
#         if field == "id":
#             assert row_count == parent_model_count
#         elif field == "null_field":
#             assert row_count == 0
#         assert all(row.grouping_id is not None for row in rows)
#     else:
#         # Or branch
#         assert row_count == parent_model_count
#         assert all(
#             row.null_field is not None or row.grouping_id is not None for row in rows
#         )


# @mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
# def test_apply_is_any_of_apply_filter_to_query_from_model_multiple_fields(
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     TARGET_IDS = [1, 2, 3]
#     TARGET_GROUPS = list(
#         {calculate_grouping_id(model_id=TARGET_ID) for TARGET_ID in TARGET_IDS}
#     )

#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "id",
#                     "value": TARGET_IDS,
#                     "operator_value": "isAnyOf",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": TARGET_GROUPS,
#                     "operator_value": "isAnyOf",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert (
#         f"WHERE {ParentModel.__tablename__}.id IN (__[POSTCOMPILE_id_1])"
#         in compiled_str
#     )
#     assert (
#         f"{sql_link_operator} {ParentModel.__tablename__}.grouping_id IN "
#         + "(__[POSTCOMPILE_grouping_id_1])"
#         in compiled_str
#     )
#     assert compiled.params["id_1"] == [1, 2, 3]
#     assert compiled.params["grouping_id_1"] == [0]

#     rows = filtered_query.all()
#     if link_operator == GridLinkOperator.And:
#         assert len(rows) == len(TARGET_IDS)
#         assert all(row.id in TARGET_IDS for row in rows)
#         assert all(row.grouping_id in TARGET_GROUPS for row in rows)
#     else:
#         assert len(rows) == 99
#         assert all(
#             row.id in TARGET_IDS or row.grouping_id in TARGET_GROUPS for row in rows
#         )


# @mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
# def test_apply_contains_apply_filter_to_query_from_model_multiple_fields(
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     parent_model_count: int,
#     resolver: Resolver,
# ) -> None:
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "name",
#                     "value": ParentModel.__name__,
#                     "operator_value": "contains",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": 0,
#                     "operator_value": "contains",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert (
#         f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ? || '%')" in compiled_str # noqa
#     )
#     assert (
#         f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE "
#         + "'%' || ? || '%')"
#         in compiled_str
#     )
#     assert compiled.params["name_1"] == ParentModel.__name__
#     assert compiled.params["grouping_id_1"] == 0

#     rows = filtered_query.all()
#     if link_operator == GridLinkOperator.And:
#         assert len(rows) == parent_model_count / 10
#         assert all(ParentModel.__name__ in row.name for row in rows)
#         assert all("0" in str(row.grouping_id) for row in rows)
#     else:
#         # all have the name
#         assert len(rows) == parent_model_count
#         assert all(
#             ParentModel.__name__ in row.name or "0" in str(row.grouping_id)
#             for row in rows
#         )


# @mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
# def test_apply_starts_with_apply_filter_to_query_from_model_multiple_fields(
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     parent_model_count: int,
#     resolver: Resolver,
# ) -> None:
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "name",
#                     "value": ParentModel.__name__,
#                     "operator_value": "startsWith",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": 0,
#                     "operator_value": "startsWith",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE ({ParentModel.__tablename__}.name LIKE ? || '%')" in compiled_str
#     assert (
#         f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE ? || '%')"
#         in compiled_str
#     )
#     assert compiled.params["name_1"] == ParentModel.__name__
#     assert compiled.params["grouping_id_1"] == 0

#     rows = filtered_query.all()
#     if link_operator == GridLinkOperator.And:
#         groups = parent_model_count / 10
#         assert len(rows) == (groups - 1)
#         assert all(row.name.startswith(ParentModel.__name__) for row in rows)
#         assert all(str(row.grouping_id).startswith("0") for row in rows)
#     else:
#         assert len(rows) == parent_model_count
#         assert all(
#             row.name.startswith(ParentModel.__name__)
#             or str(row.grouping_id).startswith("0")
#             for row in rows
#         )


# @mark.parametrize(argnames=("link_operator"), argvalues=(LINK_OPERATOR_ARGVALUES))
# def test_apply_ends_with_apply_filter_to_query_from_model_multiple_fields(
#     link_operator: Optional[GridLinkOperator],
#     query: "Query[ParentModel]",
#     resolver: Resolver,
# ) -> None:
#     VALUE = "0"
#     model = GridFilterModel.parse_obj(
#         {
#             "items": [
#                 {
#                     "column_field": "name",
#                     "value": VALUE,
#                     "operator_value": "endsWith",
#                 },
#                 {
#                     "column_field": "grouping_id",
#                     "value": VALUE,
#                     "operator_value": "endsWith",
#                 },
#             ],
#             "link_operator": link_operator,
#             "quick_filter_logic_operator": None,
#             "quick_filter_values": None,
#         }
#     )
#     filtered_query = apply_filter_to_query_from_model(
#         query=query, model=model, resolver=resolver
#     )
#     compiled = filtered_query.statement.compile(dialect=sqlite.dialect())
#     compiled_str = str(compiled)
#     sql_link_operator = _sql_link_operator_from(link_operator=link_operator)
#     assert f"WHERE ({ParentModel.__tablename__}.name LIKE '%' || ?)" in compiled_str
#     assert (
#         f"{sql_link_operator} ({ParentModel.__tablename__}.grouping_id LIKE '%' || ?)"
#         in compiled_str
#     )
#     assert compiled.params["name_1"] == VALUE
#     assert compiled.params["grouping_id_1"] == VALUE

#     rows = filtered_query.all()
#     if link_operator == GridLinkOperator.And:
#         assert len(rows) == 10
#         assert all(row.name.endswith(VALUE) for row in rows)
#         assert all(str(row.grouping_id).endswith(VALUE) for row in rows)
#     else:
#         assert len(rows) == 190
#         assert all(
#             row.name.endswith(VALUE) or str(row.grouping_id).endswith(VALUE)
#             for row in rows
#         )
