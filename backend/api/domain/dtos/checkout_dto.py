from typing import Literal
from pydantic import BaseModel, EmailStr



class CheckoutRequestDto(BaseModel):
    price_id: str
    tenant_id: str | None = None
    mode: Literal["payment", "subscription", "setup"] = "subscription"
    email: EmailStr


class CheckoutResponseDto(BaseModel):
    checkout_url: str
