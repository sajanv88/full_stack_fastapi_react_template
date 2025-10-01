from fastapi import APIRouter, Depends, status

from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.utils import get_logger
from api.core.container import   get_tenant_service
from api.core.exceptions import TenantNotFoundException
from api.domain.dtos.tenant_dto import CreateTenantResponseDto, SubdomainAvailabilityDto, TenantDto, TenantListDto, CreateTenantDto
from api.domain.dtos.user_dto import CreateUserDto
from api.domain.entities.tenant import Subdomain
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.tenant_service import TenantService
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation, handle_post_tenant_deletion

logger = get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=TenantListDto, status_code=status.HTTP_200_OK)
async def list_tenants(
    skip: int = 0, limit: int = 10,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))    
):
    return await service.list_tenants(skip=skip, limit=limit)

@router.post("/", response_model=CreateTenantResponseDto, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: CreateTenantDto,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))
):
    tenant_id = await service.create_tenant(data)
    response = CreateTenantResponseDto(id=str(tenant_id))
    admin_user = CreateUserDto(
        email=data.admin_email,
        password=data.admin_password,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender,
        tenant_id=response.id
    )
    payload=WorkerPayloadDto(
        label="post-tenant-creation",
        data=admin_user,
        tenant_id=response.id
    )
    handle_post_tenant_creation.delay(
        payload=payload.model_dump_json()
    )
    return response


@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tenant(
    id: str,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))
):
    await service.delete_tenant(tenant_id=id)
    payload=WorkerPayloadDto(
        label="post-tenant-deletion",
        data=None,
        tenant_id=id
    )
    handle_post_tenant_deletion.delay(payload=payload.model_dump_json())
    return status.HTTP_202_ACCEPTED


@router.get("/search_by_name/{name}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_name(
    name: str,
    service: TenantService = Depends(get_tenant_service)
):

    tenant = await service.find_by_name(name)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)


@router.get("/search_by_subdomain/{subdomain}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_subdomain(
    subdomain: Subdomain,
    service: TenantService = Depends(get_tenant_service)
):
    tenant = await service.find_by_subdomain(subdomain)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)


@router.get("/check_subdomain/{subdomain}", response_model=SubdomainAvailabilityDto, status_code=status.HTTP_200_OK)
async def check_subdomain_availability(
    subdomain: Subdomain,
    service: TenantService = Depends(get_tenant_service)
):
    try: 
        await service.find_by_subdomain(subdomain)
        is_available = False
    except TenantNotFoundException as e:
        is_available = True

    return SubdomainAvailabilityDto(is_available=is_available)