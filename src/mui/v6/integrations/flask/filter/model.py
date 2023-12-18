"""The model module contains the Grid Filter Model Flask integration.

Supports parsing a GridFilterModel from Flask's request.args
"""

from flask import request
from typing_extensions import Literal

from mui.v6.grid.filter import GridFilterModel


def get_grid_filter_model_from_request(
    key: str = "filter_model", model_format: Literal["json"] = "json"
) -> GridFilterModel:
    """Retrieves a GridFilterModel from request.args.

    Currently, this only supports a JSON encoded model, but in the future the plan is
    to write a custom querystring parser to support nested arguments as JavaScript
    libraries like Axios create out of the box.

    Args:
        key (str): The key in the request args where the filter model should be parsed
            from. Defaults to "filter_model".

    Raises:
        ValidationError: Raised when an invalid type was received.
        ValueError: Raised when an invalid model format was received.

    Returns:
        GridFilterModel: The parsed filter model, if found. If no filter model is
            found, an empty GridFilterModel instance is returned.
    """
    # get swallows `KeyError` and `ValueError`, which is why we don't allow this to
    # raise an exception
    # https://github.com/pallets/werkzeug/blob/main/src/werkzeug/datastructures.py#L919
    if model_format == "json":
        # https://pydantic-docs.helpmanual.io/usage/models/#helper-functions
        return request.args.get(
            key=key, default=GridFilterModel(), type=GridFilterModel.model_validate_json
        )
    raise ValueError(f"Unsupported model format: {model_format}")
