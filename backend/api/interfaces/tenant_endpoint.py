from fastapi import APIRouter, Depends, status
from typing import List
from api.common.utils import get_logger
from api.core.container import get_tenant_service
from api.domain.dtos.tenant_dto import CreateTenantResponseDto, TenantDto, TenantListDto, CreateTenantDto
from api.domain.entities.tenant import Subdomain
from api.usecases.tenant_service import TenantService


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
    service: TenantService = Depends(get_tenant_service)
):
    tenant_id = await service.create_tenant(data)
    return CreateTenantResponseDto(id=str(tenant_id))


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
