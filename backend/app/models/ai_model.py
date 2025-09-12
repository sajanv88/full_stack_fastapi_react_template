from openai import BaseModel


class AiModel(BaseModel):
    name: str
    digest: str
    size: str
    created: str