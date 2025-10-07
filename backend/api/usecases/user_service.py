from typing import Any
from beanie import PydanticObjectId
from pydantic import EmailStr
from api.common.exceptions import InvalidOperationException
from api.common.utils import get_logger
from api.core.exceptions import EmailAlreadyExistsException, UserNotFoundException
from api.domain.dtos.dashboard_dto import TimeSeriesDto
from api.domain.entities.user import User
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto, UserDto, UserListDto, UserResendActivationEmailRequestDto
from api.domain.entities.user_password_reset import UserPasswordReset
from api.infrastructure.persistence.repositories.user_password_reset_repository_impl import UserPasswordResetRepository
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository
from api.common.security import hash_it

logger = get_logger(__name__)

class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            user_password_reset_repository: UserPasswordResetRepository
        ):

        self.user_repository = user_repository
        self.user_password_reset_repository = user_password_reset_repository
        logger.info("Initialized.")


    async def list_users(self, skip: int = 0, limit: int = 10) -> UserListDto:
        return await self.user_repository.list(skip=skip, limit=limit)

    async def find_by_email(self, email: EmailStr) -> User:
        """Find user by email. Returns User model. Raises UserNotFoundException if not found."""
        existing = await self.user_repository.single_or_none(email=email)
        if existing is None:
            raise UserNotFoundException(email)
        return existing
    
    async def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID. Returns User model. Raises UserNotFoundException if not found."""
        existing = await self.user_repository.get(id=user_id)
        if existing is None:
            raise UserNotFoundException(user_id)
        return existing

    async def create_user(self, user_data: CreateUserDto) -> PydanticObjectId:
        """Create a new user and returns its ID. Raises EmailAlreadyExistsException if email already exists."""
        existing = await self.user_repository.single_or_none(email=user_data.email)
        if existing is not None:
            raise EmailAlreadyExistsException(user_data.email)
        user_data.password = hash_it(user_data.password)
        user_id = await self.user_repository.create(user_data)
        
        # avoid circular import
        from api.core.container import get_auth_service

        auth_service = get_auth_service()
        welcome_email = UserResendActivationEmailRequestDto(
            email=user_data.email,
            first_name=user_data.first_name,
            tenant_id=user_data.tenant_id,
            id=str(user_id)
        )
        await auth_service.send_activation_email(welcome_email)
        return user_id

    async def update_user(self, user_id: str, user_data: UpdateUserDto) -> User | None:
        """Update user by ID. Returns updated User model. Raises UserNotFoundException if user does not exist."""
        existing = await self.user_repository.get(id=user_id)
        if existing is None:
            raise UserNotFoundException(user_id)
        return await self.user_repository.update(user_id=user_id, data=user_data)
     

    async def delete_user(self, user_id: str) -> None:
        """Delete user by ID. Returns None otherwise, Raises UserNotFoundException if user does not exist."""
        if await self.user_repository.delete(id=user_id) is False:
            raise UserNotFoundException(user_id)
        

    async def update_user_password(self, user_id: str, new_password: str) -> User | None:
        """Update user password by ID. Returns updated User model. Raises UserNotFoundException if user does not exist."""
        existing = await self.user_repository.get(id=user_id)
        if existing is None:
            raise UserNotFoundException(user_id)
        hashed_password = hash_it(new_password)
        existing.password = hashed_password
        await existing.save()
        return existing

    async def total_count(self, params: Any | None = None) -> int:
        """Get total user count."""
        return await self.user_repository.count(params=params)
    
    async def request_password_reset(self, email: EmailStr) -> UserPasswordReset:
        """Set password reset for user by ID. Returns None otherwise, Raises InvalidOperationException on failure."""
        try:
            user = await self.find_by_email(email=email)
            return await self.user_password_reset_repository.set_password_reset(user_id=str(user.id), first_name=user.first_name, tenant_id=user.tenant_id)
        except Exception as e:
            logger.error(f"Error setting password reset for user with an email: {email} wasn't successful: {e}")
            raise InvalidOperationException(message="Failed to set password reset.")

    async def retrieve_password_reset_data_by_user_id(self, user_id: str) -> UserPasswordReset | None:
        """Get password reset entry by token. Returns UserPasswordReset model or None if not found."""
        return await self.user_password_reset_repository.single_or_none(user_id=PydanticObjectId(user_id))

    async def clear_password_reset_data_by_user_id(self, user_id: str) -> bool:
        """Clear password reset entry by user ID. Returns boolean."""
        logger.info(f"Clearing password reset data for user_id: {user_id}")
        return await self.user_password_reset_repository.delete(id=user_id)
    
    async def check_email_exists(self, email: EmailStr) -> bool:
        """Check if email exists. Returns boolean."""
        existing = await self.user_repository.single_or_none(email=email)
        return existing is not None
    
    async def aggregate(self, pipeline: list[dict]) -> list[TimeSeriesDto]:
        """Aggregate users based on the provided pipeline. Returns an async list[TimeSeriesDto]."""
        return await self.user_repository.aggregate(pipeline, projection_model=TimeSeriesDto)