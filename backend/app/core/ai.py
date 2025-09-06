from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage
from typing import List, Union
import time


MAX_HISTORY = 10

llm = ChatOllama(
    model="llama3.2-vision:11b",  # must match your `ollama run` model name
    streaming=True
)

# Create a simple chain
prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant talking to {username}.\n\n{history}\nUser: {question}\nAssistant:"
)
chain = prompt | llm

class OllamaChat:
    def __init__(self, username: str):
        self.history: List[BaseMessage] = []
        self.username = username
        self.history.append(SystemMessage(content=f"The user’s name is {username}. Please refer to them by name."))

    def generate_response(self, question: str):
        self.history.append(HumanMessage(content=question))
        print(f"Generating response for question: {question}")
        def event_stream():
            output = ""
            recent_history = self.history[-MAX_HISTORY:]

            for chunk in chain.stream({"question": question, "history": recent_history, "username": self.username}):
                output += chunk.content
                yield chunk.content
                time.sleep(0.01)
            self.history.append(AIMessage(content=output))
        return event_stream
    
    