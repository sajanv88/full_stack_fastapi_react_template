from datetime import datetime, timedelta
import os

def get_date_range(filter_type: str):
    """Return (start, end, group_format) based on filter type"""
    now = datetime.utcnow()
    if filter_type == "today":
        start = datetime(now.year, now.month, now.day)
        group_format = "%H:00"  # group by hour
    elif filter_type == "this_week":
        start = now - timedelta(days=now.weekday())  # Monday start
        start = datetime(start.year, start.month, start.day)
        group_format = "%Y-%m-%d"  # group by day
    elif filter_type == "last_3_months":
        start = now - timedelta(days=90)
        group_format = "%Y-%m"  # group by month
    else:
        start = None
        group_format = "%Y-%m-%d"
    return start, now, group_format


def is_tenancy_enabled() -> bool:
    multi_tenancy_strategy = os.getenv("MULTI_TENANCY_STRATEGY", "none").lower()
    return multi_tenancy_strategy != "none"