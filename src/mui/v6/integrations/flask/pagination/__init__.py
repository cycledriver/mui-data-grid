"""The pagination module contains the pagination model integration for Flask."""

from mui.v6.integrations.flask.pagination.model import (
    get_grid_pagination_model_from_request,
)

# isort: unique-list
__all__ = ["get_grid_pagination_model_from_request"]
