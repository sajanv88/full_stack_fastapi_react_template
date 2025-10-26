
from enum import Enum


class Permission(str, Enum):
    
    FULL_ACCESS = "full:access"

    USER_READ_AND_WRITE_ONLY = "user:read_and_write_only"
    USER_DELETE_ONLY = "user:delete_only"
    USER_SELF_READ_AND_WRITE_ONLY = "user:self_read_and_write_only"
    USER_ROLE_ASSIGN_OR_REMOVE_ONLY = "role:assign_or_remove_only"
    USER_VIEW_ONLY = "user:view_only"


    ROLE_VIEW_ONLY = "role:view_only"
    ROLE_READ_AND_WRITE_ONLY = "role:read_and_write_only"
    ROLE_DELETE_ONLY = "role:delete_only"
    ROLE_PERMISSION_READ_AND_WRITE_ONLY = "role:permission_read_and_write_only"

    
    HOST_MANAGE_TENANTS = "host:manage_tenants"
    MANAGE_STORAGE_SETTINGS = "manage:storage_settings"
    
    MANAGE_TENANT_SETTINGS = "manage:tenant_settings"

    MANAGE_BILLING = "manage:billing"
    MANAGE_PAYMENTS_SETTINGS = "manage:payments_settings"
    MANAGE_PRODUCTS_AND_PRICING = "manage:products_and_pricing"