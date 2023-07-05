"""The factory module contains the data type used by a factory function.

A factory is responsible for taking a SQLAlchemy model and converting it into another
data type / structure.
"""
from typing import Callable, TypeVar

from typing_extensions import TypeAlias

_SQLAlchemyInstance = TypeVar("_SQLAlchemyInstance")
_FactoryReturnType = TypeVar("_FactoryReturnType")

Factory: TypeAlias = Callable[[_SQLAlchemyInstance], _FactoryReturnType]
