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

from exceptions import JWTHTTPException
from setting import setting
from utils.convert import units2seconds
from utils.exception import exception_wrapper
from utils.http import HTTPStatusCode




class JWT:
    setting: 'Dynaconf' = setting.plugin.jwt

    def __init__(
        self,
        required: bool = False
    ) -> None:
        self.required: bool = required

    def __call__(
        self,
        request: Request,
        response: Response,
        authorization: typing.Optional[str] = Header(None)
    ) -> None:
        if authorization:
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

            payloads: typing.Dict[str, typing.Any] = self.decode_token(credential)

        return self

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
