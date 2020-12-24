import arrow
import datetime
import jwt
import typing
import uuid

from fastapi import (
    Depends,
    Header,
    Request,
    Response
)

from db import db
from exceptions import JWTHTTPException
from setting import setting
from models.user_model import UserModel
from utils.convert import units2seconds
from utils.exception import exception_wrapper
from utils.http import HTTPStatusCode


class JWT:
    setting: 'Dynaconf' = setting.plugin.jwt

    def __init__(
        self,
        required: bool = False,
        user_loader: typing.Optional[
            typing.Callable[[str], typing.Any]
        ] = None,
        user_cache: bool = True
    ) -> None:
        self.claims: typing.Dict[str, typing.Any] = {}
        self.payload: typing.Dict[str, typing.Any] = {}

        if user_loader is None:
            user_loader = self._default_user_loader

        self.user_loader: typing.Callable[[str], typing.Any] = user_loader
        self.user_cache: bool = user_cache

        self.cached_user: typing.Optional[UserModel] = None

        self.required: bool = required
        self.token_loaded: bool = False

    def __call__(
        self,
        request: Request,
        response: Response,
        authorization: typing.Optional[str] = Header(None)
    ) -> None:
        if authorization:
            credential: str = self.get_credential_from_header(authorization)
            
            self.load_token(credential)

        return self

    @property
    def user(self) -> UserModel:
        if not self.token_loaded:
            raise JWTHTTPException(
                detail='Token claims not loaded'
            )

        if 'sub' not in self.claims:
            raise JWTHTTPException(
                detail="'sub' must be in token claims"
            )

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
    ) -> typing.Optional[UserModel]:
        user = db.session.query(UserModel)\
            .filter(UserModel.email == subject)\
            .first()

        return user


    @classmethod
    def get_credential_from_header(
        cls,
        authorization: str
    ) -> typing.Dict[str, typing.Any]:
        tokens: typing.List[str] = authorization.split(' ')

        if len(tokens) != 2:
            raise JWTHTTPException(
                detail="Authorization header must like 'Bearer <credentials>'"
            )

        type_: str = tokens[0]
        credential: str = tokens[1]

        if type_ != 'Bearer':
            raise JWTHTTPException(
                detail="Authorization token type must be 'Bearer'",
            )

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
    ) -> typing.Dict[str, typing.Any]:
        return jwt.decode(
            token,
            setting.secret_key.jwt_secret_key,
            algorithms=algorithm
        )

    @classmethod
    def create_access_token(
        cls,
        subject: str,
        payload: typing.Dict[str, typing.Any] = {}
    ) -> str:
        return cls._create_token(
            subject=subject,
            payload=payload,
            expires=cls.setting.access_token_expires
        )

    @classmethod
    def create_refresh_token(
        cls,
        subject: str
    ) -> str:
        return cls._create_token(
            subject=subject,
            token_type='refresh',
            expires=cls.setting.refresh_token_expires
        )

    @classmethod
    @exception_wrapper(
        JWTHTTPException,
        excs=(jwt.exceptions.PyJWTError),
    )
    def _create_token(
        cls,
        subject: str,
        token_type: str = 'access',
        expires: typing.Optional[int] = None,
        payload: typing.Dict[str, typing.Any] = {},
        algorithm: typing.Optional[str] = None
    ) -> str:
        if algorithm is None:
            algorithm = cls.setting.algorithm

        now_timestamp: int = arrow.now(setting.timezone).int_timestamp

        headers: typing.Dict[str, typing.Any] = {
            'typ': 'JWT',
            'alg': algorithm
        }

        claims: typing.Dict[str, typing.Any] = {
            'sub': subject,
            'iat': now_timestamp,
            'nbf': now_timestamp,
            'jti': str(uuid.uuid4()),
            'type': token_type
        }

        if token_type == 'refresh':
            payload = {}

        if expires:
            claims['exp'] = now_timestamp + units2seconds(expires)

        return jwt.encode(
            {**claims, **{'payload': payload}},
            setting.secret_key.jwt_secret_key,
            algorithm=algorithm,
            headers=headers
        )
