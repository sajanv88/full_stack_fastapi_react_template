from datetime import datetime
from beanie import PydanticObjectId
from api.common.utils import get_utc_now
from api.domain.entities.api_base_model import ApiBaseModel
from pymongo import ASCENDING, IndexModel


class UserMagicLink(ApiBaseModel):
    user_id: PydanticObjectId
    token: str
    expires_at: datetime = get_utc_now()

    class Settings:
        name = "user_magic_links"

        indexes = [
            IndexModel(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=900 # 15 minutes
            )
        ]