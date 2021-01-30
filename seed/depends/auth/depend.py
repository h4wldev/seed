from fastapi import (
    Header,
    Request
)
from typing import Any, Callable, List, Optional, Tuple, Union

from seed.db import db
from seed.exceptions import JWTHTTPException
from app.models import UserModel
from seed.setting import setting

from .types import JWTToken, JWTTokenType
from .util import AuthUtil


class Auth(AuthUtil, JWTTokenType):
    token: Optional[JWTToken] = None

    def __init__(
        self,
        required: bool = False,
        token_type: Optional[str] = None,
        user_loader: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self.required: bool = required
        self.token_type: str = token_type or self.ACCESS_TOKEN
        self.user_loader: Callable[str, Any] = user_loader or self._user_loader

    def __call__(
        self,
        request: Request,
        authorization: Optional[str] = Header(None)
    ) -> 'Auth':
        credential: Optional[str] = self._get_credential(
            request=request,
            authorization=authorization
        )

        if credential is not None:
            self.token: JWTToken = JWTToken(credential)

            if self.token.token_type != self.token_type:
                raise JWTHTTPException(f"Token type must be '{self.token_type}'")

            if not self.token.verify():
                raise JWTHTTPException('Signature has expired or not verified')
        elif self.required:
            raise JWTHTTPException('JWT credential required')

        return self

    @property
    def user(self) -> Any:
        if self.token is None:
            return None

        return self.user_loader(self.token.subject)

    def _get_credential(
        self,
        request: Request,
        authorization: Optional[str] = None
    ) -> Optional[str]:
        credential: Optional[str] = None

        for m in ['cookie', 'header']:
            method: Callable[..., str] = getattr(
                self, f'_get_credential_{m.lower()}'
            )
            args: Tuple[Union[str, Request]] = (
                (authorization,) if m == 'header' else (request,)
            )

            _credential: Optional[str] = method(*args)

            if _credential is not None:
                credential = _credential

        return credential

    def _get_credential_cookie(
        self,
        request: Request
    ) -> str:
        cookie_key: str = setting.jwt.cookie.key.get(self.token_type, self.token_type)
        credential: Optional[str] = request.cookies.get(
            cookie_key, None
        )

        return credential

    def _get_credential_header(
        self,
        authorization: Optional[str]
    ) -> str:
        if authorization is None:
            return None

        tokens: List[str] = str(authorization).split(' ')

        if len(tokens) != 2:
            raise JWTHTTPException("Authorization header must like 'Bearer <credentials>'")

        type_: str = tokens[0]
        credential: str = tokens[1]

        if type_ != 'Bearer':
            raise JWTHTTPException("Authorization token type must be 'Bearer'")

        return credential

    def _user_loader(
        self,
        subject: str
    ) -> Optional[UserModel]:  # pragma: no cover
        user_key_field: 'Column' = getattr(UserModel, setting.user_key_field)

        return db.session.query(UserModel)\
            .filter(user_key_field == subject)\
            .first()
