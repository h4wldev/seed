from typing import Optional

from pydantic import BaseModel, Field, validator

from seed.utils.regex_patterns import email_pattern


class RegisterSchema(BaseModel):
    code: str = Field(..., min_length=20)
    email: str = Field(..., max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=50)
    email_promotion: Optional[bool] = Field(True)
    email_notification: Optional[bool] = Field(True)

    @validator('email')
    def email_pattern(
        cls,
        value: str
    ) -> str:
        if not email_pattern.match(value):
            raise ValueError('must email pattern')

        return value


class SocialInfoSchema(BaseModel):
    social_id: str = Field(...)
    provider: str = Field(...)
