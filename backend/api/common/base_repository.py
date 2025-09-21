from typing import List, Optional, TypeVar, Generic
from beanie import Document, PydanticObjectId
from beanie.operators import Set

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