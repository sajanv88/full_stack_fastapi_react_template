
from fastapi import APIRouter

from api.common.utils import get_logger
from api.domain.dtos.permission_dto import PermissionDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser

logger = get_logger(__name__)

router = APIRouter(prefix="/permissions")
router.tags = ["Permissions"]


@router.get("/", response_model=list[PermissionDto])
async def get_permissions(
    current_user: CurrentUser
):
    permissions = [{"name": perm.value} for perm in Permission]
    if current_user.tenant_id:
        logger.debug("Filtering out host-level permissions for tenant user")
        permissions = filter(
            lambda p: not p["name"].startswith("host:"),
            permissions
        )
        permissions = list(permissions)

    return permissions
