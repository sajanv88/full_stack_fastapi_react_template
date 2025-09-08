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

def get_tenancy_strategy() -> str:
    return os.getenv("MULTI_TENANCY_STRATEGY", "none").lower()


# Simple utility function to store file. Later, will configure AWS S3, Azure storage etc..
def save_file(file, upload_dir="app/ui/assets/user_profiles"):
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    print(f"File saved at {file_location}")
    return file_location
