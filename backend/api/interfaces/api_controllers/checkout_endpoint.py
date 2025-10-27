from fastapi import APIRouter, Depends

from api.core.container import get_billing_record_service
from api.infrastructure.security.current_user import CurrentUserOptional
from api.usecases.billing_record_service import BillingRecordService


router = APIRouter(prefix="/checkout")
router.tags = ["Stripe - Checkout"]

@router.post("/")
async def create_checkout_session(
    current_optional_user: CurrentUserOptional,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    pass  # Implementation of checkout session creation goes here
