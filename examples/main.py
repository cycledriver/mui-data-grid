#!/usr/bin/env python
"""An example script demonstrating how to use this library."""
# examples/main.py

from math import floor
from typing import Dict

import sqlalchemy as sa
from flask import Flask, jsonify
from flask.wrappers import Response
from sqlalchemy.orm import DeclarativeMeta, Mapped, registry, sessionmaker

from mui.v5.integrations.flask import get_grid_models_from_request
from mui.v5.integrations.sqlalchemy import apply_request_grid_models_to_query

app = Flask(__name__)
engine = sa.create_engine(url="sqlite:///:memory:")
Session = sessionmaker(engine)

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    """The base class for all SQLAlchemy models."""

    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor


class ExampleModel(Base):
    """An example SQLAlchemy model."""

    __tablename__ = "example_models"

    id: Mapped[int] = sa.Column(  # pyright: ignore
        sa.Integer(),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="The primary key identifier.",
    )
    group_number: Mapped[int] = sa.Column(  # pyright: ignore
        sa.Integer(), nullable=False, comment="A grouping identifier"
    )

    def dict(self) -> Dict[str, int]:
        """Converts the model into a dictionary.

        Returns:
            Dict[str, int]: The mapping of attribute names to values.
        """
        return {"id": self.id, "groupNumber": self.group_number}

    @staticmethod
    def dict_factory(model: "ExampleModel") -> Dict[str, int]:
        """A factory function for converting the model to a dictionary.

        Args:
            model (ExampleModel): The model to convert.

        Returns:
            Dict[str, int]: The dictionary representation of the model.
        """
        return model.dict()


def example_model_resolver(field: str) -> int:
    """The column resolver for the example model class.

    Args:
        field (str): The attribute / field name, as specified in the user-interface.

    Raises:
        ValueError: Raised when a field is provided which is not resolvable.

    Returns:
        int: Returns the column field. The type hint incorrectly maps the Column type
            to the data-type of the Column because of SQLAlchemy's MyPy plugin. This
            can safely be ignore, though is a bit of a confusing oddity.
    """
    normalized_field = field.lower()
    if normalized_field == "id":
        return ExampleModel.id
    elif normalized_field in {"group_number", "groupnumber"}:
        return ExampleModel.group_number
    raise ValueError("Invalid field requested")


MODELS_TO_CREATE = 100
GROUPS_TO_CREATE = 4
FILTER_MODEL_KEY = "filter_model"
SORT_MODEL_KEY = "sort_model[]"
PAGINATION_MODEL_KEY = None  # stored inline in the query string, not encoded as an obj


def prepare_db() -> None:
    """Creates the database structure and seeds it with basic data for
    querying purposes.
    """
    Base.metadata.create_all(bind=engine)
    with Session() as session:
        for i in range(MODELS_TO_CREATE + 1):
            group = floor(i % GROUPS_TO_CREATE)
            model = ExampleModel(group_number=group)
            session.add(model)
        session.commit()


def cleanup_db() -> None:
    """Not strictly needed because we're using an in-memory database"""
    Base.metadata.drop_all(bind=engine)


@app.route("/echo")
def print_sorted_details() -> Response:
    """This method will act as an echo server for the caller.

    Query Parameters:
        filter_model: The Material-UI Data Grid Filter Model.
        page: The current page number.
        pageSize: The size of each page.
        sort_model[]: The Material-UI Data Grid Sort Model.
    """
    models = get_grid_models_from_request(
        filter_model_key=FILTER_MODEL_KEY,
        pagination_model_key=PAGINATION_MODEL_KEY,
        sort_model_key=SORT_MODEL_KEY,
    )
    return jsonify(
        {
            # sort_model is a list[GridSortItem]
            SORT_MODEL_KEY: [model.model_dump() for model in models.sort_model],
            # filter_model is GridFilterModel
            FILTER_MODEL_KEY: models.filter_model.model_dump(),
            # pagination_model is a GridPaginationModel
            # providing a consistent interface to pagination parameters
            PAGINATION_MODEL_KEY: models.pagination_model,
        }
    )


@app.route("/query")
def print_query_results() -> Response:
    """This method will act as an echo server for the caller.

    Query Parameters:
        filter_model: The Material-UI Data Grid Filter Model.
        page: The current page number.
        pageSize: The size of each page.
        sort_model[]: The Material-UI Data Grid Sort Model.
    """
    models = get_grid_models_from_request(
        filter_model_key=FILTER_MODEL_KEY,
        pagination_model_key=PAGINATION_MODEL_KEY,
        sort_model_key=SORT_MODEL_KEY,
    )
    session = Session()
    try:
        base_query = session.query(ExampleModel)
        dg_query = apply_request_grid_models_to_query(
            query=base_query,
            request_model=models,
            column_resolver=example_model_resolver,
        )
        total = dg_query.total()
        return jsonify(
            {
                "items": dg_query.items(factory=ExampleModel.dict_factory),
                "page": dg_query.page,
                "pageSize": dg_query.page_size,
                "pages": dg_query.pages(total=total),
                "total": total,
            }
        )
    finally:
        session.close()


if __name__ == "__main__":
    prepare_db()
    try:
        app.run()
    finally:
        cleanup_db()
