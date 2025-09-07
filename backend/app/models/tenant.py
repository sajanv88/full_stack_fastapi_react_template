from typing import Optional

from pydantic import BaseModel


class Tenant(BaseModel):
    id: str
    name: str
    subdomain: Optional[str] = None
