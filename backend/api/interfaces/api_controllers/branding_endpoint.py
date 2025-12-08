from fastapi import APIRouter, Depends, status

from api.core.container import get_deps
from api.domain.dtos.branding_dto import UpdateBrandingDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.branding_service import BrandingService


router = APIRouter(prefix="/brandings", tags=["Brandings"], dependencies=[Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS]))])

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_branding(
    current_user: CurrentUser,
    data: UpdateBrandingDto,
    branding_service: BrandingService = Depends(get_deps(BrandingService))
):
    branding = await branding_service.get_branding()
    if branding is None:
        data.tenant_id = current_user.tenant_id
        branding = await branding_service.create_branding(data=data)
    else:
        await branding_service.update_branding(id=str(branding.id), data=data)
    