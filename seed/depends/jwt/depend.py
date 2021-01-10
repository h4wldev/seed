from fastapi import (
    Header,
    Request
)
from fastapi.responses import ORJSONResponse
from typing import Any, Dict, Callable, List, Optional, Tuple, Union

from db import db
from exceptions import JWTHTTPException
from seed.models.user_model import UserModel
from seed.depends.redis import RedisContextManager
from setting import setting

from .types import JWTToken, JWTMode, JWTTokenType


class JWT(JWTMode, JWTTokenType):
    setting: 'Dynaconf' = setting.depend.jwt
    token: Optional[JWTToken] = None

    _user: Any = None

    def __init__(
        self,
        required: bool = False,
        mode: Optional[str] = None,
        token_type: Optional[str] = None,
        user_loader: Optional[Callable[[str], Any]] = None
    ) -> None:
        self.required: bool = required
        self.mode: str = mode
        self.token_type: str = token_type or self.ACCESS_TOKEN
        self.user_loader: Callable[str, Any] = user_loader or self._user_loader

        self.cookie_domain: Optional[str] = None

        if len(self.setting.httponly_cookie.domains):
            self.cookie_domain = ','.join(
                self.setting.httponly_cookie.domains
            )

        if self.mode not in ('BOTH_MODE', 'COOKIE_MODE', 'HEADER_MODE'):
            self.mode = self.BOTH_MODE

    def __call__(
        self,
        request: Request,
        authorization: Optional[str] = Header(None)
    ) -> 'JWT':
        credential: Optional[str] = self._get_credential(
            request=request,
            authorization=authorization
        )

        if self.required and credential is None:
            raise JWTHTTPException('JWT credential required')

        self.token: JWTToken = JWTToken(credential)

        if self.token.token_type != self.token_type:
            raise JWTHTTPException(f"Token type must be '{self.token_type}'")

        if setting.jwt.redis.get('enable', False):
            with RedisContextManager() as r:
                name: str = f'token:{self.token.subject}'
                stored_id: str = r.hget(name=name, key=self.token_type)

                if not stored_id or self.token.id != stored_id.decode():
                    raise JWTHTTPException('Signature has expired or not verified')

        return self

    def get_create_response(
        self,
        subject: str,
        payload: Dict[str, Any] = {},
        token_types: List[str] = ['access', 'refresh'],
        response_type: 'Response' = ORJSONResponse,
        response_headers: Dict[str, Any] = {},
        return_tokens: bool = False
    ) -> Tuple['Response', Dict[str, Any]]:
        tokens: Dict[str, Any] = {}
        content: Dict[str, Any] = {}
        token_types: List[str] = self._token_type_filter(
            token_types=token_types
        )

        if len(token_types) < 0:
            token_types = ['access', 'refresh']

        for t in token_types:
            token: JWTToken = JWTToken.create(
                subject=subject,
                payload=payload,
                token_type=t
            )
            tokens[t]: JWTToken = token
            content[f'{t}_token']: str = token.credential
            content[f'{t}_token_expires']: str = token.expires_in

        response: response_type = response_type(content=content)

        if self.mode in (self.BOTH_MODE, self.COOKIE_MODE):
            for t in token_types:
                response.set_cookie(
                    key=getattr(self.setting.httponly_cookie, f'{t}_token_cookie_key'),
                    value=tokens[t].credential,
                    domain=self.cookie_domain,
                    max_age=tokens[t].expires_in,
                    httponly=True
                )

        if setting.jwt.redis.get('enable', False):
            with RedisContextManager() as r:
                name: str = f'token:{subject}'

                for t in token_types:
                    r.hset(name=name, key=t, value=tokens[t].id)

                if 'refresh' in token_types:
                    r.expire(name=name, time=tokens['refresh'].expires)

        if return_tokens:
            return response, tokens

        return response

    def get_expire_response(
        self,
        token_types: List[str] = ['access', 'refresh'],
        response_type: 'Response' = ORJSONResponse,
        response_headers: Dict[str, Any] = {}
    ) -> 'Response':
        token_types: List[str] = self._token_type_filter(
            token_types=token_types
        )
        response: response_type = response_type()

        if setting.jwt.redis.get('enable', False):
            with RedisContextManager() as r:
                name: str = f'token:{self.token.subject}'
                r.hdel(name, *token_types)

                if 'refresh' in token_types:
                    r.delete(name)

        if self.mode in (self.BOTH_MODE, self.COOKIE_MODE):
            for t in token_types:
                response.delete_cookie(
                    key=getattr(self.setting.httponly_cookie, f'{t}_token_cookie_key'),
                    domain=self.cookie_domain
                )

        return response

    @classmethod
    def create_access_token(
        cls,
        subject: str,
        payload: Dict[str, Any] = {}
    ) -> JWTToken:
        return JWTToken.create(
            subject=subject,
            payload=payload,
            token_type=self.ACCESS_TOKEN
        )

    @classmethod
    def create_refresh_token(
        cls,
        subject: str,
        payload: Dict[str, Any] = {}
    ) -> JWTToken:
        return JWTToken.create(
            subject=subject,
            payload=payload,
            token_type=self.REFRESH_TOKEN
        )

    @property
    def user(self) -> Any:
        if self.token is None:
            return None

        if self._user is not None:
            return self._user

        return self.user_loader(self.token.subject)

    def _get_credential(
        self,
        request: Request,
        authorization: Optional[str] = None
    ) -> Optional[str]:
        credential: Optional[str] = None
        modes: List[str] = [self.mode]

        if modes[0] == self.BOTH_MODE:
            modes = [self.COOKIE_MODE, self.HEADER_MODE]

        for m in modes:
            method: Callable[..., str] = getattr(
                self, f'_get_credential_{m.lower()}'
            )
            args: Tuple[Union[str, Request]] = (authorization,)

            if m == self.COOKIE_MODE:
                args = (request,)

            _credential: Optional[str] = method(*args)

            if _credential is not None:
                credential = _credential

        return credential

    def _get_credential_cookie_mode(
        self,
        request: Request
    ) -> str:
        cookie_key: str = getattr(
            self.setting.httponly_cookie,
            f'{self.token_type}_token_cookie_key'
        )
        credential: Optional[str] = request.cookies.get(
            cookie_key, None
        )

        return credential

    def _get_credential_header_mode(
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
    ) -> Optional[UserModel]:
        user_key_field: 'Column' = getattr(UserModel, setting.user_key_field)

        return db.session.query(UserModel)\
            .filter(user_key_field == subject)\
            .first()

    @staticmethod
    def _token_type_filter(
        token_types: List[str]
    ) -> List[str]:
        return list(filter(
            lambda t: t in ('access', 'refresh'), token_types
        ))
