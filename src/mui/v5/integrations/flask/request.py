"""The request grid model Flask integration.

Supports parsing the filter, pagination, and sort models from Flask's request.args."""
from typing import Optional

from typing_extensions import Literal

from mui.v5.grid.request import RequestGridModels
from mui.v5.integrations.flask.filter.model import get_grid_filter_model_from_request
from mui.v5.integrations.flask.pagination.model import (
    get_grid_pagination_model_from_request,
)
from mui.v5.integrations.flask.sort.model import get_grid_sort_model_from_request


def get_grid_models_from_request(
    sort_model_key: str = "sort_model[]",
    filter_model_key: str = "filter_model",
    pagination_model_key: Optional[str] = None,
    sort_model_format: Literal["json"] = "json",
    filter_model_format: Literal["json"] = "json",
) -> RequestGridModels:
    """Parses the filter, sort, and pagination models from the request.

    Args:
        sort_model_key (str, optional): The key to retrieve the grid sort model from in
            the request.args. The sort model is URL-encoded JSON list of grid sort
            items. Defaults to "sort_model[]".
        filter_model_key (str, optional): The key to retrieve the grid filter model
            from in the request.args. The filter model is URL-encoded JSON object with
            the shape of a grid filter model. Defaults to "filter_model".
            Example query string:
        pagination_model_key (str | None, optional): The key to retrieve the grid
            pagination model from in the request.args. The pagination model may either
            be provided in the query string directly or as a URL-encoded JSON object.
                If the provided key is None, the former will be assumed, otherwise the
                latter. Defaults to None.
                Example None query string:
                    ?page=0&pageSize=12
                Example "pagination_model" query string:
                    ?pagination_model=%7B%22page%22%3A%200%2C%20%22pageSize%22%3A%2015%7D

    Raises:
        ValidationError: Raised when an invalid or partial data structure is received
            that doesn't meet the minimum validation requirements.

    Returns:
        RequestGridModels: The located grid models.
    """
    return RequestGridModels(
        filter_model=get_grid_filter_model_from_request(
            key=filter_model_key, model_format=filter_model_format
        ),
        sort_model=get_grid_sort_model_from_request(
            key=sort_model_key, model_format=sort_model_format
        ),
        pagination_model=get_grid_pagination_model_from_request(
            key=pagination_model_key
        ),
    )
