"""The request module contains the model used to store parsed models."""
from typing import ClassVar

from pydantic import Field, validator

from mui.v5.grid.base import GridBaseModel, OptionalKeys
from mui.v5.grid.filter import GridFilterItem, GridFilterModel
from mui.v5.grid.link import GridLinkOperator
from mui.v5.grid.pagination import GridPaginationModel
from mui.v5.grid.sort import GridSortDirection, GridSortItem, GridSortModel


class RequestGridModels(GridBaseModel):
    """The x-data-grid models that are commonly sent to a server when requesting
    server-side enabled features.

    A grid model is a data structure used by the data grid to store the state of one
    aspect of it's features. For example, the GridFilterModel holds the data necessary
    to either filter the table's data or render the UI component responsible for
    controlling how the table's data is filtered.

    Attributes:
        filter_model (GridFilterModel): The filter model representing how to filter the
            table's data.
        pagination_model (GridPaginationModel): The pagination model representing how
            to paginate the table's data.
        sort_model (GridSortModel): The sort model representing how to sort the
            table's data.
    """

    filter_model: GridFilterModel = Field(
        default_factor=GridFilterModel,
        title="Filter Model",
        description="The filter model representing how to filter the table's data.",
        alias="filterModel",
        example=GridFilterModel(
            items=[
                GridFilterItem(
                    column_field="fieldName",
                    id=123,
                    operator_value="!=",
                    value="Field Value",
                )
            ],
            link_operator=GridLinkOperator.And,
            quick_filter_logic_operator=None,
            quick_filter_values=None,
        ),
    )
    pagination_model: GridPaginationModel = Field(
        default_factory=GridPaginationModel,
        title="Pagination Model",
        description=(
            "The pagination model representing how to paginate the table's data."
        ),
        alias="paginationModel",
        example=GridPaginationModel(page=3, page_size=30),
    )
    sort_model: GridSortModel = Field(
        default_factory=list,
        title="Sort Model",
        description="The sort model representing how to sort the table's data.",
        alias="sortModel",
        example=[GridSortItem(field="fieldName", sort=GridSortDirection.DESC)],
    )

    @validator("filter_model", pre=True)
    def ensure_filter_model_isnt_none(cls, v: object) -> object:  # noqa: B902
        """Ensures that the key used the correct default when dynamically set."""
        return GridFilterModel() if v is None else v

    @validator("pagination_model", pre=True)
    def ensure_pagination_model_isnt_none(cls, v: object) -> object:  # noqa: B902
        """Ensures that the key used the correct default when dynamically set."""
        return GridPaginationModel() if v is None else v

    @validator("sort_model", pre=True)
    def ensure_sort_model_isnt_none(cls, v: object) -> object:  # noqa: B902
        """Ensures that the key used the correct default when dynamically set."""
        return [] if v is None else v

    _optional_keys: ClassVar[OptionalKeys] = {
        ("pagination_model", "paginationModel"),
        ("sort_model", "sortModel"),
        ("filter_model", "filterModel"),
    }
