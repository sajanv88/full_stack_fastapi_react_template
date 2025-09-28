from datetime import datetime

from beanie import PydanticObjectId
from api.domain.entities.api_base_model import ApiBaseModel


class UserPasswordReset(ApiBaseModel):
    user_id: PydanticObjectId
    token_secret: str
    reset_secret_updated_at: datetime
    first_name: str

    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "user_id": str(self.user_id),
            "token_secret": self.token_secret,
            "reset_secret_updated_at": str(self.reset_secret_updated_at),
            "first_name": self.first_name,
        }

    class Settings:
        name = "user_password_resets"