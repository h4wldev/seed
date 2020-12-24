import arrow
import jwt
import uuid

from fastapi import (
    Header,
    Request,
    Response
)
from typing import Any, Dict, Callable, Optional

from db import db
from exceptions import JWTHTTPException
from setting import setting
from models.user_model import UserModel
from utils.convert import units2seconds
from utils.exception import exception_wrapper


class JWT:
    setting: 'Dynaconf' = setting.depend.jwt

    def __init__(
        self,
        required: bool = False,
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

        self.required: bool = required
        self.token_type: str = token_type
        self.token_loaded: bool = False

    def __call__(
        self,
        request: Request,
        response: Response,
        authorization: Optional[str] = Header(None)
    ) -> None:
        if authorization is None:
            if self.required:
                raise JWTHTTPException(
                    detail="'Authorization' must not be empty"
                )

            return self

        credential: str = self.get_credential_from_header(authorization)
        self.load_token(credential)

        if 'type' not in self.claims or self.claims['type'] != self.token_type:
            raise JWTHTTPException(
                detail=f"Token type must be '{self.token_type}'"
            )

        return self

    @property
    def user(self) -> Any:
        if not self.token_loaded:
            return None

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
    ) -> Optional[UserModel]:
        user = db.session.query(UserModel)\
            .filter(UserModel.email == subject)\
            .first()

        return user

    @classmethod
    def get_credential_from_header(
        cls,
        authorization: str
    ) -> Dict[str, Any]:
        tokens: List[str] = authorization.split(' ')

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
