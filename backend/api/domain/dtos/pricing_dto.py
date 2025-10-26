from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

class RecurringDto(BaseModel):
   interval: Literal["day", "week", "month", "year"] = Field(default="month", description="Billing interval, e.g., 'month'")
   interval_count: int = Field(default=1, description="Number of intervals between each billing cycle")
   usage_type: Literal["licensed", "metered"] = Field(default="licensed", description="Configures how the quantity per period should be determined. Can be either metered or licensed. licensed automatically bills the quantity set when adding it to a subscription. metered aggregates the total usage based on usage records. Defaults to licensed.")
   
class CreatePricingDto(BaseModel):
   currency: str = Field(default="eur", description="Currency code, e.g., 'usd'")
   unit_amount: int = Field(..., description="A positive integer in cents (or 0 for a free price) representing how much to charge. One of unit_amount, unit_amount_decimal, or custom_unit_amount is required, unless billing_scheme=tiered.")
   product: str = Field(..., description="The ID of the product this price is associated with")
   active: bool = Field(default=True, description="Whether the price is active or not")
   recurring: RecurringDto


class PricingDto(BaseModel):
   id: str
   currency: str
   unit_amount: int
   product: str
   active: bool
   recurring: RecurringDto
   tax_behavior: str
   type: str
   unit_amount_decimal: str

class PricingListDto(BaseModel):
   pricings: list[PricingDto]
   has_more: bool

class UpdatePricingDto(BaseModel):
   active: bool
   metadata: Optional[Dict[str, Any]] = None
   tax_behavior: Optional[Literal["exclusive", "inclusive", "unspecified"]] = None
   