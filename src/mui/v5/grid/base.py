"""The base module contains the base pydantic model used throughout mui-data-grid."""

from collections.abc import MutableMapping
from typing import AbstractSet, ClassVar, Sequence

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import TypeAlias

OptionalKeys: TypeAlias = AbstractSet[Sequence[str]]


class GridBaseModel(BaseModel):
    """The base model for all mui-data-grid pydantic models.

    Attributes:
        _optional_keys: Keys which may not be present in the incoming structures.
            This feature is used to represent `?` parameters in TypeScript interfaces.
    """

    _optional_keys: ClassVar[OptionalKeys] = set()

    @model_validator(mode="before")
    @classmethod
    def ensure_optional_keys_exist(cls, haystack: object) -> object:
        """A validator that runs before validating the attribute's values.

        This validator ensures that at least one key per tuple exists if the received
        object is a mutable mapping, such as a dictionary.

        Arguments:
            haystack (object): The haystack, or incoming value, being evaluated to
                identify if it has at least one of the optional keys (needles).
                The name comes from looking for a needle in a haystack.

        Returns:
            object: The haystack, with the keys added to the mapping, if it was an
                object we could mutate.
        """
        if isinstance(haystack, MutableMapping):
            for keys in cls._optional_keys:
                found_needle = any(needle in haystack for needle in keys)
                if not found_needle:
                    key = keys[0]
                    haystack[key] = None
        return haystack

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
