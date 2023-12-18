"""The model module contains the Grid Pagination Model Flask integration.

Supports parsing a GridPaginationModel from Flask's request.args
"""

from typing import Optional

from flask import request

from mui.v5.grid.pagination import GridPaginationModel


def get_grid_pagination_model_from_request(
    key: Optional[str] = None,
) -> GridPaginationModel:
    """Retrieves a GridPaginationModel from request.args.

    Args:
        key (str): The key in the request args where the pagination model should be
            parsed from, if it is encoded as an object rather than inline.
            If set, a URL-encoded JSON object will attempt to be retrieved from the
            key, otherwise the arguments will be located in the root of the query
            string. Defaults to None.

    Example Query Strings:
        Camel case:
            Default structure:
                /api/v1/endpoint?page=0&pageSize=15
            Key-based structure:
                /api/v1/endpoint?pageModel=%7B%22page%22%3A%200%2C%20%22pageSize%22%3A%2015%7D
        Snake case:
            Default structure:
                /api/v1/endpoint?page=0&page_size=15
            Key-based structure:
                /api/v1/endpoint?page_model=%7B%22page%22%3A%200%2C%20%22page_size%22%3A%2015%7D

    Raises:
        ValidationError: Raised when an invalid type was received.

    Returns:
        GridSortModel: The parsed sort model.
    """
    # get swallows `KeyError` and `ValueError`, which is why we don't allow this to
    # raise an exception
    # https://github.com/pallets/werkzeug/blob/main/src/werkzeug/datastructures.py#L919
    obj = (
        request.args.get(key=key, default=GridPaginationModel())
        if isinstance(key, str)
        else request.args
    )
    if isinstance(obj, str):
        return GridPaginationModel.model_validate_json(obj)
    if isinstance(obj, GridPaginationModel):
        return obj
    return GridPaginationModel.model_validate(obj)
