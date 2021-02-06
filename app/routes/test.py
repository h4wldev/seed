from fastapi import Depends, Request
from typing import Any, Tuple

from seed.router import Route
from seed.depends.auth import Auth
from seed.models import UserModel


class Test(Route):
    async def get() -> Tuple[Any, int]:
        1 / 0

        return 'foo', 200
