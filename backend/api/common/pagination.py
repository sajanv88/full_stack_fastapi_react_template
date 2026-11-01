from typing import Annotated

from fastapi import Query

MAX_PAGE_SIZE = 1000

Skip = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]
