from typing import Optional
from pydantic import BaseModel

from api.domain.entities.stripe_settings import PaymentType


class CreateStripeSettingDto(BaseModel):
    default_currency: str = "eur"
    stripe_webhook_secret: str
    mode: PaymentType = "recurring"
    trial_period_days: int = 14  # Default trial period for subscriptions in days
    stripe_secret_key: Optional[str] = None # Secret key for Stripe API only tenant scope

