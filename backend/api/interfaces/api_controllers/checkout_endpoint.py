from fastapi import APIRouter, Depends, status

from api.common.exceptions import InvalidOperationException
from api.core.container import get_billing_record_service
from api.domain.dtos.billing_dto import BillingRecordListDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUserOptional
from api.interfaces.security.role_checker import check_permissions_for_current_role
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

@router.get("/all", response_model=BillingRecordListDto, status_code=status.HTTP_200_OK)
async def list_checkout_records(
    skip: int = 0, limit: int = 100,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_BILLING])),
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    return await billing_service.list_checkout_records(skip=skip, limit=limit)
