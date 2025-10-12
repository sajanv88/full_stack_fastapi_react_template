from typing import Literal, Optional
from pydantic import BaseModel

class CoolifyAppDto(BaseModel):
    uuid: str
    name: str
    fqdn: Optional[str] = None

    

class UpdateCoolifyAppDto(BaseModel):
    domain: str

class UpdateDomainDto(UpdateCoolifyAppDto):
    mode: Literal["add", "remove"] = "add"
    