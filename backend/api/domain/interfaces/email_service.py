from abc import abstractmethod
from typing import Literal, Protocol

from fastapi_mail import MessageType


class IEmailService(Protocol):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, type: Literal[MessageType.html, MessageType.plain]) -> None:
        raise NotImplementedError