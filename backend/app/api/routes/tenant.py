from typing import List
from typing_extensions import Annotated
from fastapi import BackgroundTasks, Depends, APIRouter, status, HTTPException
from pydantic import BaseModel

from app.models.tenant import Tenant
from app.api.routes.auth import get_current_user
from app.core.permission import Permission
from app.services.tenant_service import TenantService
from app.core.db import get_db_reference
from app.core.role_checker import create_permission_checker
from app.services.auth_service import AuthService
from app.models.user import NewUser, User

router = APIRouter(prefix="/tenants")
router.tags = ["Tenants"]


class TenantListData(BaseModel):
    tenants: List[Tenant]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool

class TenantListResponse(BaseModel):
    status: int
    message: str
    data: TenantListData

class NewTenantCreateRequest(BaseModel):
    subdomain: str
    admin_email: str
    admin_password: str
    first_name: str
    last_name: str
    gender: str


@router.get("/", response_model=TenantListResponse)
async def get_tenants(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0, limit: int = 10,
     _: bool = Depends(create_permission_checker([Permission.HOST_MANAGE_TENANTS])),
    db = Depends(get_db_reference)
):
    tenant_service = TenantService(db)
    tenants = await tenant_service.list_tenants(skip=skip, limit=limit)
    total = await tenant_service.total_count()
    hasPrevious = skip > 0
    hasNext = (skip + limit) < total
    
    data = TenantListData(
        tenants=tenants,
        skip=skip,
        limit=limit,
        total=total,
        hasPrevious=hasPrevious,
        hasNext=hasNext
    )
    
    return TenantListResponse(
        status=status.HTTP_200_OK,
        message="Tenants retrieved successfully",
        data=data
    )

@router.post("/", response_model=Tenant)
async def create_tenant(
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: NewTenantCreateRequest,
    background_tasks: BackgroundTasks,
    _: bool = Depends(create_permission_checker([Permission.HOST_MANAGE_TENANTS])),
    db = Depends(get_db_reference)
):
    try:
        auth_service = AuthService(db)
        return await auth_service.register_user(NewUser(
            email=tenant.admin_email,
            password=tenant.admin_password,
            first_name=tenant.first_name,
            last_name=tenant.last_name,
            gender=tenant.gender,
            sub_domain=tenant.subdomain
        ), background_tasks=background_tasks)
    except Exception as e:
        print(f"Error creating tenant: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tenant")


@router.get("/search_by_name", response_model=Tenant)
async def search_tenant_by_name(
    name: str,
    db = Depends(get_db_reference)
):
    tenant_service = TenantService(db)
    tenant = await tenant_service.find_by_name(name)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant