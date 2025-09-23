from fastapi import APIRouter, BackgroundTasks, Depends, status

from api.common.utils import get_logger
from api.core.container import  get_role_service, get_tenant_service, get_user_service
from api.domain.dtos.tenant_dto import CreateTenantResponseDto, TenantDto, TenantListDto, CreateTenantDto
from api.domain.dtos.user_dto import CreateUserDto
from api.domain.entities.tenant import Subdomain
from api.infrastructure.background.post_tenant_creation_task_service import PostTenantCreationTaskService
from api.infrastructure.persistence.mongodb import mongo_client
from api.usecases.role_service import RoleService
from api.usecases.tenant_service import TenantService
from api.usecases.user_service import UserService


logger = get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=TenantListDto)
async def list_tenants(
    skip: int = 0, limit: int = 10,
    service: TenantService = Depends(get_tenant_service)
):
    return await service.list_tenants(skip=skip, limit=limit)

@router.post("/", response_model=CreateTenantResponseDto, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: CreateTenantDto,
    background_tasks: BackgroundTasks,
    service: TenantService = Depends(get_tenant_service),
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service)
):
    tenant_id = await service.create_tenant(data)
    response = CreateTenantResponseDto(id=str(tenant_id))
    admin_user = CreateUserDto(
        email=data.admin_email,
        password=data.admin_password,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender
    )
    post_tenant_creation_service = PostTenantCreationTaskService(
        background_tasks=background_tasks,
        user_service=user_service,
        role_service=role_service,
        database=mongo_client
    )
    await post_tenant_creation_service.enqueue(admin_user=admin_user, tenant_id=str(tenant_id))
    return response



@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tenant(id: str, service: TenantService = Depends(get_tenant_service)):
    await service.delete_tenant(tenant_id=id)
    return status.HTTP_202_ACCEPTED


@router.get("/search_by_name/{name}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_name(name: str, service: TenantService = Depends(get_tenant_service)):
    tenant = await service.find_by_name(name)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)


@router.get("/search_by_subdomain/{subdomain}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_subdomain(subdomain: Subdomain, service: TenantService = Depends(get_tenant_service)):
    tenant = await service.find_by_subdomain(subdomain)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)
