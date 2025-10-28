from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from api.domain.entities.stripe_settings import ActorType, PaymentType, ScopeType, StatusType


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
    trial_period_days: Optional[int] = None
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


class InvoiceDto(BaseModel):
  id: str
  amount_country: str
  account_name: str
  amount_due: int = 0
  amount_paid: int = 0
  amount_remaining: int = 0
  amount_overpaid: int = 0
  attempt_count: int = 0
  attempted: bool = False
  auto_advance: bool = False
  billing_reason: str
  collection_method: str
  created: int
  currency: str
  customer: str
  customer_name: str
  status: str
  total: int
  receipt_number: Optional[str] = None

class InvoiceListDto(BaseModel):
    invoices: List[InvoiceDto]
    has_more: bool = False



# Billing Record stored in our system
class BillingRecordDto(BaseModel):
    scope: ScopeType
    actor: ActorType
    user_id: Optional[str] = None
    payment_type: PaymentType
    currency: str
    amount: Optional[int] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    product_id: Optional[str] = None
    price_id: Optional[str] = None
    status: StatusType
    current_period_end: Optional[int] = None
    canceled_at: Optional[int] = None
    cancellation_reason: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class BillingRecordListDto(BaseModel):
    billing_records: List[BillingRecordDto]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool


