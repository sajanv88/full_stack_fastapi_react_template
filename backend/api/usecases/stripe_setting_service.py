from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.payment_repository_impl import PaymentRepository
from api.usecases.tenant_service import TenantService


class StripeSettingService:
    def __init__(self, payment_repository: PaymentRepository, stripe_resolver: StripeResolver, tenant_service: TenantService):
        self.payment_repository: PaymentRepository = payment_repository
        self.stripe_resolver: StripeResolver = stripe_resolver
        self.tenant_service: TenantService = tenant_service

    async def configure_stripe_settings(self, settings: CreateStripeSettingDto, tenant_id: str) -> None:
        """
        Configure Stripe settings for the application.
        Args:
            settings (CreateStripeSettingDto): The Stripe settings to configure.
        Raises:
            StripeSettingsException: If there is an error configuring the settings.
            TenantNotFoundException: If the tenant does not exist.
        """
        await self.tenant_service.get_tenant_by_id(tenant_id)
        await self.payment_repository.store_stripe_settings(stripe_config=settings)
        
        