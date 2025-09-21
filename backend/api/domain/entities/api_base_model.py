from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId

from api.common.utils import get_utc_now


class ApiBaseModel(Document):
    created_at: datetime = get_utc_now()
    updated_at: datetime = get_utc_now()
    tenant_id: Optional[PydanticObjectId] = None

    
    async def to_serializable_dict(self):
        data = self.model_dump()
        data["id"] = str(self.id)
        data["created_at"] = str(self.created_at)
        data["updated_at"] = str(self.updated_at)
        if self.tenant_id:
            data["tenant_id"] = str(self.tenant_id)
        return data



