import arrow
import jwt
import uuid

from typing import Any, Dict, Union, Optional

from seed.exceptions import JWTHTTPException
from seed.utils.convert import units2seconds
from seed.utils.exception import exception_wrapper
from setting import setting


class JWTMode:
    BOTH_MODE: str = 'BOTH_MODE'
    COOKIE_MODE: str = 'COOKIE_MODE'
    HEADER_MODE: str = 'HEADER_MODE'


class JWTTokenType:
    ACCESS_TOKEN: str = 'access'
    REFRESH_TOKEN: str = 'refresh'


class JWTToken(JWTTokenType):
    def __init__(
        self,
        credential: str,
        algorithm: str = 'HS256',
        claims: Optional[Dict[str, Any]] = None
    ) -> None:
        self.credential: str = credential

        self.claims: Dict[str, Any] = claims or self.decode(
            credential=credential,
            algorithm=algorithm
        )

        self.id: str = self.claims['jti']
        self.subject: str = self.claims['sub']
        self.payload: Dict[str, Any] = self.claims['payload']
        self.token_type: str = self.claims['type']
        self.expires: Optional[int] = self.claims.get('exp', None)
        self.expires_in: Optional[int] = self.claims.get('exp_in', None)
        self.created_at: int = self.claims['iat']

    @classmethod
    @exception_wrapper(
        JWTHTTPException,
        excs=(jwt.exceptions.PyJWTError),
    )
    def decode(
        cls,
        credential: str,
        algorithm: str = 'HS256'
    ) -> Dict[str, Any]:
        return jwt.decode(
            credential,
            setting.secret_key.jwt_secret_key,
            algorithms=algorithm
        )

    @classmethod
    def create(
        cls,
        subject: str,
        payload: Dict[str, Any] = {},
        token_type: Optional[str] = None,
        expires: Union[int, str] = None,
        algorithm: Optional[str] = None
    ) -> str:
        token_type: str = token_type or self.ACCESS_TOKEN
        algorithm: str = algorithm or setting.jwt.algorithm
        expires: Union[int, str] = expires or getattr(
            setting.jwt, f'{token_type}_token_expires', None
        )

        now: int = arrow.now(setting.timezone).int_timestamp

        claims: Dict[str, Any] = {
            'sub': subject,
            'iat': now,
            'nbf': now,
            'jti': str(uuid.uuid4()),
            'type': token_type,
            'payload': payload,
        }

        if expires is not None:
            if isinstance(expires, str):
                expires = units2seconds(expires)

            claims['exp'] = now + expires
            claims['exp_in'] = expires

        return cls(
            credential=jwt.encode(
                claims,
                setting.secret_key.jwt_secret_key,
                algorithm=algorithm,
                headers={'typ': 'JWT', 'alg': algorithm}
            ),
            algorithm=algorithm,
            claims=claims,
        )
