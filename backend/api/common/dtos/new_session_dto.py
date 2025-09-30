from pydantic import BaseModel


class NewSessionResponseDto(BaseModel):
    session_id: str