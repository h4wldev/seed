from fastapi import Depends
from typing import Optional

from logger import logger

from .jwt import JWT
from .uuid import UUID


__version__ = '0.0.1'


class Logger:
    def __new__(
        self,
        uuid: UUID = Depends(),
        jwt: JWT() = Depends()
    ) -> 'Logger':
        user_id: Optional[int] = None

        if jwt.user:
            user_id = jwt.user.id

        return logger.bind(
            uuid=uuid,
            user_id=user_id,
        )
