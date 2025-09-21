import punq
from api.infrastructure.persistence.repositories.role_repository_impl import RoleRepository
from api.infrastructure.persistence.repositories.tenant_repository_impl import TenantRepository
from api.infrastructure.persistence.repositories.user_password_reset_repository_impl import UserPasswordResetRepository
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository
from api.usecases.role_service import RoleService
from api.usecases.user_service import UserService
from api.usecases.tenant_service import TenantService
from api.infrastructure.persistence.mongodb import Database, mongo_client


container = punq.Container()

# Register database
container.register(Database, instance=mongo_client)

# Register repositories and services

## Tenant
container.register(TenantRepository)
container.register(TenantService)


## User
container.register(UserRepository)
container.register(UserPasswordResetRepository)
container.register(UserService)

## Role
container.register(RoleRepository)
container.register(RoleService)



def get_tenant_service() -> TenantService:
    return container.resolve(TenantService)


def get_user_service() -> UserService:
    return container.resolve(UserService)


def get_role_service() -> RoleService:
    return container.resolve(RoleService)

