from datetime import datetime, timezone
from pydantic import BaseModel


class PasswordReset(BaseModel):
    user_id: str
    token_secret: str
    created_at: datetime
    reset_secret_updated_at: datetime # After this timestamp, all previous tokens are invalid