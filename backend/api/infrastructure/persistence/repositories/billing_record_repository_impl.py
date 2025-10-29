from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.dtos.billing_dto import BillingRecordDto, BillingRecordListDto
from api.domain.entities.stripe_settings import BillingRecord

logger = get_logger(__name__)

class BillingRecordRepository(BaseRepository[BillingRecord]):
    def __init__(self):
        super().__init__(BillingRecord)

    async def list (self, skip: int = 0, limit: int = 10) -> BillingRecordListDto:
        logger.debug(f"Listing billing records with skip={skip} and limit={limit}")
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        result = BillingRecordListDto(
            billing_records=[BillingRecordDto(**doc.model_dump()) for doc in docs],
            skip=skip,
            limit=limit,
            total=total,
            hasPrevious=skip > 0,
            hasNext=skip + limit < total
        )
        return result
    