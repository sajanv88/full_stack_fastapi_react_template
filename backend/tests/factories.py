from typing import Iterable

from beanie import PydanticObjectId

from api.common.enums.gender import Gender
from api.common.security import hash_it
from api.domain.dtos.auth_dto import MeResponseDto
from api.domain.dtos.role_dto import RoleDto
from api.domain.entities.role import Role
from api.domain.entities.tenant import Tenant
from api.domain.entities.user import User
from api.domain.enum.permission import Permission

TIMESTAMP = "2024-10-01T00:00:00Z"
PASSWORD = "Test@123!"


def make_user(
    permissions: Iterable[Permission] = (),
    tenant_id: str | None = None,
    user_id: str | None = None,
    email: str = "user@example.com",
) -> MeResponseDto:
    """The in-memory user a request acts as, for tests that override `get_current_user`."""
    role_id = str(PydanticObjectId())
    return MeResponseDto(
        id=user_id or str(PydanticObjectId()),
        first_name="Test",
        last_name="User",
        email=email,
        gender=Gender.OTHER,
        is_active=True,
        role_id=role_id,
        tenant_id=tenant_id,
        created_at=TIMESTAMP,
        updated_at=TIMESTAMP,
        role=RoleDto(
            id=role_id,
            name="test-role",
            description=None,
            permissions=list(permissions),
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
            tenant_id=tenant_id,
        ),
        subscription=None,
    )


async def seed_user(
    email: str = "user@example.com",
    password: str = PASSWORD,
    permissions: Iterable[Permission] = (),
    **fields,
) -> User:
    """A persisted user and role, for tests that go through the real authentication."""
    role = await Role(name=f"role-{PydanticObjectId()}", description=None, permissions=list(permissions)).insert()
    return await User(
        first_name="Test",
        last_name="User",
        email=email,
        gender=Gender.OTHER,
        is_active=fields.pop("is_active", True),
        role_id=role.id,
        password=hash_it(password),
        **fields,
    ).insert()


async def seed_tenant(name: str = "alpha") -> Tenant:
    return await Tenant(name=name, subdomain=f"{name}.fsrapp.com", is_active=True).insert()
