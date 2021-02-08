from pydantic import BaseModel, Field


class OAuthCodeSchema(BaseModel):
    provider: str = Field(...)
    code: str = Field(...)