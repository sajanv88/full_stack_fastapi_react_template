from typing import List
from fastapi import APIRouter, Depends
from api.domain.enum.feature import Feature as FeatureEnum
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role

router = APIRouter(prefix="/features")
router.tags = ["Features"]

@router.get("/", response_model=List[FeatureEnum], description="List all available features. Requires HOST_MANAGE_TENANTS permission.")
def list_features(
   _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS])) 
):
    return [feature for feature in FeatureEnum]


