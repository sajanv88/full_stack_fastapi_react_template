from typing import Optional
from pydantic import BaseModel

from api.domain.entities.stripe_settings import PaymentType


class CreateStripeSettingDto(BaseModel):
    default_currency: str = "eur"
    stripe_webhook_secret: str
    mode: PaymentType = "recurring"
    trial_period_days: int = 14  # Default trial period for subscriptions in days
    stripe_secret_key: str  #Secret key for Stripe API only tenant scope

class UpdateStripeSettingDto(BaseModel):
    default_currency: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    mode: Optional[PaymentType] = None
    trial_period_days: Optional[int] = None
    stripe_secret_key: Optional[str] = None  #Secret key for Stripe API only tenant scope


class StripeSettingDto(BaseModel):
    id: str
    tenant_id: str
    default_currency: str
    mode: PaymentType
    trial_period_days: int
