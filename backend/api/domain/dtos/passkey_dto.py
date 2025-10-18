
from webauthn.helpers.structs import AuthenticatorTransport
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegisteredPasskeyCredentialsDto(BaseModel):
    credential_id: str
    public_key: str
    sigin_count: int
    transports: list[AuthenticatorTransport] = []
    created_at: datetime
    last_used_at: Optional[datetime] = None
