
from typing import Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime

from pymongo import ASCENDING, IndexModel

from api.common.utils import get_utc_now
from api.domain.entities.api_base_model import ApiBaseModel
from webauthn.helpers.structs import (
    AuthenticatorTransport
)
class Credential(BaseModel):
    credential_id: str
    public_key: str
    sigin_count: int
    transports: list[AuthenticatorTransport] = []
    created_at: datetime

class UserPasskey(ApiBaseModel):
    user_email: EmailStr
    credentials: list[Credential] = []
    class Settings:
        name = "user_passkeys"


class Challenges(ApiBaseModel):
    email: EmailStr
    type: Literal["registration", "authentication"] = "registration"
    challenge: str
    expires_at: datetime = get_utc_now()

    class Settings:
        name = "user_passkey_challenges"
        indexes = [
            IndexModel(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=300  # Document expires 5 minutes after 'expired_at'
            )
        ]
    