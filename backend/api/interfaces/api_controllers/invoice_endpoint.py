from fastapi import APIRouter, Depends

from api.core.container import get_billing_record_service
from api.domain.dtos.billing_dto import InvoiceListDto
from api.domain.enum.feature import Feature
from api.domain.enum.permission import Permission
from api.domain.security.feature_access_management import check_feature_access
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.billing_record_service import BillingRecordService


router = APIRouter(
    prefix="/invoices", 
    dependencies=[
        Depends(check_feature_access(feature_name=Feature.STRIPE)),
        Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_BILLING]))
    ]
)
router.tags = ["Stripe - Invoices"]

@router.get("/", summary="List invoices", response_model=InvoiceListDto)
async def list_invoices(
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user.tenant_id:
        scope = "tenant"

    return await billing_service.list_invoices(scope=scope)
    
    