from typing import Any, Dict, Optional, Union

from fastapi import HTTPException as FastAPIHTTPException

from utils.http import HTTPStatusCode


class HTTPException(FastAPIHTTPException):
    def __init__(
        self,
        status_code: Union[int, HTTPStatusCode] = 400,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        if isinstance(status_code, HTTPStatusCode):
            status_code = status_code.value

        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class JWTHTTPException(HTTPException):
    pass
