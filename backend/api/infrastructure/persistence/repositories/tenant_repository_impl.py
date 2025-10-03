from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.exceptions import ConflictException
from api.common.utils import get_logger
from api.domain.dtos.tenant_dto import CreateTenantDto, TenantListDto
from api.domain.entities.tenant import Tenant
from pymongo.errors import DuplicateKeyError

logger = get_logger(__name__)

class TenantRepository(BaseRepository[Tenant]):
    def __init__(self):
        super().__init__(Tenant)

    async def list(self, skip: int = 0, limit: int = 10) -> TenantListDto:
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        tenant_dto = [await doc.to_serializable_dict() for doc in docs]
        return TenantListDto(
            tenants=tenant_dto,
            skip=skip,
            limit=limit,
            total=total,
            hasPrevious=skip > 0,
            hasNext=skip + limit < total
        )
    
    async def create(self, data: CreateTenantDto) -> PydanticObjectId | None:
        try:
            new_tenant = Tenant(
                name=data.name,
                subdomain=data.subdomain
            )
            result = await super().create(new_tenant.model_dump())
            return result.id
        except DuplicateKeyError as ex:
            logger.error(f"Error creating tenant: {str(ex)}")
            raise ConflictException("Tenant", data.name)
    