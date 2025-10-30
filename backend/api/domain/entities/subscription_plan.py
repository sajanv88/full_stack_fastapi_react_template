# This entity is used to represent subscription plans in the system Not used by Stripe directly

from datetime import datetime
from typing import Dict, Literal

from beanie import PydanticObjectId
from api.domain.entities.api_base_model import ApiBaseModel
from pydantic import field_serializer


class SubscriptionPlan(ApiBaseModel):
    plan_level: Dict[str, int] = {"basic": 0, "pro": 1, "enterprise": 2}  # e.g., 0: Basic, 1: Pro, 2: Enterprise
    is_trial: bool = False
    actor: Literal["tenant", "end_user"] = "tenant" # who it is applied to, If end_userm, then user_id must be set
    user_id: PydanticObjectId | None = None  # The end user who has this subscription, if applicable
    plan_id: str  # Corresponding Stripe Price ID    

    @field_serializer("id", "tenant_id", "created_at", "updated_at", "user_id")
    def serialize_as_str(self, value: datetime | PydanticObjectId | None) -> str | None:
       if value is None:
           return None
       return str(value)
    
    class Settings:
        name = "subscription_plans"
        indexes = [
            ("tenant_id", "plan_id"),
            ("user_id", "plan_id"),
            "is_trial",
        ]