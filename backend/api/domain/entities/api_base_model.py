from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field, field_serializer
from pymongo.asynchronous.collection import AsyncCollection

from api.common.tenant_context import get_active_database
from api.common.utils import get_utc_now


class ApiBaseModel(Document):
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
    tenant_id: Optional[PydanticObjectId] = None

    @classmethod
    def get_pymongo_collection(cls) -> AsyncCollection:
        """Every Beanie operation resolves its collection here, which makes this the tenant routing point."""
        database = get_active_database()
        if database is None:
            return super().get_pymongo_collection()
        return database[cls.get_collection_name()]

    # Todo: Remove all the to_serializable_dict methods and use field_serializers instead
    # @field_serializer("created_at", "updated_at", "tenant_id")
    # def serialize_object_id(self, value):
    #     if isinstance(value, PydanticObjectId):
    #         return str(value)
    #     return str(value)
        
    
    async def to_serializable_dict(self):
        data = self.model_dump()
        data["id"] = str(self.id)
        data["created_at"] = str(self.created_at)
        data["updated_at"] = str(self.updated_at)
        if self.tenant_id:
            data["tenant_id"] = str(self.tenant_id)
        return data



