
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.core.exceptions import StripeSettingsNotFoundException
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto
from api.domain.entities.stripe_settings import  StripeSettings

logger = get_logger(__name__)


class StripeSettingsRepository(BaseRepository[StripeSettings], AuditLogRepository):
    def __init__(self):
        super().__init__(StripeSettings)

    async def store_stripe_settings(self, stripe_config: CreateStripeSettingDto) -> None:
        """
        Store or update Stripe settings in the database.
        Args:
            stripe_config (CreateStripeSettingDto): The Stripe configuration data to store.
        Raises:
            StripeSettingsNotFoundException: If there is an error storing the settings.
        """
        settings = await self.single_or_none()
        if settings:
            settings.stripe_secret_key = stripe_config.stripe_secret_key
            settings.default_currency = stripe_config.default_currency
            settings.stripe_webhook_secret = stripe_config.stripe_webhook_secret
            settings.mode = stripe_config.mode
            settings.trial_period_days = stripe_config.trial_period_days
            await settings.save()
            logger.info(f"Updated Stripe settings for tenant {settings.tenant_id}")
            await self.add_audit_log(AuditLogDto(
                action="update",
                changes={"info": f"Updated Stripe settings for tenant {settings.tenant_id}"},
                entity="StripeSettings",
                tenant_id=str(settings.tenant_id) if settings.tenant_id else None,
                user_id=None  # Todo: Need to add a new property in role.. to determine who updated it.
            ))
        else:
            logger.info(f"Creating new Stripe settings for tenant")
            settings = StripeSettings(**stripe_config.model_dump())
            settings.tenant_id = stripe_config.tenant_id
            await self.create(settings.model_dump())
            await self.add_audit_log(AuditLogDto(
                action="create",
                changes={"info": f"Created Stripe settings for tenant {settings.tenant_id}"},
                entity="StripeSettings",
                tenant_id=str(settings.tenant_id) if settings.tenant_id else None,
                user_id=None  # Todo: Need to add a new property in role.. to determine who added it.
            ))

    async def get_stored_stripe_settings(self) -> StripeSettings:
        """
        Retrieve stored Stripe settings from the database.
        Returns:
            StripeSettings: The stored Stripe settings.
        Raises:
            StripeSettingsNotFoundException: If no settings are found.
        """
        try:
            result = await self.single_or_none()
            if result is None:
                raise StripeSettingsNotFoundException("Stripe settings not found.")
            return result
        except Exception as e:
            logger.error(f"Error fetching stored Stripe settings: {e}")
            await self.add_audit_log(AuditLogDto(
                action="error",
                changes={"info": f"Attempted to read Stripe settings, but an error occurred: {e}"},
                entity="StripeSettings",
                tenant_id=None,
                user_id=None # Todo: Need to add a new property in role.. to determine who added it.
            ))
            raise StripeSettingsNotFoundException("Stripe settings not found.")
    



class PaymentRepository(StripeSettingsRepository):
    pass
