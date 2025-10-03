from typing import Literal

from fastapi import Depends, Query, APIRouter
from api.common.utils import get_date_range
from api.core.container import get_user_service
from api.domain.dtos.dashboard_dto import DashboardMetricsDto
from api.infrastructure.security.current_user import CurrentUser
from api.usecases.user_service import UserService


router = APIRouter(prefix="/dashboard") # type: ignore
router.tags = ["Dashboard"]


@router.get("/",  response_model=DashboardMetricsDto)
async def get_dashboard_metrics(
    current_user: CurrentUser,
    filter: Literal["today", "this_week", "last_3_months", "all"] = Query("all"),
    user_service: UserService = Depends(get_user_service)
):
    # Simulate fetching data based on the filter
    start, end, group_format = get_date_range(filter)

     # Base match query
    match_stage = {}
    if start:
        match_stage = {"created_at": {"$gte": start, "$lte": end}}

     # Aggregation pipeline for time series
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": group_format, "date": "$created_at"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "time_or_date": "$_id",
                "count": "$count",
                "_id": 0
            }
        }
    ]

    timeseries =  await user_service.aggregate(pipeline)
    total_users = await user_service.total_count()
    joined_users = await user_service.total_count(match_stage) if match_stage else total_users

    data = {
        "filter": filter,
        "joined_users": joined_users,
        "total_users": total_users,
        "timeseries": timeseries
    }
    return DashboardMetricsDto(**data)
