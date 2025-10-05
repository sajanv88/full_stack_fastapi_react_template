import subprocess
from typing import List
from fastapi import BackgroundTasks
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage
from api.common.utils import format_bytes_to_human_readable_size, get_logger
from api.domain.dtos.ai_dto import AIModelInfoDto
from api.usecases.local_ai_service import LocalAIService
from api.core.config import settings
import requests
import time

logger = get_logger(__name__)


class OllamaModels:
    """
        Interacts with the local Ollama AI models. Requires Ollama to be installed and configured in the environment.
    """
    def list_models(self) -> List[AIModelInfoDto]:
        """
            Lists available AI models using the Ollama CLI.
        """
        models: List[AIModelInfoDto] = []
        try:
            response = requests.get(f"{settings.ollama_host}/api/tags")
            if response.status_code != 200:
                logger.error(f"Failed to fetch models from Ollama API: {response.status_code} - {response.text}")
                raise Exception(f"Failed to fetch models from Ollama API: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Ollama models fetched: {data}")
            for item in data["models"]:
                models.append(AIModelInfoDto(
                    name=item["name"],
                    digest=item["digest"],
                    size=format_bytes_to_human_readable_size(item["size"]),
                    created=item["modified_at"]
                ))
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
        finally:
            return models


class OllamaChat:
    def __init__(self, 
        user_id: str, 
        username: str, 
        model_name: str, 
        current_session: str, 
        local_ai_service: LocalAIService, 
        tenant_id: str = None
        ):
        self.MAX_HISTORY = 10
        self.history: List[BaseMessage] = []
        self.user_id = user_id
        self.username = username
        self.model_name = model_name
        self.local_ai_service = local_ai_service
        self.current_session = current_session
        self.tenant_id = tenant_id
        self.history.append(SystemMessage(content=f"The user’s name is {username}. Please refer to them by name."))
        self.llm = ChatOllama(model=model_name, streaming=True)
        self.prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant talking to {username}.\n\n{history}\nUser: {question}\nAssistant:"
        )
        self.chain = self.prompt | self.llm
        

    async def feed_previous_conversations(self, history_service: LocalAIService):
        is_session_valid = await history_service.is_session_exists(self.current_session)
        if is_session_valid is False:
            logger.debug("No previous chat history session found!")
            return

        logger.info(f"Using existing session: {self.current_session} for user: {self.username}")
        logger.debug(f"Current history before fetching from DB: {self.history}")
        stored_history = await history_service.get_histories_by_session_id(self.user_id, self.current_session)
        logger.debug(f"Stored history fetched from DB: {stored_history}")
        previous_histories = stored_history["histories"]
        logger.debug(f"Memory fetched from DB: {len(previous_histories)} items")
        for item in previous_histories:
            self.history.append(HumanMessage(content=item["query"]))
            self.history.append(AIMessage(content=item["response"]))
    

    async def generate_response(self, question: str, background_tasks: BackgroundTasks):
        await self.feed_previous_conversations(self.local_ai_service)

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
            background_tasks.add_task(self.local_ai_service.save_user_query,
                user_id=self.user_id,
                query=question,
                response=output,
                session_id=self.current_session,
                tenant_id=self.tenant_id,
            )
        return event_stream