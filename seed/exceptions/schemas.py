from typing import Any, Dict, Optional, Union, List

from pydantic import BaseModel, Field


class HTTPExceptionSchema(BaseModel):
    trace_id: str = Field(...)
    symbol: str = Field(...)
    status_code: int = Field(400)
    type: str = Field('HTTPException')
    message: Optional[str]
    detail: Optional[Any]
    headers: Optional[Dict[str, Union[str, int]]]


class RequestValidationDetailSchema(BaseModel):
    loc: List[str] = Field([])
    msg: str = Field(...)
    type: str = Field(...)


class RequestValidationExceptionSchema(BaseModel):
    trace_id: str = Field(...)
    symbol: str = Field('request_validation_failed')
    status_code: int = Field(422)
    type: str = Field('RequestValidationError')
    message: Optional[str]
    detail: Optional[RequestValidationDetailSchema]
    headers: Optional[Dict[str, Union[str, int]]]
