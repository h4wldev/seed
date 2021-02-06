from pydantic import BaseModel, Field


class OAuthCodeField(BaseModel):
    provider: str = Field(...)
    code: str = Field(...)