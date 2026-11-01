from api.common.exceptions import ApiBaseException
from api.common.utils import get_logger
from api.core.exceptions import BrandingException
from api.domain.dtos.branding_dto import BrandingDto, UpdateBrandingDto
from api.domain.entities.branding import Branding, ThemeConfig
from api.infrastructure.persistence.repositories.branding_repository_impl import BrandingRepository
from api.usecases.file_service import FileService

logger = get_logger(__name__)

class BrandingService:
    def __init__(self, branding_repository: BrandingRepository, file_service: FileService):
        self.branding_repository = branding_repository
        self.file_service = file_service

    def _to_dto(self, branding: Branding) -> BrandingDto:
        # Host level branding has no tenant, the DTO represents that as an empty string.
        return BrandingDto(**{**branding.model_dump(), "tenant_id": str(branding.tenant_id or "")})

    def _to_entity(self, data: UpdateBrandingDto, **dump_options) -> Branding:
        fields = data.model_dump(exclude={"identity"}, exclude_none=True, **dump_options)
        if data.identity:
            fields["app_name"] = data.identity.app_name
        return Branding(**fields)

    async def default_theme_config(self) -> ThemeConfig:
        config = await self.branding_repository.default_theme_config()
        return config

    async def get_branding(self) -> BrandingDto | None:
        res = await self.branding_repository.get_branding()
        logger.debug(f"Fetched branding: {res}")
        if res is None:
            return None
        branding = self._to_dto(res)
        if branding.logo_url:
            try:
                branding.logo_url = await self.file_service.get_file_url(file_key=branding.logo_url)
            except ApiBaseException as e:
                # App configuration is served from this, a storage problem must not take the app down.
                logger.error(f"Could not resolve the logo url: {e}")
                branding.logo_url = None
        return branding
    
    async def update_branding(self, id: str, data: UpdateBrandingDto) -> None:
        try:
            logger.debug(f"Updating branding with ID {id} using data: {data}")
            await self.branding_repository.update_branding(id, self._to_entity(data, exclude_unset=True))
        except Exception as e:
            raise BrandingException(str(e))
        
    async def create_branding(self, data: UpdateBrandingDto) -> BrandingDto:
        if await self.branding_repository.count() > 0:
            raise BrandingException("Branding already exists. Only one branding allowed.")
        
        created_branding = await self.branding_repository.create_branding(data=self._to_entity(data))
        logger.debug(f"Created default branding: {created_branding}")
        return self._to_dto(created_branding)
