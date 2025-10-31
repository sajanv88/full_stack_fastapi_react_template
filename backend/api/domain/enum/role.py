from enum import Enum


class RoleType(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    HOST = "host"
    BILLING_MANAGER = "billing_manager"