"""The types module holds types related to the resolver callable.

A resolver is used to resolve a data grid column name to a column or other sortable or
filterable SQLAlchemy model.
"""
from typing import Any, Callable

from typing_extensions import TypeAlias

Resolver: TypeAlias = Callable[[str], Any]
