from fastapi import (
    Header,
    Request
)
from typing import Callable, List, Optional, Tuple, Union, Set

from seed.db import db
from seed.exceptions import AuthHTTPException
from seed.models import UserModel
from seed.setting import setting

from .types import JWTToken, JWTTokenType
from .util import AuthUtil


class Auth(AuthUtil, JWTTokenType):
    user: Optional[UserModel] = None
    token: Optional[JWTToken] = None

    def __init__(
        self,
        required: bool = False,
        token_type: Optional[str] = None,
        roles: List[Union[List[str], str]] = [],
        abilities: List[Union[List[str], str]] = []
    ) -> None:
        self.required: bool = required
        self.token_type: str = token_type or self.ACCESS_TOKEN

        self.roles: List[Union[List[str], str]] = roles
        self.abilities: List[Union[List[str], str]] = abilities

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
                raise AuthHTTPException(f"Token type must be '{self.token_type}'")

            if not self.token.verify():
                raise AuthHTTPException('Signature has expired or not verified')

            self.user: Optional[UserModel] = self._user_loader(self.token.subject)

            if len(self.roles) or len(self.abilities):
                self._check_permission()
        elif self.required:
            raise AuthHTTPException('JWT credential required')

        return self

    def _check_permission(self) -> None:
        if self.user is None:
            raise AuthHTTPException('User does not exists')

        roles: Set[str] = set()
        abilities: Set[str] = set()

        for role in self.user.roles:
            roles.add(role.role_)

            if len(self.abilities):
                abilities |= role.abilities

        if not self._check_has(roles, self.roles)\
           or not self._check_has(abilities, self.abilities):
            raise AuthHTTPException('Permission Denied')

    def _check_has(
        self,
        has: Set[str],
        check: List[Union[List[str], str]]
    ) -> bool:
        for item in check:
            if isinstance(item, list):
                checked: bool = False

                for i in item:
                    if i in has:
                        checked = True
                        break

                if not checked:
                    return False
            else:
                if item not in has:
                    return False

        return True

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
            raise AuthHTTPException("Authorization header must like 'Bearer <credentials>'")

        type_: str = tokens[0]
        credential: str = tokens[1]

        if type_ != 'Bearer':
            raise AuthHTTPException("Authorization token type must be 'Bearer'")

        return credential

    def _user_loader(
        self,
        subject: str
    ) -> Optional[UserModel]:  # pragma: no cover
        user_key_field: 'Column' = getattr(UserModel, setting.user_key_field)

        return db.session.query(UserModel)\
            .filter(user_key_field == subject)\
            .first()
