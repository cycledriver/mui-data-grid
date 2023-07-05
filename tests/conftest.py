from datetime import datetime, timedelta
from math import floor
from typing import Generator, Union

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session

from mui.v5.integrations.sqlalchemy import Resolver
from tests.fixtures import Base, Category, ChildModel, ParentModel, category_from_id

GENERATED_PARENT_MODEL_COUNT = 400
GENERATED_CHILD_MODEL_COUNT = 100
GENERATED_PARENT_GROUPS = 10
PARENT_MODELS_PER_GROUP = floor(GENERATED_PARENT_MODEL_COUNT / GENERATED_PARENT_GROUPS)

PARENT_MODEL_RESOLVABLE_FIELDS = (
    "created_at",
    "createdat",
    "grouping_id",
    "groupingid",
    "id",
    "name",
    "null_field",
    "nullfield",
)
CHILD_MODEL_RESOLVABLE_FIELDS = (
    "category",
    "parent_id",
    "parentid",
)
RESOLVABLE_FIELDS = PARENT_MODEL_RESOLVABLE_FIELDS + CHILD_MODEL_RESOLVABLE_FIELDS
FIRST_DATE_STR = "2022-11-01T12:00:00.000000+00:00"
FIRST_DATE_DATETIME = datetime.fromisoformat(FIRST_DATE_STR)


def child_model_resolver(field: str) -> Union[int, str, Category]:
    """Resolves the model's field names to the corresponding column names.

    Args:
        field (str): The field name being resolved.

    Raises:
        ValueError: Raised when the field is not a resolvable field.
        ValueError: Raised when the resolver doesn't support the field even though
            it was considered a resolvable field. This is considered a programming
            error, but ensures MyPy is satisfied.

    Returns:
        Union[int, str]: The column (which mypy thinks is actually it's value)
    """
    normalized_field = field.lower()
    if normalized_field not in CHILD_MODEL_RESOLVABLE_FIELDS:
        raise ValueError(
            "Incorrect configuration in CHILD_MODEL_RESOLVABLE_FIELDS constant"
        )
    if normalized_field == "category":
        return ChildModel.category
    if normalized_field in {"parent_id", "parentid"}:
        return ChildModel.parent_id
    raise ValueError("Resolver does not support this field name")


def parent_model_resolver(field: str) -> Union[int, str]:
    """Resolves the model's field names to the corresponding column names.

    Args:
        field (str): The field name being resolved.

    Raises:
        ValueError: Raised when the field is not a resolvable field.
        ValueError: Raised when the resolver doesn't support the field even though
            it was considered a resolvable field. This is considered a programming
            error, but ensures MyPy is satisfied.

    Returns:
        Union[int, str]: The column (which mypy thinks is actually it's value)
    """
    normalized_field = field.lower()
    if normalized_field not in PARENT_MODEL_RESOLVABLE_FIELDS:
        raise ValueError("Incorrect configuration in RESOLVABLE_FIELDS constant")
    if normalized_field == "id":
        return ParentModel.id
    if field in {"grouping_id", "groupingid"}:
        return ParentModel.grouping_id
    if field in {"null_field", "nullfield"}:
        return ParentModel.null_field
    if field == "name":
        return ParentModel.name
    if field in {"created_at", "createdat"}:
        return ParentModel.created_at
    raise ValueError("Resolver does not support this field name")


def query_resolver(field: str) -> Union[int, str, Category]:
    normalized_field = field.lower()
    if normalized_field not in RESOLVABLE_FIELDS:
        raise ValueError(f"Ambiguous resolution key provided: {normalized_field}")
    return (
        child_model_resolver(field=field)
        if normalized_field in CHILD_MODEL_RESOLVABLE_FIELDS
        else parent_model_resolver(field=field)
    )


def calculate_grouping_id(model_id: int) -> int:
    """Calculate a grouping ID from the model's ID.

    Formula:
        floor(model_id % TOTAL_GROUPS)

    Args:
        model_id (int): The model's ID.

    Returns:
        int: The model's grouping ID.
    """
    return floor(model_id % GENERATED_PARENT_GROUPS)


@fixture(scope="session")
def parent_model_count() -> int:
    """The number of parent models that were committed to the database.

    Returns:
        int: The parent model count.
    """
    return GENERATED_PARENT_MODEL_COUNT


@fixture(scope="session")
def child_model_count() -> int:
    """The number of child models that were committed to the database.

    Returns:
        int: The child model count.
    """
    return GENERATED_PARENT_MODEL_COUNT


@fixture(scope="session")
def total_model_count(parent_model_count: int, child_model_count: int) -> int:
    """The number of total models that were committed to the database.

    Returns:
        int: The total model count.
    """
    return parent_model_count * child_model_count


@fixture(scope="session")
def parent_model_group_count() -> int:
    return GENERATED_PARENT_GROUPS


@fixture(scope="session")
def parent_models_per_group_count() -> int:
    return PARENT_MODELS_PER_GROUP


@fixture(scope="session")
def target_parent_id(parent_model_count: int) -> int:
    """The target ID of a parent model.

    Returns:
        int: The ID of the parent model to target.
    """
    return floor(parent_model_count / 2)


@fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    """The SQLAlchemy engine, after creating the metadata.

    Yields:
        Engine: The SQLAlchemy engine
    """
    engine = create_engine(url="sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@fixture(scope="session")
def session(engine: Engine, parent_model_count: int) -> Generator[Session, None, None]:
    """The SQLAlchemy session, after committing models to the database.

    Yields:
        Session: The SQLAlchemy session
    """
    session = Session(bind=engine, future=True)
    for i in range(1, parent_model_count + 1):
        group = calculate_grouping_id(model_id=i)
        created = FIRST_DATE_DATETIME + timedelta(days=i - 1)
        # faked for testing of `is` equality operator and other date-time operators
        model = ParentModel(
            created_at=created,
            name=f"{ParentModel.__name__} {i}",
            grouping_id=group,
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        for j in range(1, parent_model_count + 1):
            seen_ids = parent_model_count * j
            related_model = ChildModel(
                category=category_from_id(id=j + seen_ids), parent_id=model.id
            )
            session.add(related_model)
    session.commit()
    yield session


@fixture(scope="module")
def query(session: Session) -> Generator["Query[ParentModel]", None, None]:
    """A fixture representing a SQLAlchemy query."""
    yield (session.query(ParentModel))


@fixture(scope="module")
def joined_query(session: Session) -> Generator["Query[ChildModel]", None, None]:
    """A fixture representing a SQLAlchemy query."""
    yield (session.query(ChildModel).join(ParentModel))


@fixture(scope="module")
def resolver() -> Resolver:
    return query_resolver
