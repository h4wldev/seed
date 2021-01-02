import arrow
import jwt
import uuid

from fastapi import (
    Header,
    Request,
    Response
)
from fastapi.responses import ORJSONResponse
from typing import Any, Dict, Callable, Optional

from api.router import status
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
        token_type: str = 'access',
        user_loader: Optional[Callable[[str], Any]] = None,
        user_cache: bool = True,
        httponly_cookie_mode: Optional[bool] = None
    ) -> None:
        self.claims: Dict[str, Any] = {}
        self.payload: Dict[str, Any] = {}

        if user_loader is None:
            user_loader = self._default_user_loader

        self.user_loader: Callable[[str], Any] = user_loader
        self.user_cache: bool = user_cache

        self.cached_user: Optional[UserModel] = None

        self.httponly: bool = self.setting.httponly_cookie.enable
        if httponly_cookie_mode is not None:
            self.httponly = httponly_cookie_mode

        self.required: bool = required
        self.token_type: str = token_type
        self.token_loaded: bool = False

    def __call__(
        self,
        request: Request,
        authorization: Optional[str] = Header(None)
    ) -> None:
        credential: Optional[str] = None

        try:
            if self.httponly:
                credential = self.get_credential_from_cookie(request)
            else:
                credential = self.get_credential_from_header(authorization)

            if credential is None:
                raise JWTHTTPException('Credential must not be empty')

            self.load_token(credential)

            if 'type' not in self.claims or self.claims['type'] != self.token_type:
                raise JWTHTTPException(f"Token type must be '{self.token_type}'")
        except JWTHTTPException as e:
            if self.required:
                raise e

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
        credential: str
    ) -> None:
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
        cookie_key: str = cls.setting.httponly_cookie.access_token_cookie_key

        if token_type == 'refresh':
            cookie_key = cls.setting.httponly_cookie.refresh_token_cookie_key

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

    @classmethod
    def get_jwt_token_response(
        cls,
        subject: str,
        payload: Dict[str, Any] = {}
    ) -> ORJSONResponse:
        access_token: str = cls.create_access_token(subject, payload)
        refresh_token: str = cls.create_refresh_token(subject, payload)

        response: ORJSONResponse = ORJSONResponse(
            content={
                'access_token': access_token,
                'refresh_token': refresh_token,
            },
            status_code=status.HTTP_201_CREATED
        )

        if cls.setting.httponly_cookie.enable:
            domain: Optional[str] = ','.join(cls.setting.httponly_cookie.domains)

            if domain == '':
                domain = None

            response.set_cookie(
                key=cls.setting.httponly_cookie.access_token_cookie_key,
                value=access_token,
                domain=domain,
                max_age=units2seconds(cls.setting.access_token_expires),
            )

            response.set_cookie(
                key=cls.setting.httponly_cookie.refresh_token_cookie_key,
                value=refresh_token,
                domain=domain,
                max_age=units2seconds(cls.setting.refresh_token_expires),
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
