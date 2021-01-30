from fastapi import Depends

from seed.logger import logger

from .uuid import UUID


__version__ = '0.0.1'


class ContextLogger:
    def __new__(
        self,
        uuid: UUID = Depends()
    ) -> 'Logger':
        return logger.bind(
            uuid=str(uuid)
        )
