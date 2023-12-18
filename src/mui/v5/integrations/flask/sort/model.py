"""The sort model Flask integration.

Supports parsing a GridSortModel from Flask's request.args
"""

from flask import request
from pydantic import TypeAdapter
from typing_extensions import Literal

from mui.v5.grid.sort import GridSortModel

GridSortModelAdapter: TypeAdapter[GridSortModel] = TypeAdapter(GridSortModel)


def get_grid_sort_model_from_request(
    key: str = "sorl_model[]", model_format: Literal["json"] = "json"
) -> GridSortModel:
    """Retrieves a GridSortModel from request.args.

    Currently, this only supports a JSON encoded model, but in the future the plan is
    to write a custom querystring parser to support nested arguments as JavaScript
    libraries like Axios create out of the box.

    Args:
        key (str): The key in the request args where the sort model should be parsed
            from. Defaults to "sort_model[]".

    Raises:
        ValidationError: Raised when an invalid type was received.
        ValueError: Raised when an invalid model format was received.

    Returns:
        GridSortModel: The parsed sort model.
    """
    # getlist returns [] as a default when the key doesn't exist
    # https://github.com/pallets/werkzeug/blob/main/src/werkzeug/datastructures.py#L395
    if model_format == "json":
        value = request.args.get(key=key)
        return GridSortModelAdapter.validate_json(value) if value is not None else []
    raise ValueError(f"Invalid model format: {model_format}")
