# Keep generic exceptions here

class ApiBaseException(Exception):
    """Base exception for the app."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class NotFoundException(ApiBaseException):
    """Entity not found."""
    def __init__(self, entity: str, identifier: str):
        message = f"{entity} with identifier {identifier} not found."
        super().__init__(message)

class ConflictException(ApiBaseException):
    """Entity already exists / conflict."""
    def __init__(self, entity: str, identifier: str):
        message = f"{entity} with identifier {identifier} already exists."
        super().__init__(message)

class UnauthorizedException(ApiBaseException):
    """Unauthorized or forbidden action."""
    def __init__(self, message: str):
        super().__init__(message)

class InvalidOperationException(ApiBaseException):
    """Invalid input or operation."""
    def __init__(self, message: str):
        super().__init__(message)


class ForbiddenException(ApiBaseException):
    """Forbidden action."""
    def __init__(self, message: str):
        super().__init__(message)


class AuthenticationFailedException(ApiBaseException):
    """Authentication failed."""
    def __init__(self, message: str = "Authentication failed."):
        super().__init__(message)