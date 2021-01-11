from typing import Any, Dict, Optional

from fastapi import status, HTTPException as FastAPIHTTPException


class HTTPException(FastAPIHTTPException):
    _default_status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        detail: Any = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        if status_code is None:
            status_code = self._default_status_code

        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class JWTHTTPException(HTTPException):
    pass


class OAuthHTTPException(HTTPException):
    pass


class RoleHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_403_FORBIDDEN