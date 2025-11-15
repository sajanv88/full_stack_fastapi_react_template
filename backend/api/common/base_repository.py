from typing import Any, Dict, List, Optional, TypeVar, Generic
from beanie import Document, PydanticObjectId
from beanie.operators import Set
from beanie.odm.interfaces.aggregate import DocumentProjectionType, AggregationQuery
from api.common.utils import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=Document)

class BaseRepository(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    async def single_or_none(self, **kwargs) -> Optional[T]:
        result = await self.model.find(kwargs).first_or_none()
        return result
    
    async def get(self, id: str) -> Optional[T]:
        result = await self.model.find_one({"_id": PydanticObjectId(id)})
        logger.debug(f"Get result for id {id}: {result}")
        return result

    async def list(self) -> List[T]:
        results = await self.model.find_all().to_list()
        return results
    
    async def search(self, query: Dict[str, Any], limit: int = 100) -> List[T]:      
        results = await self.model.find(query).to_list(length=limit)
        return results
    
    async def create(self, data: dict) -> T:
        doc = self.model(**data)
        result = await doc.insert()
        return result


    async def update(self, id: str, data: dict) -> Optional[T]:
        doc = await self.get(id)
        if not doc:
            return None
        await doc.update(Set(data))
        return doc

    async def delete(self, id: str) -> bool:
        doc = await self.get(id)
        logger.info(f"Deleting document with id: {id}, Found doc: {doc is not None}")
        if not doc:
            return False
        await doc.delete()
        logger.info(f"Document with id: {id} deleted successfully.")
        return True
    
    async def count(self, params: Optional[Any] | None = None) -> int:
        if params:
            return await self.model.find(params).count()
        return await self.model.count()

    async def aggregate(self, pipeline: List[dict], projection_model: type[DocumentProjectionType] | None = None) -> type[DocumentProjectionType] | AggregationQuery[Dict[str, Any]]:
        if not projection_model:
            return self.model.aggregate(pipeline)
        else:
            data = self.model.aggregate(pipeline, projection_model=projection_model)
            return await data.to_list()
        
    async def collection_name(self) -> str:
        return self.model.get_collection_name()
