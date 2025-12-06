from datetime import datetime
from typing import Dict, Literal, Optional
from beanie import PydanticObjectId
from pydantic import Field, field_serializer
from api.domain.entities.api_base_model import ApiBaseModel

PaymentType = Literal["one_time", "recurring", "both"]
ScopeType = Literal["host", "tenant"]
StatusType = Literal[
    "paid", "pending", "requires_payment_method", "requires_action",
    "active", "succeeded", "payment_failed", "canceled", "incomplete"
]
ActorType = Literal["tenant", "end_user"] # who is being billed

class StripeSettings(ApiBaseModel):
    default_currency: str = "eur"
    stripe_webhook_secret: str
    mode: PaymentType = "recurring"
    trial_period_days: int = 14  # Default trial period for subscriptions in days
    stripe_secret_key: Optional[str] = None # Secret key for Stripe API only tenant scope

    @field_serializer("id", "tenant_id", "created_at", "updated_at")
    def serialize_as_str(self, value: PydanticObjectId | datetime | None) -> str:
       if value is None:
           return None
       return str(value)


    class Settings:
        name = "stripe_settings"




class BillingRecord(ApiBaseModel):
    scope: ScopeType
    actor: ActorType
    user_id: PydanticObjectId | None = None  # The end user who made the payment, if applicable
    payment_type: str
    currency: str
    amount: Optional[int] = None  # unit amount used for one-time payments
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    product_id: Optional[str] = None
    price_id: Optional[str] = None
    status: StatusType = "pending"
    current_period_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

    @field_serializer("id", "tenant_id", "created_at", "updated_at", "current_period_end", "canceled_at", "user_id")
    def serialize_as_str(self, value: PydanticObjectId | datetime | None) -> str:
       if value is None:
           return None
       return str(value)

    class Settings:
        name = "billing_records"
        indexes = [
            ("tenant_id", "stripe_subscription_id"),
            "stripe_session_id",
            "user_id",
            ("scope", "status"),
            ("tenant_id", "created_at"),
        ]