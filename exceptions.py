from typing import Any, Dict, Optional, Union

from fastapi import HTTPException as FastAPIHTTPException

from utils.http import HTTPStatusCode


class HTTPException(FastAPIHTTPException):
    _default_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(
        self,
        status_code: Optional[Union[int, HTTPStatusCode]] = None,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        if status_code is None:
            status_code = self._default_status_code

        if isinstance(status_code, HTTPStatusCode):
            status_code = status_code.value

        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class JWTHTTPException(HTTPException):
    _default_status_code = HTTPStatusCode.BAD_REQUEST


class RoleHTTPException(HTTPException):
    _default_status_code = HTTPStatusCode.FORBIDDEN
