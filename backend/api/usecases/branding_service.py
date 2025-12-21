from api.common.utils import get_logger
from api.core.exceptions import BrandingException
from api.domain.dtos.branding_dto import BrandingDto, UpdateBrandingDto
from api.domain.entities.branding import Branding
from api.infrastructure.persistence.repositories.branding_repository_impl import BrandingRepository
from api.usecases.file_service import FileService

logger = get_logger(__name__)

class BrandingService:
    def __init__(self, branding_repository: BrandingRepository, file_service: FileService):
        self.branding_repository = branding_repository
        self.file_service = file_service
    
    async def get_branding(self) -> BrandingDto | None:
        res = await self.branding_repository.get_branding()
        logger.debug(f"Fetched branding: {res}")
        if res is None:
            return None
        branding =  BrandingDto(**res.model_dump())
        if branding.logo_url:
            branding.logo_url = await self.file_service.get_file_url(file_key=branding.logo_url)
        return branding
    
    async def update_branding(self, id: str, data: UpdateBrandingDto) -> None:
        try:
            logger.debug(f"Updating branding with ID {id} using data: {data}")
            await self.branding_repository.update_branding(id, Branding(**data.model_dump(exclude_unset=True, exclude_none=True), app_name=data.identity.app_name))
        except Exception as e:
            raise BrandingException(str(e))
        
    async def create_branding(self, data: UpdateBrandingDto) -> BrandingDto:
        if await self.branding_repository.count() > 0:
            raise BrandingException("Branding already exists. Only one branding allowed.")
        
        branding_data = Branding(**data.model_dump(exclude_unset=True, exclude_none=True))
        created_branding = await self.branding_repository.create(data=branding_data.model_dump())
        logger.debug(f"Created default branding: {created_branding}")
        return BrandingDto(**created_branding.model_dump())