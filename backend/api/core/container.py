import punq
from api.common.audit_logs_repository import AuditLogRepository
from api.domain.interfaces.email_service import IEmailService
from api.infrastructure.externals.coolify_app import CoolifyApp
from api.infrastructure.externals.dns_resolver import DnsResolver
from api.infrastructure.externals.smtp_email import SmtpEmail

from api.infrastructure.externals.sso_auth_provider import SSOAuthProvider
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.chat_history_ai_repository_impl import ChatHistoryAIRepository
from api.infrastructure.persistence.repositories.chat_session_ai_repository_impl import ChatSessionAIRepository
from api.infrastructure.persistence.repositories.payment_repository_impl import PaymentRepository, StripeSettingsRepository
from api.infrastructure.persistence.repositories.role_repository_impl import RoleRepository
from api.infrastructure.persistence.repositories.sso_settings_provider_respository_impl import SSOSettingsProviderRepository
from api.infrastructure.persistence.repositories.storage_settings_repository_impl import StorageSettingsRepository
from api.infrastructure.persistence.repositories.subscription_plan_repository_impl import SubscriptionPlanRepository
from api.infrastructure.persistence.repositories.tenant_repository_impl import TenantRepository
from api.infrastructure.persistence.repositories.user_magic_link_repository_impl import UserMagicLinkRepository
from api.infrastructure.persistence.repositories.user_passkey_repository_impl import UserPasskeyChallengesRepository, UserPasskeyRepository
from api.infrastructure.persistence.repositories.user_password_reset_repository_impl import UserPasswordResetRepository
from api.infrastructure.persistence.repositories.user_preference_repository_impl import UserPreferenceRepository
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository
from api.infrastructure.persistence.repositories.billing_record_repository_impl import BillingRecordRepository
from api.infrastructure.persistence.repositories.notification_banner_repository_impl import NotificationBannerRepository

from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.infrastructure.security.passkey_service import PasskeyService
from api.usecases.audit_logs_service import AuditLogsService
from api.usecases.billing_record_service import BillingRecordService
from api.usecases.coolify_app_service import CoolifyAppService
from api.usecases.local_ai_service import LocalAIService
from api.usecases.auth_service import AuthService
from api.usecases.file_service import FileService
from api.usecases.magic_link_service import EmailMagicLinkService
from api.usecases.pricing_service import PricingService
from api.usecases.product_service import ProductService
from api.usecases.role_service import RoleService
from api.usecases.sso_settings_service import SSOSettingsService
from api.usecases.storage_settings_service import StorageSettingsService
from api.usecases.stripe_setting_service import StripeSettingService
from api.usecases.subscription_plan_service import SubscriptionPlanService
from api.usecases.user_preference_service import UserPreferenceService
from api.usecases.user_service import UserService
from api.usecases.tenant_service import TenantService
from api.usecases.notification_banner_service import NotificationBannerService

from api.infrastructure.persistence.mongodb import Database, mongo_client

container = punq.Container()

# Register database
container.register(Database, instance=mongo_client)



# Register security components

## Smtp email Service
container.register(IEmailService, SmtpEmail, scope=punq.Scope.singleton)

## JWT Token Service
container.register(JwtTokenService, scope=punq.Scope.singleton)


## Passkey Components
container.register(UserPasskeyRepository, scope=punq.Scope.singleton)
container.register(UserPasskeyChallengesRepository, scope=punq.Scope.singleton)
container.register(PasskeyService, scope=punq.Scope.singleton)

## Email magic link user login
container.register(UserMagicLinkRepository, scope=punq.Scope.singleton)
container.register(EmailMagicLinkService, scope=punq.Scope.singleton)


# Register infra components

## DNS Resolver
container.register(DnsResolver, scope=punq.Scope.singleton)

## Coolify Integration
container.register(CoolifyApp, scope=punq.Scope.singleton)
container.register(CoolifyAppService, scope=punq.Scope.singleton)


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

## File Service
container.register(FileService, scope=punq.Scope.singleton)


## AI Components
container.register(ChatSessionAIRepository)
container.register(ChatHistoryAIRepository)
container.register(LocalAIService, scope=punq.Scope.singleton)

## Subscription Plan Components
container.register(SubscriptionPlanRepository, scope=punq.Scope.singleton)
container.register(SubscriptionPlanService, scope=punq.Scope.singleton)

## Stripe and Payment Components
container.register(StripeSettingsRepository, scope=punq.Scope.singleton)
container.register(BillingRecordRepository, scope=punq.Scope.singleton)
container.register(PaymentRepository, scope=punq.Scope.singleton)
container.register(StripeResolver, scope=punq.Scope.singleton)

container.register(BillingRecordService, scope=punq.Scope.singleton)
container.register(ProductService, scope=punq.Scope.singleton)
container.register(PricingService, scope=punq.Scope.singleton)
container.register(StripeSettingService, scope=punq.Scope.singleton)


## Notification Banner Components
container.register(NotificationBannerRepository, scope=punq.Scope.singleton)
container.register(NotificationBannerService, scope=punq.Scope.singleton)

## Audit Log Components
container.register(AuditLogRepository, scope=punq.Scope.singleton)
container.register(AuditLogsService, scope=punq.Scope.singleton)


## SSO Settings Components
container.register(SSOSettingsProviderRepository, scope=punq.Scope.singleton)
container.register(SSOSettingsService, scope=punq.Scope.singleton)
container.register(SSOAuthProvider, scope=punq.Scope.singleton)


## Dependency resolver functions

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

def get_storage_settings_repository() -> StorageSettingsRepository:
    return container.resolve(StorageSettingsRepository)

def get_file_service() -> FileService:
    return container.resolve(FileService)

def get_email_service() -> IEmailService:
    return container.resolve(IEmailService)

def get_local_ai_service() -> LocalAIService:
    return container.resolve(LocalAIService)

def get_dns_resolver() -> DnsResolver:
    return container.resolve(DnsResolver)

def get_coolify_app_service() -> CoolifyAppService:
    return container.resolve(CoolifyAppService)

def get_user_passkey_repository() -> UserPasskeyRepository:
    return container.resolve(UserPasskeyRepository)

def get_user_passkey_challenges_repository() -> UserPasskeyChallengesRepository:
    return container.resolve(UserPasskeyChallengesRepository)

def get_passkey_service() -> PasskeyService:
    return container.resolve(PasskeyService)

def get_user_magic_link_repository() -> UserMagicLinkRepository:
    return container.resolve(UserMagicLinkRepository)

def get_email_magic_link_service() -> EmailMagicLinkService:
    return container.resolve(EmailMagicLinkService)

def get_billing_record_service() -> BillingRecordService:
    return container.resolve(BillingRecordService)

def get_product_service() -> ProductService:
    return container.resolve(ProductService)

def get_pricing_service() -> PricingService:
    return container.resolve(PricingService)

def get_stripe_resolver() -> StripeResolver:
    return container.resolve(StripeResolver)

def get_stripe_setting_service() -> StripeSettingService:
    return container.resolve(StripeSettingService)

def get_subscription_plan_service() -> SubscriptionPlanService:
    return container.resolve(SubscriptionPlanService)

def get_notification_banner_service() -> NotificationBannerService:
    return container.resolve(NotificationBannerService)

def get_audit_logs_service() -> AuditLogsService:
    return container.resolve(AuditLogsService)


def get_sso_settings_service() -> SSOSettingsService:
    return container.resolve(SSOSettingsService)

def get_sso_auth_provider() -> SSOAuthProvider:
    return container.resolve(SSOAuthProvider)

print("Dependency injection container configured.")
