from pydantic import BaseModel


class PasskeyRepDto(BaseModel):
    rp_id: str
    rp_name: str