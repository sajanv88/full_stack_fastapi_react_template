import logging
from datetime import datetime, timezone
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



PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]")
def validate_password(password: str) -> str:
    """Validate password strength. Raises InvalidOperationException if invalid."""
    if not PASSWORD_REGEX.match(password):
        raise InvalidOperationException("Password must be at least 8 characters long, include uppercase and lowercase letters, a number, and a special character.")
    return password


