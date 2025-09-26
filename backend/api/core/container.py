import punq
from api.infrastructure.persistence.repositories.role_repository_impl import RoleRepository
from api.infrastructure.persistence.repositories.storage_settings_repository_impl import StorageSettingsRepository
from api.infrastructure.persistence.repositories.tenant_repository_impl import TenantRepository
from api.infrastructure.persistence.repositories.user_password_reset_repository_impl import UserPasswordResetRepository
from api.infrastructure.persistence.repositories.user_preference_repository_impl import UserPreferenceRepository
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.usecases.auth_service import AuthService
from api.usecases.role_service import RoleService
from api.usecases.storage_settings_service import StorageSettingsService
from api.usecases.user_preference_service import UserPreferenceService
from api.usecases.user_service import UserService
from api.usecases.tenant_service import TenantService
from api.infrastructure.persistence.mongodb import Database, mongo_client


container = punq.Container()

# Register database
container.register(Database, instance=mongo_client)

# Register security components

## JWT Token Service
container.register(JwtTokenService, scope=punq.Scope.singleton)

# Register repositories and services

## Tenant
container.register(TenantRepository)
container.register(TenantService, scope=punq.Scope.singleton)

## User
container.register(UserRepository)
container.register(UserPasswordResetRepository)
container.register(UserService, scope=punq.Scope.singleton)

## User Preference
container.register(UserPreferenceRepository)
container.register(UserPreferenceService, scope=punq.Scope.singleton)

## Role
container.register(RoleRepository)
container.register(RoleService, scope=punq.Scope.singleton)

## Auth service
container.register(AuthService, scope=punq.Scope.singleton)

## Storage Settings
container.register(StorageSettingsRepository)
container.register(StorageSettingsService, scope=punq.Scope.singleton)


def get_database() -> Database:
    return container.resolve(Database)

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

def get_storage_settings_service() -> StorageSettingsService:
    return container.resolve(StorageSettingsService)