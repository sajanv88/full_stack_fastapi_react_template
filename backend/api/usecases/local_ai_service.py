from typing import List
from uuid import uuid4
from beanie import PydanticObjectId
from api.common.utils import get_logger, get_utc_now
from api.domain.dtos.ai_dto import  AIHistoriesDto, AISessionByUserIdDto
from api.domain.entities.ai import AISessions, ChatHistoryAI, ChatSessionAI
from api.infrastructure.persistence.repositories.chat_history_ai_repository_impl import ChatHistoryAIRepository
from api.infrastructure.persistence.repositories.chat_session_ai_repository_impl import ChatSessionAIRepository

logger = get_logger(__name__)


class LocalAIService:
    def __init__(self, 
        chat_session_repository: ChatSessionAIRepository,
        chat_history_repository: ChatHistoryAIRepository
    ) -> None:
        self.chat_session_repository = chat_session_repository
        self.chat_history_repository = chat_history_repository
    
    async def is_session_exists(self, session_id: str) -> bool:
        return await self.chat_session_repository.is_session_exists(session_id)
    

    async def get_user_sessions(self, user_id: str, limit: int = 100) -> List[AISessionByUserIdDto]:
        """
        Get user sessions with chat histories
        1. Match sessions by user_id
        2. Sort by created_at desc
        3. Limit by `limit`
        4. Lookup chat histories by history_id
        5. Return sessions with chat histories
        6. Convert ObjectId to str in the result
        7. Return the result as List[AISessionByUserIdDto]
        """
        pipeline = [
          {"$match": {"user_id": PydanticObjectId(user_id)}},
          {"$sort": {"created_at": -1}},
          {"$limit": limit},
          {"$lookup": {
              "from": await self.chat_history_repository.collection_name(),
              "localField": "history_id",
              "foreignField": "_id",
              "as": "sessions"
          }}
        ]
        sessions = await self.chat_session_repository.aggregate(pipeline, projection_model=AISessions)
        results: List[AISessionByUserIdDto] = []
        for s in sessions:
            serializable_dict = await s.to_serializable_dict()
            if "sessions" in serializable_dict:
                serializable_dict["sessions"] = [await session.to_serializable_dict() for session in s.sessions]
            results.append(AISessionByUserIdDto(**serializable_dict))
        logger.debug(f"Found {len(results)} sessions for user_id: {user_id}")
        return results
    

    async def get_histories_by_session_id(self, user_id: str, session_id: str) -> List[AIHistoriesDto]:
        session = await self.chat_session_repository.single_or_none(session_id=PydanticObjectId(session_id), user_id=PydanticObjectId(user_id))
        if not session:
            return []
        history = await self.chat_history_repository.single_or_none(_id=session.history_id)
        if not history:
            return []
        serializable_dict = await history.to_serializable_dict()
        if "histories" in serializable_dict:
            serializable_dict["histories"] = [history.to_serializable_dict() for history in history.histories]

        logger.debug(f"Found histories for session_id: {session_id}, user_id: {user_id}")
        return [AIHistoriesDto(**serializable_dict)]
    
    
    async def delete_session(self, user_id: str, session_id: str) -> None:
        session = await self.chat_session_repository.single_or_none(session_id=PydanticObjectId(session_id), user_id=PydanticObjectId(user_id))
        if not session:
            return
        logger.debug(f"Deleted session for user_id: {user_id}, session_id: {session_id}")
        history = await self.chat_history_repository.single_or_none(id=session.history_id)
        if history:
            logger.debug(f"Deleting history for session_id: {session_id}, user_id: {user_id} and history_id: {session.history_id}")
            await history.delete()
        await session.delete()
        
    

    async def save_user_query(self, user_id: str, query: str, response: str, session_id: str | None = None, tenant_id: str | None = None) -> None:
        session = await self.chat_session_repository.single_or_none(session_id=PydanticObjectId(session_id))

        histories = {
            "histories": {
                "uid": str(uuid4()),
                "query": query,
                "response": response,
                "timestamp": get_utc_now()
            }
        }
        data = ChatHistoryAI(
            histories=[histories["histories"]],
            tenant_id=PydanticObjectId(tenant_id) if tenant_id else None,
            id=PydanticObjectId(),
            created_at=get_utc_now(),
            updated_at=get_utc_now()
        )
        # If session does not exist, then there is no history, so create a new history
        if session is None:
            new_history = await self.chat_history_repository.create(data=data.model_dump())
            session = ChatSessionAI(
                session_id=PydanticObjectId(session_id) if session_id else PydanticObjectId(),
                user_id=PydanticObjectId(user_id),
                history_id=new_history.id,
                created_at=get_utc_now(),
                tenant_id=PydanticObjectId(tenant_id) if tenant_id else None
            )
            new_session = await self.chat_session_repository.create(data=session.model_dump())
            logger.debug(f"New chat history saved for user: {user_id}, session: {new_session.id} and history: {new_history.id}")
        else:
            exisiting_history = await self.chat_history_repository.single_or_none(_id=session.history_id)
            if not exisiting_history:
                logger.error(f"Chat history not found for user: {user_id}, session: {session.id} and history: {session.history_id}")
                return
            exisiting_history.histories.append(histories["histories"])
            exisiting_history.updated_at = get_utc_now()
            await exisiting_history.save()
            logger.debug(f"Chat history updated for user: {user_id}, session: {session.id} and history: {session.history_id}")
