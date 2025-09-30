from typing import Literal

from pydantic import BaseModel


class TimeSeriesDto(BaseModel):
    time_or_date: str
    count: int
    
class DashboardMetricsDto(BaseModel):
    filter: Literal["today", "this_week", "last_3_months", "all"]
    joined_users: int
    total_users: int
    timeseries: list[TimeSeriesDto]


