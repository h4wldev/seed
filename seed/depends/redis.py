import redis

from typing import Any

from seed.setting import setting


class RedisContextManager:  # pragma: no cover
    def __init__(self) -> None:
        self.connection: 'Redis' = redis.Redis(
            host=setting.redis.host,
            port=setting.redis.port,
            db=0,
            encoding=setting.redis.encoding
        )

    def __enter__(self) -> 'Redis':
        return self.connection

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any
    ) -> None:
        self.connection.close()


class Redis:  # pragma: no cover
    def __new__(self):
        return RedisContextManager
