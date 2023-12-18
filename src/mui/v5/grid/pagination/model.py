"""The pagination model is designed to abstract the pagination-related data grid state.
"""

from pydantic import AliasChoices, Field, PositiveInt

from mui.v5.grid.base import GridBaseModel


class GridPaginationModel(GridBaseModel):
    """A normalized pagination model for Material-UI's data grid.

    Attributes:
        page (int): The current page number. Defaults to 0. First page is page zero.
        page_size (int): The size of each page. Defaults to 15.
    """

    page: int = Field(
        default=0,
        title="Starting Page",
        description="The starting page number (beginning with 0).",
        gt=-1,
        examples=[0],
    )
    page_size: PositiveInt = Field(
        default=15,
        title="Page Size",
        description="The size of each results page",
        validation_alias=AliasChoices("page_size", "pageSize"),
        examples=[15],
    )

    @property
    def offset(self) -> int:
        """Calculates the SQL offset.

        A SQL offset is the number of rows to skip before the first result. This is
        created by multiplying the page number (page 0 being the first) with the page
        size, or number of rows per page).

        Returns:
            int: The page offset
        """
        return self.page * self.page_size
