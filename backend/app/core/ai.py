from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage
from typing import List
from app.models.ai_model import AiModel as ModelsResponse
import time
import logging
import subprocess
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.ai_history_service import AIHistoryService

logger = logging.getLogger(__name__)

class OllamaChat:
    def __init__(self, user_id: str, username: str, model_name: str, current_session: str, db: AsyncIOMotorDatabase):
        self.MAX_HISTORY = 10
        self.history: List[BaseMessage] = []
        self.user_id = user_id
        self.username = username
        self.model_name = model_name
        self.current_session = current_session
        self.history.append(SystemMessage(content=f"The user’s name is {username}. Please refer to them by name."))
        self.llm = ChatOllama(model=model_name, streaming=True)
        self.prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant talking to {username}.\n\n{history}\nUser: {question}\nAssistant:"
        )
        self.chain = self.prompt | self.llm
        self.db = db
        

    async def generate_response(self, question: str):
        history_service = AIHistoryService(self.db)
        is_session_valid = await history_service.is_session_exists(self.current_session)
        if is_session_valid:
            logger.info(f"Using existing session: {self.current_session} for user: {self.username}")
            logger.debug(f"Current history before fetching from DB: {self.history}")
            stored_history = await history_service.get_user_history(self.user_id, limit=self.MAX_HISTORY)
            logger.debug(f"Memory fetched from DB: {stored_history.count()}")
            for item in stored_history:
                self.history.append(HumanMessage(content=item["query"]))
                self.history.append(AIMessage(content=item["response"]))

        self.history.append(HumanMessage(content=question))
        logger.debug(f"Generating response for question: {question}")
        async def event_stream():
            output = ""
            recent_history = self.history[-self.MAX_HISTORY:]

            for chunk in self.chain.stream({"question": question, "history": recent_history, "username": self.username}):
                output += chunk.content
                yield chunk.content
                time.sleep(0.01)

            self.history.append(AIMessage(content=output))
            await history_service.save_user_query(
                user_id=self.user_id,
                query=question,
                response=output,
                session_id=self.current_session
            )
        return event_stream


class OllamaModels:
    def list_models(self) -> List[ModelsResponse]:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        models: List[ModelsResponse] = []
        lines = result.stdout.strip().split("\n")
            # Skip header line (first one)
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            name = parts[0]
            digest = parts[1]
            size = parts[2] + (f" {parts[3]}" if parts[3].upper() in ["GB", "MB"] else "")
            created = " ".join(parts[4:])
            models.append(ModelsResponse(
                name=name,
                digest=digest,
                size=size,
                created=created
            ))
        return models
