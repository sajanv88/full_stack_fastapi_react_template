from fastapi import APIRouter, Depends, status

from api.common.exceptions import InvalidOperationException
from api.core.container import get_stripe_setting_service
from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto, StripeSettingDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.stripe_setting_service import StripeSettingService


router = APIRouter(prefix="/stripe", dependencies=[Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_PAYMENTS_SETTINGS]))])
router.tags = ["Stripe"]

@router.post("/configure", status_code=status.HTTP_201_CREATED)
async def configure_stripe_setting(
    configuration: CreateStripeSettingDto,
    current_user: CurrentUser,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service)
):
    if not current_user.tenant_id:
        raise InvalidOperationException("Tenant context is required to configure Stripe settings.")

    await stripe_setting_service.configure_stripe_settings(settings=configuration, tenant_id=str(current_user.tenant_id))
    return status.HTTP_201_CREATED

@router.get("/", response_model=StripeSettingDto, status_code=status.HTTP_200_OK)
async def get_stripe_settings(
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service)
):
    return await stripe_setting_service.get_stripe_settings()