from fastapi import APIRouter, Depends, status

from api.common.exceptions import InvalidOperationException
from api.core.container import get_stripe_setting_service
from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto, StripeSettingDto
from api.domain.enum.permission import Permission
from api.domain.security.feature_access_management import check_feature_access
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.stripe_setting_service import StripeSettingService
from api.domain.enum.feature import Feature as FeatureEnum


router = APIRouter(prefix="/configurations", dependencies=[
    Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_PAYMENTS_SETTINGS])),
    Depends(check_feature_access(FeatureEnum.STRIPE))
])
router.tags = ["Stripe"]

@router.post("/stripe", status_code=status.HTTP_201_CREATED)
async def configure_stripe_setting(
    configuration: CreateStripeSettingDto,
    current_user: CurrentUser,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service)
):
    if not current_user.tenant_id:
        raise InvalidOperationException("Tenant context is required to configure Stripe settings.")

    await stripe_setting_service.configure_stripe_settings(settings=configuration, tenant_id=str(current_user.tenant_id))
    return status.HTTP_201_CREATED

@router.get("/stripe", response_model=StripeSettingDto, status_code=status.HTTP_200_OK)
async def get_stripe_settings(
    current_user: CurrentUser,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service)
):
    if not current_user.tenant_id:
        raise InvalidOperationException("Tenant context is required to get Stripe settings.")
    return await stripe_setting_service.get_stripe_settings()