from pydantic import BaseModel, Field


class HealthCheckResponseDto(BaseModel):
    status: str = Field(..., example="Ok")