from typing_extensions import Annotated, Literal
from fastapi import Depends, APIRouter, status, HTTPException, Query
from pydantic import BaseModel
from app.core.db import user_collection
from app.core.utils import get_date_range
from app.api.routes.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard")
router.tags = ["Dashboard"]

class DashboardMetrics(BaseModel):
    filter: Literal["today", "this_week", "last_3_months", "all"]
    joined_users: int
    total_users: int
    timeseries: list[dict]


@router.get("/",  response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
    filter: Literal["today", "this_week", "last_3_months", "all"] = Query("all")):
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

    cursor = await user_collection.aggregate(pipeline)
    timeseries = [doc async for doc in cursor]

    total_users = await user_collection.count_documents({})
    joined_users = await user_collection.count_documents(match_stage) if match_stage else total_users

    data = {
        "filter": filter,
        "joined_users": joined_users,
        "total_users": total_users,
        "timeseries": timeseries
    }
    return DashboardMetrics(**data)
