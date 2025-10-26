from typing import Optional
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.core.exceptions import StripeSettingsNotFoundException
from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto
from api.domain.entities.stripe_settings import BillingRecord, StripeSettings

logger = get_logger(__name__)


class StripeSettingsRepository(BaseRepository[StripeSettings]):
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
        else:
            logger.info(f"Creating new Stripe settings for tenant")
            settings = StripeSettings(**stripe_config.model_dump())
            await self.create(settings.model_dump())

    async def get_stored_stripe_settings(self) -> StripeSettings:
        """
        Retrieve stored Stripe settings from the database.
        Returns:
            StripeSettings: The stored Stripe settings.
        Raises:
            StripeSettingsNotFoundException: If no settings are found.
        """
        try:
            return await self.single_or_none()
        except Exception as e:
            logger.error(f"Error fetching stored Stripe settings: {e}")
            raise StripeSettingsNotFoundException("Stripe settings not found.")
    

class BillingRecordRepository(BaseRepository[BillingRecord]):
    def __init__(self):
        super().__init__(BillingRecord)
    

class PaymentRepository(StripeSettingsRepository):
    pass
