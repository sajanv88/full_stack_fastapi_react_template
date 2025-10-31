from fastapi import APIRouter, Depends, status
from api.common.exceptions import InvalidOperationException
from api.core.container import get_billing_record_service, get_tenant_service
from api.domain.dtos.billing_dto import BillingRecordListDto
from api.domain.dtos.checkout_dto import CheckoutRequestDto, CheckoutResponseDto
from api.domain.enum.feature import Feature
from api.domain.enum.permission import Permission
from api.domain.security.feature_access_management import check_feature_access
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.billing_record_service import BillingRecordService
from api.usecases.tenant_service import TenantService

from api.common.utils import get_host_main_domain_name, get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/checkouts", dependencies=[
    Depends(check_feature_access(feature_name=Feature.STRIPE)),
])
router.tags = ["Stripe - Checkout"]

@router.post("/host/{tenant_id:path}/tenant", response_model=CheckoutResponseDto)
async def create_host_checkout_session(
    checkout_req: CheckoutRequestDto,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    if current_user and current_user.tenant_id is not None:
        if checkout_req.tenant_id != current_user.tenant_id:
            logger.error(f"Tenant ID mismatch for the current user. And current user's tenant id is: {current_user.tenant_id} and requested tenant id is: {checkout_req.tenant_id}")
            raise InvalidOperationException(f"Tenant ID mismatch for the current user. {checkout_req.tenant_id}")
        
        host_main_domain = f"https://{get_host_main_domain_name()}"
        url = await billing_service.create_host_check_out_session_for_tenant(frontend_url=host_main_domain, checkout_req=checkout_req)
        return CheckoutResponseDto(checkout_url=url)


@router.post("/tenant/subscription", response_model=CheckoutResponseDto)
async def create_tenant_checkout_session(
    checkout_req: CheckoutRequestDto,
    current_user: CurrentUser,
    tenant_service: TenantService = Depends(get_tenant_service),
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    if current_user and current_user.tenant_id is not None:
        if checkout_req.tenant_id != current_user.tenant_id:
            logger.error(f"Tenant ID mismatch for the current user. And current user's tenant id is: {current_user.tenant_id} and requested tenant id is: {checkout_req.tenant_id}")
            raise InvalidOperationException(f"Tenant ID mismatch for the current user. {checkout_req.tenant_id}")
    
    if current_user.email != checkout_req.email:
        logger.error(f"Email mismatch for the current user. And current user's email is: {current_user.email} and requested email is: {checkout_req.email}")
        raise InvalidOperationException(f"Email mismatch for the current user. {checkout_req.email}")

    tenant = await tenant_service.get_tenant_by_id(current_user.tenant_id)
    domain = tenant.subdomain
    if tenant.custom_domain not in (None, ""):
        domain = tenant.custom_domain
    frontend_url = f"https://{domain}"
    url = await billing_service.create_tenant_check_out_session_for_tenant_users(
        frontend_url=frontend_url,
        user_id=current_user.id,
        checkout_req=checkout_req
    )
    return CheckoutResponseDto(checkout_url=url)



@router.post("/host/payment/success", status_code=status.HTTP_202_ACCEPTED)
async def host_checkout_success(
    session_id: str,
    tenant_id: str,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    if current_user.tenant_id != tenant_id:
        logger.error(f"Tenant ID mismatch for the current user. And current user's tenant id is: {current_user.tenant_id} and requested tenant id is: {tenant_id}")
        raise InvalidOperationException(f"Tenant ID mismatch for the current user. {tenant_id}")
    
    await billing_service.handle_host_checkout_success(session_id=session_id, tenant_id=current_user.tenant_id)
    return status.HTTP_202_ACCEPTED


@router.post("/host/payment/cancel", status_code=status.HTTP_202_ACCEPTED)
async def host_checkout_success(
    tenant_id: str,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    if current_user.tenant_id != tenant_id:
        logger.error(f"Tenant ID mismatch for the current user. And current user's tenant id is: {current_user.tenant_id} and requested tenant id is: {tenant_id}")
        raise InvalidOperationException(f"Tenant ID mismatch for the current user. {tenant_id}")
    
    await billing_service.handle_host_checkout_canceled(tenant_id=current_user.tenant_id)
    return status.HTTP_202_ACCEPTED


@router.post("/tenant/payment/success", status_code=status.HTTP_202_ACCEPTED)
async def tenant_checkout_success(
    session_id: str,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    await billing_service.handle_tenant_checkout_success(session_id=session_id, user_id=current_user.id)
    return status.HTTP_202_ACCEPTED


@router.post("/tenant/payment/cancel", status_code=status.HTTP_202_ACCEPTED)
async def tenant_checkout_canceled(
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    await billing_service.handle_tenant_checkout_canceled(user_id=current_user.id)
    return status.HTTP_202_ACCEPTED


@router.get("/all", response_model=BillingRecordListDto, status_code=status.HTTP_200_OK)
async def list_checkout_records(
    skip: int = 0, limit: int = 100,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_BILLING])),
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    return await billing_service.list_checkout_records(skip=skip, limit=limit)

