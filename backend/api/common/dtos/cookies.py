from typing import Optional
from pydantic import BaseModel
class Cookies(BaseModel):
    refresh_token: Optional[str] | None = None
    # Add more session Id, facebook_tracking etc..