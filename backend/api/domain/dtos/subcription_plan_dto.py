# This dto is used to represent subscription plans in the system Not used by Stripe directly

from typing import Dict
from pydantic import BaseModel, Field


class SubscriptionPlanDto(BaseModel):
    id: str
    plan_level: Dict[str, int] = Field(..., description="e.g., {'basic': 0, 'pro': 1, 'enterprise': 2}")
    is_trial: bool = Field(..., description="Indicates if the subscription is a trial")
    tenant_id: str | None = Field(..., description="The tenant who owns the subscription")
    actor: str = Field(..., description="who it is applied to, If end_user, then user_id must be set")
    user_id: str | None = Field(..., description="The end user who has this subscription, if applicable")
    plan_id: str = Field(..., description="Corresponding Stripe Price ID")


class CreateSubscriptionPlanDto(BaseModel):
    plan_level: Dict[str, int] = Field(..., description="e.g., {'basic': 0, 'pro': 1, 'enterprise': 2}")
    is_trial: bool = Field(..., description="Indicates if the subscription is a trial")
    tenant_id: str | None = Field(..., description="The tenant who owns the subscription")
    actor: str = Field(..., description="who it is applied to, If end_user, then user_id must be set")
    user_id: str | None = Field(..., description="The end user who has this subscription, if applicable")
    plan_id: str = Field(..., description="Corresponding Stripe Price ID")