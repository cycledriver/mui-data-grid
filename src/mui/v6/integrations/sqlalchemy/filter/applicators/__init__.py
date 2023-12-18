"""The applicators module contains the functions that apply operators to columns.

These generally take two values, the column and the value and apply the operator
in a SQLAlchemy compatible way, to the query.
"""

from mui.v6.integrations.sqlalchemy.filter.applicators.after import apply_after_operator
from mui.v6.integrations.sqlalchemy.filter.applicators.basic import (
    SUPPORTED_BASIC_OPERATORS,
    apply_basic_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.before import (
    apply_before_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.contains import (
    apply_contains_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.endswith import (
    apply_endswith_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.is_ import apply_is_operator
from mui.v6.integrations.sqlalchemy.filter.applicators.is_any_of import (
    apply_is_any_of_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.is_empty import (
    apply_is_empty_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.is_not_empty import (
    apply_is_not_empty_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.not_ import apply_not_operator
from mui.v6.integrations.sqlalchemy.filter.applicators.on_or_after import (
    apply_on_or_after_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.on_or_before import (
    apply_on_or_before_operator,
)
from mui.v6.integrations.sqlalchemy.filter.applicators.startswith import (
    apply_startswith_operator,
)

# isort: unique-list
__all__ = [
    "SUPPORTED_BASIC_OPERATORS",
    "apply_after_operator",
    "apply_basic_operator",
    "apply_before_operator",
    "apply_contains_operator",
    "apply_endswith_operator",
    "apply_is_any_of_operator",
    "apply_is_empty_operator",
    "apply_is_not_empty_operator",
    "apply_is_operator",
    "apply_not_operator",
    "apply_on_or_after_operator",
    "apply_on_or_before_operator",
    "apply_startswith_operator",
]
