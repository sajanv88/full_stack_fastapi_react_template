from fastapi import APIRouter, status
from fastapi.params import Depends

from api.core.container import get_pricing_service
from api.domain.dtos.pricing_dto import CreatePricingDto, PricingListDto, UpdatePricingDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.pricing_service import PricingService


router = APIRouter(
    prefix="/prices",
    dependencies=[
        Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_PRODUCTS_AND_PRICING]))
    ]

)
router.tags = ["Stripe - Pricing"]

@router.get("/", response_model=PricingListDto)
async def get_pricing_list(
    current_user: CurrentUser,
    pricing_service: PricingService = Depends(get_pricing_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    return await pricing_service.list_prices(scope=scope)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pricing(
    pricing: CreatePricingDto,
    current_user: CurrentUser,
    pricing_service: PricingService = Depends(get_pricing_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    await pricing_service.create_price(scope=scope, price=pricing)
    return status.HTTP_201_CREATED


@router.patch("/{price_id:path}", status_code=status.HTTP_204_NO_CONTENT)
async def update_pricing(
    price_id: str,
    pricing: UpdatePricingDto,
    current_user: CurrentUser,
    pricing_service: PricingService = Depends(get_pricing_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    await pricing_service.update_price(price_id=price_id, scope=scope, update=pricing)
    return status.HTTP_204_NO_CONTENT