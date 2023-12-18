"""The resolver module holds details about the resolver callable.

A resolver is used to resolve a data grid column name to a column or other sortable or
filterable SQLAlchemy model.
"""

from mui.v6.integrations.sqlalchemy.resolver.types import Resolver

# isort: unique-list
__all__ = ["Resolver"]
