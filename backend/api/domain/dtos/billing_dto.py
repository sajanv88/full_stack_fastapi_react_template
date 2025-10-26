from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PlanDto(BaseModel):
    id: str
    active: bool
    amount: int
    amount_decimal: str
    billing_scheme: str
    currency: str = "eur"
    interval: str
    interval_count: int
    product: str
    trial_period_days: int
    usage_type: str


class PlanListDto(BaseModel):
    plans: List[PlanDto]
    has_more: bool


class CreatePlanDto(BaseModel):
    currency: str = Field(default="eur", description="Must be a supported currency: https://docs.stripe.com/currencies")
    interval: Literal["month", "year"] # Add day or week later... if needed.
    product_id: str = Field(..., description="The product whose pricing the created plan will represent. This must be the ID of an existing product.")
    amount: int    


class UpdatePlanDto(BaseModel):
    trial_period_days: int
    active: bool = True
    metadata: Optional[Dict[str, Any]] = None
