from typing_extensions import Annotated
from fastapi import Depends, APIRouter, status, HTTPException, Response
from pydantic import BaseModel

from app.models.user import User
from app.api.routes.auth import get_current_user
from app.core.permission import Permission

class PermissionBase(BaseModel):
    name: str

router = APIRouter(prefix="/permissions")
router.tags = ["Permissions"]


@router.get("/", response_model=list[PermissionBase])
async def get_permissions(current_user: Annotated[User, Depends(get_current_user)]):
    permissions = [{"name": perm.value} for perm in Permission]
    return permissions
