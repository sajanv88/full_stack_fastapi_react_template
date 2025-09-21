# Keep only domain-specific exceptions here

from api.common.exceptions import InvalidOperationException, NotFoundException, ConflictException

class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__("User", user_id)

class EmailAlreadyExistsException(ConflictException):
    def __init__(self, email: str):
        super().__init__("User", email)


class InvalidSubdomainException(InvalidOperationException):
    def __init__(self, subdomain: str):
        message = f"Subdomain '{subdomain}' is invalid format (3–63 chars, letters/digits/hyphens, no leading/trailing hyphen)."
        super().__init__(message)

class TenantNotFoundException(NotFoundException):
    def __init__(self, tenant_id: str):
        super().__init__("Tenant", tenant_id)

class RoleNotFoundException(NotFoundException):
    def __init__(self, role_id: str):
        super().__init__("Role", role_id)

class RoleAlreadyExistsException(ConflictException):
    def __init__(self, name: str):
        super().__init__("Role", name)