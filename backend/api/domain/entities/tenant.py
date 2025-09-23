from datetime import datetime
import re
from typing import Annotated, Literal
from beanie import Document, Indexed, PydanticObjectId
from pydantic import AfterValidator, ConfigDict
from api.common.utils import get_host_main_domain_name, get_utc_now
from api.core.exceptions import InvalidSubdomainException

SUBDOMAIN_REGEX = re.compile(r"^(?!-)[A-Za-z0-9-]{3,63}(?<!-)$")

def validate_subdomain(subdomain: str | None) -> str | None:
    """Validate subdomain format. Raises InvalidSubdomainException if invalid. Returns None if subdomain is None."""
    if subdomain is None:
        return None
    
    main_domain = get_host_main_domain_name()

    if not subdomain.endswith(f".{main_domain}"):
        raise InvalidSubdomainException(subdomain)

    label = subdomain.replace(f".{main_domain}", "")

    if not SUBDOMAIN_REGEX.match(label):
        raise InvalidSubdomainException(subdomain)

    return subdomain

Subdomain = Annotated[str, AfterValidator(validate_subdomain)]

class Tenant(Document):
    name: str = Indexed(str, unique=True)
    subdomain: Subdomain | None = None
    created_at: datetime = get_utc_now()
    updated_at: datetime = get_utc_now()
    is_active: bool = False
    subdomain_status: Literal["active", "failed", "activation-progress"] = "failed"
    
    model_config = ConfigDict(
        json_encoders={
            PydanticObjectId: str
        }
    )

    async def to_serializable_dict(self):
        data = self.model_dump()
        data["id"] = str(self.id)
        data["created_at"] = str(self.created_at)
        data["updated_at"] = str(self.updated_at)
        data["subdomain"] = str(self.subdomain) if self.subdomain else None
        data["is_active"] = self.is_active 
        data["subdomain_status"] = self.subdomain_status 
        
        return data
    
    class Settings:
        name = "tenants"
    

