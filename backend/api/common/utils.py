import logging
from datetime import datetime, timezone, timedelta
import re
from api.common.exceptions import InvalidOperationException
from api.core.config import settings

def get_utc_now():
    return datetime.now(timezone.utc)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def is_tenancy_enabled() -> bool:
    return settings.multi_tenancy_strategy != "none"

def get_tenancy_strategy() -> str:
    return settings.multi_tenancy_strategy.lower()

def get_host_main_domain_name() -> str:
    return settings.host_main_domain.lower()

def get_app_environment() -> str:
    return settings.fastapi_env.lower()

def is_production_environment() -> bool:
    return get_app_environment() == "production"

def is_development_environment() -> bool:
    return get_app_environment() == "development"


PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]")
def validate_password(password: str) -> str:
    """Validate password strength. Raises InvalidOperationException if invalid."""
    if not PASSWORD_REGEX.match(password):
        raise InvalidOperationException("Password must be at least 8 characters long, include uppercase and lowercase letters, a number, and a special character.")
    return password


def get_email_sharing_link(user_id: str, type: str, token: str) -> str:
    """
    Generate a complete email sharing link with token.
    """
    sharing_link = f"{settings.api_endpoint_base}/v1/account/{type}?user_id={user_id}&token={token}"
    return sharing_link


def get_date_range(filter_type: str):
    """Return (start, end, group_format) based on filter type"""
    now = get_utc_now()
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
