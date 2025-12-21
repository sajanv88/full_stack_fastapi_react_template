from fastapi import APIRouter, Depends, UploadFile, status
from pydantic import Json
from api.common.utils import get_logger
from api.core.container import get_deps
from api.core.exceptions import BrandingException
from api.domain.dtos.branding_dto import IdentityDto, UpdateBrandingDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.branding_service import BrandingService
from api.usecases.file_service import FileService

logger = get_logger(__name__)

router = APIRouter(prefix="/brandings", dependencies=[Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS]))])
router.tags = ["Branding"]

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_branding(
    current_user: CurrentUser,
    data: UpdateBrandingDto,
    branding_service: BrandingService = Depends(get_deps(BrandingService))
):

    logger.debug(f"Update branding called with data: {data}")  
    branding = await branding_service.get_branding()
    if branding is None:
        data.tenant_id = current_user.tenant_id
        branding = await branding_service.create_branding(data=data)
    else:
        await branding_service.update_branding(id=str(branding.id), data=data)

@router.patch("/{branding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def partial_update_branding(
    current_user: CurrentUser,
    branding_id: str,
    data: UpdateBrandingDto,
    branding_service: BrandingService = Depends(get_deps(BrandingService))
):
    branding = await branding_service.get_branding()
    if branding is None:
        raise BrandingException("Branding not found.")

    data.tenant_id = current_user.tenant_id
    await branding_service.update_branding(id=branding_id, data=data)


@router.put("/logo", status_code=status.HTTP_202_ACCEPTED)
async def upload_logo(
    current_user: CurrentUser,
    file: UploadFile,
    branding_service: BrandingService = Depends(get_deps(BrandingService)),
    file_service: FileService = Depends(get_deps(FileService))
):
    file_content = await file.read()
    logger.debug(f"Received logo file: {file.filename}, size: {len(file_content)} bytes")
    if not file_content:
        raise BrandingException("Uploaded file is empty.")
    if file.content_type not in ["image/png", "image/jpeg", "image/svg+xml"]:
        raise BrandingException("Unsupported file type. Please upload a PNG, JPEG, or SVG image.")
    
    key = await file_service.upload_file(file=file)
    logger.debug(f"Logo uploaded successfully with key: {key}")
    branding = await branding_service.get_branding()
    if branding is None:
        current_user.tenant_id = current_user.tenant_id
        branding = await branding_service.create_branding(data=UpdateBrandingDto(logo_url=key, logo_type=file.content_type))
        return
    

    await branding_service.update_branding(id=str(branding.id), data=UpdateBrandingDto(logo_url=key, logo_type=file.content_type))