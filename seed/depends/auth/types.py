import arrow
import jwt
import uuid
import orjson

from typing import Any, Dict, Union, Optional

from seed.depends.redis import RedisContextManager
from seed.exceptions import JWTHTTPException
from seed.utils.convert import units2seconds
from seed.utils.crypto import AESCipher
from seed.utils.exception import exception_wrapper

from setting import setting


class JWTTokenType:
    ACCESS_TOKEN: str = 'access'
    REFRESH_TOKEN: str = 'refresh'


class JWTToken(JWTTokenType):
    aes_cipher: AESCipher = AESCipher()

    def __init__(
        self,
        credential: str,
        algorithm: str = 'HS256',
        claims: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.credential: str = credential

        self.claims: Dict[str, Any] = claims or self.decode(
            credential=credential,
            algorithm=algorithm
        )

        self.id: str = self.claims['jti']
        self.subject: str = self.claims['sub']
        self.payload: Dict[str, Any] = self.claims['payload']
        self.secrets: Dict[str, Any] = self.aes_cipher.decrypt(
            self.claims['secrets']
        )
        self.token_type: str = self.claims['type']
        self.expires_in: int = self.claims['exp_in']
        self.expires: 'Arrow' = arrow.get(self.claims['exp'])
        self.created_at: 'Arrow' = arrow.get(self.claims['iat'])

    def verify(self) -> bool:
        with RedisContextManager() as r:
            stored_uuid: str = r.hget(
                name=f'token:{self.subject}',
                key=self.token_type,
            )

            return stored_uuid is not None and \
                self.id == stored_uuid.decode()

    @classmethod
    def create(
        cls,
        subject: str,
        payload: Dict[str, Any] = {},
        secrets: Dict[str, Any] = {},
        token_type: Optional[str] = 'access',
        expires: Union[int, str] = None,
        algorithm: Optional[str] = 'HS256'
    ) -> str:
        token_type: str = token_type or JWTTokenType.ACCESS_TOKEN
        algorithm: str = algorithm or setting.jwt.algorithm
        expires: Union[int, str] = expires or (
            setting.jwt.get(f'{token_type}_token_expires', None)
        )
        uuid_: str = str(uuid.uuid4())

        now: int = arrow.now(setting.timezone).int_timestamp

        claims: Dict[str, Any] = {
            'sub': subject,
            'iat': now,
            'nbf': now,
            'jti': uuid_,
            'type': token_type,
            'payload': payload,
            'secrets': cls.aes_cipher.encrypt(
                orjson.dumps(secrets).decode('utf-8')
            ),
        }

        if expires is not None:
            if isinstance(expires, str):
                expires = units2seconds(expires)

            claims['exp'] = now + expires
            claims['exp_in'] = expires

        with RedisContextManager() as r:
            r.hset(
                name=f'token:{subject}',
                key=token_type,
                value=uuid_,
            )

            if token_type == JWTTokenType.REFRESH_TOKEN:  # pragma: no cover
                r.expire(
                    name=f'token:{subject}',
                    time=claims['exp_in'],
                )

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

    @staticmethod
    @exception_wrapper(
        JWTHTTPException,
        excs=(jwt.exceptions.PyJWTError),
    )
    def decode(
        credential: str,
        algorithm: str = 'HS256'
    ) -> Dict[str, Any]:
        return jwt.decode(
            credential,
            setting.secret_key.jwt_secret_key,
            algorithms=algorithm
        )
