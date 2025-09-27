# Keep only domain-specific exceptions here

from api.common.exceptions import AwsException, AzureException, InvalidOperationException, NotFoundException, ConflictException

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

class TenantNotActiveException(InvalidOperationException):
    def __init__(self, tenant_id: str):
        message = f"Tenant with ID '{tenant_id}' is not active."
        super().__init__(message)


class S3StorageException(AwsException):
    def __init__(self, message: str):
        local_message = f"S3 Storage Error: {message}"
        super().__init__(local_message)

class AzureBlobStorageException(AzureException):
    def __init__(self, message: str):
        local_message = f"Azure Blob Storage Error: {message}"
        super().__init__(local_message)


class StorageNotEnabledException(InvalidOperationException):
    def __init__(self):
        message = "No storage provider is enabled. Please enable a storage provider in the settings."
        super().__init__(message)