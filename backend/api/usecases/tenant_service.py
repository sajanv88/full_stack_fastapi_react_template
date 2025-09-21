from beanie import PydanticObjectId
from api.common.utils import get_logger, validate_password
from api.core.exceptions import TenantNotFoundException
from api.domain.dtos.tenant_dto import CreateTenantDto, TenantListDto
from api.domain.entities.tenant import Tenant
from api.infrastructure.persistence.repositories.tenant_repository_impl import TenantRepository

logger = get_logger(__name__)

class TenantService:
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
        logger.info("Initialized.")


    async def list_tenants(self, skip: int = 0, limit: int = 10) -> TenantListDto:
        return await self.tenant_repository.list(skip=skip, limit=limit)

    async def find_by_name(self, name: str) -> Tenant | None:
        exisiting = await self.tenant_repository.single_or_none(name=name)
        if exisiting is None:
            raise TenantNotFoundException(name)
        return exisiting

    async def find_by_subdomain(self, subdomain: str) -> Tenant | None:
        existing = await self.tenant_repository.single_or_none(subdomain=subdomain)
        if existing is None:
            raise TenantNotFoundException(subdomain)
        return existing

    async def get_tenant_by_id(self, tenant_id: str) -> Tenant | None:
        existing = await self.tenant_repository.get(id=tenant_id)
        if existing is None:
            raise TenantNotFoundException(tenant_id)
        return existing

    async def create_tenant(self, tenant_data: CreateTenantDto) -> PydanticObjectId | None:
        validate_password(tenant_data.admin_password)
        return await self.tenant_repository.create(tenant_data)
    
    
    async def delete_tenant(self, tenant_id: str) -> None:
        if await self.tenant_repository.delete(id=tenant_id) is None:
            raise TenantNotFoundException(tenant_id)

    async def total_count(self) -> int:
        return await self.tenant_repository.count()