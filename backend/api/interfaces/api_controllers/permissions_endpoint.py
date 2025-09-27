from fastapi import APIRouter

from api.domain.dtos.permission_dto import PermissionDto
from api.domain.enum.permission import Permission


router = APIRouter(prefix="/permissions")
router.tags = ["Permissions"]


@router.get("/", response_model=list[PermissionDto])
async def get_permissions():
    permissions = [{"name": perm.value} for perm in Permission]
    return permissions
