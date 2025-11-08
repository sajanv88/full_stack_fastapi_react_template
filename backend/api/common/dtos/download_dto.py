from pydantic import BaseModel


class DownloadResponseDto(BaseModel):
    message: str
