import arrow
import jwt
import uuid

from fastapi import (
    Header,
    Request
)
from fastapi.responses import ORJSONResponse
from typing import Any, Dict, Callable, Optional, Union, List, Set

from db import db
from exceptions import JWTHTTPException
from seed.utils.convert import units2seconds
from seed.utils.exception import exception_wrapper
from setting import setting
from models.user_model import UserModel


__version__ = '0.0.1'


class JWT:
    setting: 'Dynaconf' = setting.depend.jwt

    def __init__(
        self,
        required: bool = False,
        mode: str = 'both',
        token_type: str = 'access',
        user_loader: Optional[Callable[[str], Any]] = None,
        user_cache: bool = True
    ) -> None:
        self.claims: Dict[str, Any] = {}
        self.payload: Dict[str, Any] = {}

        if user_loader is None:
            user_loader = self._default_user_loader

        self.user_loader: Callable[[str], Any] = user_loader
        self.user_cache: bool = user_cache

        self.cached_user: Optional[UserModel] = None

        self.mode: str = mode
        if self.mode not in ('both', 'header', 'cookie'):
            self.mode = 'both'

        self.required: bool = required
        self.token_type: str = token_type
        self.token_loaded: bool = False

    def __call__(
        self,
        request: Request,
        authorization: Optional[str] = Header(None)
    ) -> None:
        credential: Optional[str] = None
        methods: List[str] = ['cookie', 'header']

        if self.mode != 'both':
            methods = [self.mode]

        for m in methods:
            method: Callable[..., str] = getattr(self, f'get_credential_from_{m}')
            arg: Union[str, Request] = (authorization,)

            if m == 'cookie':
                arg = (request, self.token_type)

            _credential: Optional[str] = method(*arg)

            if _credential is not None:
                credential = _credential

        if self.required and credential is None:
            raise JWTHTTPException('JWT credential required')

        self.load_token(credential)

        if self.token_loaded and self.claims.get('type', None) != self.token_type:
            raise JWTHTTPException(f"Token type must be '{self.token_type}'")

        return self

    @property
    def user(self) -> Any:
        if not self.token_loaded:
            return None

        if 'sub' not in self.claims:
            raise JWTHTTPException("'sub' must be in token claims")

        if self.user_cache and self.cached_user is not None:
            return self.cached_user

        return self.user_loader(self.claims['sub'])

    def load_token(
        self,
        credential: Optional[str] = None
    ) -> None:
        if credential is None:
            return

        self.token_loaded = True

        self.claims = self.decode_token(credential)
        self.payload = self.claims.get('payload', {})

    def _default_user_loader(
        self,
        subject: str
    ) -> Optional[UserModel]:
        user = db.session.query(UserModel)\
            .filter(getattr(UserModel, setting.user_key_field) == subject)\
            .first()

        return user

    @classmethod
    def get_credential_from_cookie(
        cls,
        request: Request,
        token_type: str = 'access'
    ) -> str:
        cookie_key: str = getattr(
            cls.setting.httponly_cookie,
            f'{token_type}_token_cookie_key'
        )
        credential: Optional[str] = request.cookies.get(
            cookie_key, None
        )

        return credential

    @classmethod
    def get_credential_from_header(
        cls,
        authorization: Optional[str]
    ) -> str:
        if authorization is None:
            return authorization

        tokens: List[str] = str(authorization).split(' ')

        if len(tokens) != 2:
            raise JWTHTTPException("Authorization header must like 'Bearer <credentials>'")

        type_: str = tokens[0]
        credential: str = tokens[1]

        if type_ != 'Bearer':
            raise JWTHTTPException("Authorization token type must be 'Bearer'")

        return credential

    @classmethod
    @exception_wrapper(
        JWTHTTPException,
        excs=(jwt.exceptions.PyJWTError),
    )
    def decode_token(
        cls,
        token: str,
        algorithm: str = 'HS256'
    ) -> Dict[str, Any]:
        return jwt.decode(
            token,
            setting.secret_key.jwt_secret_key,
            algorithms=algorithm
        )

    @classmethod
    def create_access_token(
        cls,
        subject: str,
        payload: Dict[str, Any] = {}
    ) -> str:
        return cls._create_token(
            subject=subject,
            payload=payload,
            expires=cls.setting.access_token_expires
        )

    @classmethod
    def create_refresh_token(
        cls,
        subject: str,
        payload: Dict[str, Any] = {}
    ) -> str:
        return cls._create_token(
            subject=subject,
            payload=payload,
            token_type='refresh',
            expires=cls.setting.refresh_token_expires
        )

    def get_jwt_token_response(
        self,
        subject: str,
        payload: Dict[str, Any] = {},
        token_types: List[str] = ['access', 'refresh']
    ) -> ORJSONResponse:
        token_response: Dict[str, Any] = {}
        token_types: Set[str] = set(filter(
            lambda t: t in ('access', 'refresh'), token_types
        ))

        if len(token_types) < 0:
            token_types = {'access'}

        for t in token_types:
            token_response[f'{t}_token'] = getattr(
                self, f'create_{t}_token',
            )(subject, payload)

            token_response[f'{t}_token_expires_in'] = units2seconds(
                getattr(self.setting, f'{t}_token_expires'),
            )

        response: ORJSONResponse = ORJSONResponse(
            content=token_response,
        )

        if self.mode in ('both', 'cookie'):
            domain: Optional[str] = ','.join(self.setting.httponly_cookie.domains)

            for t in token_types:
                response.set_cookie(
                    key=getattr(self.setting.httponly_cookie, f'{t}_token_cookie_key'),
                    value=token_response.get(f'{t}_token'),
                    domain=domain,
                    max_age=token_response.get(f'{t}_token_expires_in'),
                )

        return response

    @classmethod
    @exception_wrapper(
        JWTHTTPException,
        excs=(jwt.exceptions.PyJWTError),
    )
    def _create_token(
        cls,
        subject: str,
        token_type: str = 'access',
        expires: Optional[int] = None,
        payload: Dict[str, Any] = {},
        algorithm: Optional[str] = None
    ) -> str:
        if algorithm is None:
            algorithm = cls.setting.algorithm

        now_timestamp: int = arrow.now(setting.timezone).int_timestamp

        headers: Dict[str, Any] = {
            'typ': 'JWT',
            'alg': algorithm
        }

        claims: Dict[str, Any] = {
            'sub': subject,
            'iat': now_timestamp,
            'nbf': now_timestamp,
            'jti': str(uuid.uuid4()),
            'type': token_type
        }

        if expires:
            claims['exp'] = now_timestamp + units2seconds(expires)

        return jwt.encode(
            {**claims, **{'payload': payload}},
            setting.secret_key.jwt_secret_key,
            algorithm=algorithm,
            headers=headers
        )
