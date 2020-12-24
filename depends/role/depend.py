from fastapi import (
    Header,
    Request,
    Response
)
from typing import Any, Callable, List, Optional

from depends.jwt import JWT
from exceptions import RoleHTTPException


class Role:
    def __init__(
        self,
        roles: List[str] = [],
        perms: List[str] = [],
        user_loader: Optional[Callable[[str], Any]] = None
    ) -> None:
        self.roles: List[str] = roles
        self.perms: List[str] = perms

        self.user: Optional[Any] = None
        self.user_loader: Callable[[str], Any] = user_loader

    def __call__(
        self,
        request: Request,
        response: Response,
        authorization: Optional[str] = Header(None)
    ) -> None:
        jwt: JWT = JWT(required=True)(
            request=request,
            response=response,
            authorization=authorization,
        )

        self.user = jwt.user

        if self.user is None:
            raise RoleHTTPException(
                detail='User data not loaded'
            )

        if not self.user.permission.has(*self.perms)\
           or not self.user.role.has(*self.roles):
            raise RoleHTTPException(
                detail='Permission Denied'
            )
