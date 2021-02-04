import uuid

from typing import Any, Dict, Optional, Iterator

from fastapi import status

from seed.request import Request as SeedRequest


class HTTPException(Exception):
    _default_status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        symbol: str,
        message: Optional[str] = None,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        status_code: Optional[int] = None,
        request: Optional['Request'] = None
    ) -> None:
        self.trace_id: str = uuid.uuid4()

        self.symbol: str = symbol
        self.message: str = message
        self.detail: Any = detail
        self.headers: Optional[Dict[str, str]] = headers
        self.status_code: int = status_code
        self.request: Optional['Request'] = request

        self.type_: str = self.__class__.__name__

        if self.status_code is None:
            self.status_code = self._default_status_code

    def __repr__(self) -> str:
        return f"<{self.type_} symbol='{self.symbol}' status_code={self.status_code}>"

    def __iter__(self) -> Iterator[Any]:
        iterate_dict: Dict[str, Any] = {
            'trace_id': str(self.trace_id),
            'symbol': self.symbol,
            'message': self.message,
            'detail': self.detail,
            'headers': self.headers,
            'status_code': self.status_code,
            'type': self.type_
        }

        for key, value in iterate_dict.items():
            if value is None:
                continue

            yield (key, value)


class AuthHTTPException(HTTPException):
    pass


class OAuthHTTPException(HTTPException):
    pass
