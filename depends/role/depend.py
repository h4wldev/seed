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
        roles: List[Union[List[str], str]] = [],
        perms: List[Union[List[str], str]] = [],
        user_loader: Optional[Callable[[str], Any]] = None,
        user_cache: bool = True
    ) -> None:
        self.roles: List[Union[List[str], str]] = roles
        self.perms: List[Union[List[str], str]] = perms

        self.user: Optional[Any] = None
        self.user_loader: Callable[[str], Any] = user_loader
        self.user_cache: bool = user_cache

    def __call__(
        self,
        request: Request,
        response: Response,
        authorization: Optional[str] = Header(None)
    ) -> None:
        jwt: JWT = JWT(
            required=True,
            user_loader=self.user_loader,
            user_cache=self.user_cache
        )(
            request=request,
            response=response,
            authorization=authorization
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
