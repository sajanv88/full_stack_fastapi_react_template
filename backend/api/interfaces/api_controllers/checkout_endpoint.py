from fastapi import APIRouter, Depends

from api.common.exceptions import InvalidOperationException
from api.core.container import get_billing_record_service
from api.infrastructure.security.current_user import CurrentUserOptional
from api.usecases.billing_record_service import BillingRecordService


router = APIRouter(prefix="/checkouts")
router.tags = ["Stripe - Checkout"]

@router.post("/host")
async def create_checkout_session(
    current_optional_user: CurrentUserOptional,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    if current_optional_user and current_optional_user.tenant_id:
        raise InvalidOperationException("This request was made in tenant context. Host context is required.")
    
    pass  # Implementation of checkout session creation goes here
