import arrow
import datetime
import jwt
import typing
import uuid

from fastapi import (
    Depends,
    Header,
    Request,
    Response,
)

from setting import setting


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
        return self

    @classmethod
    def _create_token(
        cls,
        subject: str,
        token_type: str = 'access',
        expires: typing.Optional[int] = None,
        payload: typing.Dict[str, typing.Any] = {},
        algorithm: str = 'HS256'
    ) -> str:
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
        
        if isinstance(expires, int):
            claims['exp'] = now_timestamp + expires

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
