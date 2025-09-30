from typing import Any, Dict, List, Optional, TypeVar, Generic
from beanie import Document, PydanticObjectId
from beanie.operators import Set
from beanie.odm.interfaces.aggregate import DocumentProjectionType, AggregationQuery

T = TypeVar("T", bound=Document)

class BaseRepository(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    async def single_or_none(self, **kwargs) -> Optional[T]:
        return await self.model.find(kwargs).first_or_none()
    
    async def get(self, id: str) -> Optional[T]:
        return await self.model.get(PydanticObjectId(id))

    async def list(self) -> List[T]:
        return await self.model.find_all().to_list()

    async def create(self, data: dict) -> T:
        doc = self.model(**data)
        return await doc.insert()

    async def update(self, id: str, data: dict) -> Optional[T]:
        doc = await self.model.get(document_id=id)
        if not doc:
            return None
        await doc.update(Set(data))
        return doc

    async def delete(self, id: str) -> bool:
        doc = await self.model.get(PydanticObjectId(id))
        if not doc:
            return False
        await doc.delete()
        return True
    
    async def count(self, params: Optional[Any] | None = None) -> int:
        if params:
            return await self.model.find(params).count()
        return await self.model.count()

    async def aggregate(self, pipeline: List[dict], projection_model: type[DocumentProjectionType] | None = None) -> type[DocumentProjectionType] | AggregationQuery[Dict[str, Any]]:
        if not projection_model:
            return self.model.aggregate(pipeline)
        else:
            return await self.model.aggregate(pipeline, projection_model=projection_model).to_list()
        
    async def collection_name(self) -> str:
        return self.model.get_collection_name()

    
