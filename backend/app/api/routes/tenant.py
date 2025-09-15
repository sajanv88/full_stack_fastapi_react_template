import logging
from typing import List
from typing_extensions import Annotated
from fastapi import BackgroundTasks, Depends, APIRouter, Response, status, HTTPException, Path
from pydantic import BaseModel, EmailStr, field_validator, ValidationError

from app.core.utils import get_host_main_domain_name, validate_subdomain
from app.models.tenant import Tenant
from app.api.routes.auth import get_current_user
from app.core.permission import Permission
from app.services.tenant_service import TenantService
from app.core.db import get_db_reference
from app.core.role_checker import create_permission_checker
from app.services.auth_service import AuthService
from app.models.user import NewUser, User

logger = logging.getLogger(__name__)

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
    admin_email: EmailStr
    admin_password: str
    first_name: str
    last_name: str
    gender: str

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v):
        return validate_subdomain(v)


class CheckSubdomainResponse(BaseModel):
    available: bool




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
        response = await auth_service.register_user(NewUser(
            email=tenant.admin_email,
            password=tenant.admin_password,
            first_name=tenant.first_name,
            last_name=tenant.last_name,
            gender=tenant.gender,
            sub_domain=tenant.subdomain
        ), background_tasks=background_tasks)

        return Tenant(**response["tenant"])
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

@router.get("/check_subdomain/{subdomain}", response_model=CheckSubdomainResponse)
async def check_tenant_by_subdomain(
    subdomain: str = Depends(validate_subdomain),
    db = Depends(get_db_reference)
):
    tenant_service = TenantService(db)
    tenant = await tenant_service.check_subdomain_conflict(subdomain)
    logger.info(f"Subdomain '{subdomain}' conflict check: {'exists' if tenant else 'available'}")
    if tenant:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Subdomain already in use")
    return CheckSubdomainResponse(available=True)


@router.delete("/{tenant_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tenant(
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_reference),
    _: bool = Depends(create_permission_checker([Permission.HOST_MANAGE_TENANTS]))
):
    try:
        tenant_service = TenantService(db)
        await tenant_service.delete_tenant(tenant_id)
        logger.info("Tenant deleted... and initated rest of the deletion process....")
        background_tasks.add_task(tenant_service.drop_tenant_db, tenant_id)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tenant")