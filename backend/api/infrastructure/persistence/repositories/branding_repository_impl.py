from api.common.base_repository import BaseRepository
from api.common.utils import get_utc_now
from api.domain.entities.branding import Branding


class BrandingRepository(BaseRepository[Branding]):
    def __init__(self):
        super().__init__(Branding)
    
    async def get_branding(self) -> Branding | None:
        return await super().single_or_none()
    
    async def update_branding(self, id: str, data: Branding) -> None:
        data.updated_at = get_utc_now()
        await super().update(id, data.model_dump(exclude_unset=True, exclude_none=True))