import punq
from api.infrastructure.persistence.repositories.role_repository_impl import RoleRepository
from api.infrastructure.persistence.repositories.tenant_repository_impl import TenantRepository
from api.infrastructure.persistence.repositories.user_password_reset_repository_impl import UserPasswordResetRepository
from api.infrastructure.persistence.repositories.user_preference_repository_impl import UserPreferenceRepository
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.usecases.auth_service import AuthService
from api.usecases.role_service import RoleService
from api.usecases.user_preference_service import UserPreferenceService
from api.usecases.user_service import UserService
from api.usecases.tenant_service import TenantService
from api.infrastructure.persistence.mongodb import Database, mongo_client


container = punq.Container()

# Register database
container.register(Database, instance=mongo_client)


# Register security components

## JWT Token Service
container.register(JwtTokenService)


# Register repositories and services

## Tenant
container.register(TenantRepository)
container.register(TenantService)


## User
container.register(UserRepository)
container.register(UserPasswordResetRepository)
container.register(UserService)

## User Preference
container.register(UserPreferenceRepository)
container.register(UserPreferenceService)

## Role
container.register(RoleRepository)
container.register(RoleService)

## Auth service
container.register(AuthService)



def get_tenant_service() -> TenantService:
    return container.resolve(TenantService)

def get_user_service() -> UserService:
    return container.resolve(UserService)

def get_user_preference_service() -> UserPreferenceService:
    return container.resolve(UserPreferenceService)

def get_role_service() -> RoleService:
    return container.resolve(RoleService)

def get_jwt_token_service() -> JwtTokenService:
    return container.resolve(JwtTokenService)

def get_auth_service() -> AuthService:
    return container.resolve(AuthService)