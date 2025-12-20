import logging
import re
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import logger

from api.common.exceptions import InvalidOperationException
from api.core.config import settings
from api.domain.dtos.audit_logs_dto import AuditLogDto


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

def get_app_title() -> str:
    return settings.app_title or "Full-Stack FastAPI React"

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


def get_email_sharing_link(user_id: str, type: str, token: str, domain: str, tenant_id: Optional[str] = None) -> str:
    """
    Generate a complete email sharing link with token.
    """
    
    sharing_link = f"https://{domain}/{type}?user_id={user_id}&token={token}"

    if tenant_id not in (None, "None", ""):
        get_logger(__name__).info(f"tenant id in utils: {tenant_id}")
        sharing_link += f"&tenant_id={tenant_id}"
    
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


def format_bytes_to_human_readable_size(size_in_bytes: int) -> str:
    """Convert bytes into a human-readable format (KB, MB, GB, TB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB"


def is_subdomain(host: str) -> bool:
    """Check if the given host is a subdomain of the main domain."""
    main_domain = get_host_main_domain_name().lower()
    host = host.lower()
    return host != main_domain and host.endswith(f".{main_domain}")


def create_temp_file(file_name: str) -> Path:
    """Create a temporary file and return its path."""

    temp_dir = Path(tempfile.gettempdir())

    path = temp_dir / file_name

    # Ensure directory exists (temp directories always exist, but safe to include)
    path.parent.mkdir(parents=True, exist_ok=True)

    return path


async def capture_audit_log(
    log_data: AuditLogDto
) -> None:
    """Capture an audit log entry."""
    file_name = f"audit_logs_for{log_data.tenant_id if log_data.tenant_id else 'host'}_{get_utc_now().strftime('%Y%m%d')}.jsonl"
    
    file_path = create_temp_file(file_name)

    with open(file_path, "a") as f:
        f.write(log_data.model_dump_json() + "\n")
    

def get_sso_redirect_uri(provider_name: str, domain: Optional[str] = None) -> str:
    local_domain = domain if domain else get_host_main_domain_name()
    if settings.fastapi_env == "production":
        return f"https://{local_domain}/api/v1/account/sso/{provider_name}/callback"
        
    return f"http://{local_domain}:3000/api/v1/account/sso/{provider_name}/callback"
    
