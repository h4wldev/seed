import redis

from typing import Any

from setting import setting


class RedisContextManager:
    setting: 'Dynaconf' = setting.redis

    def __init__(self) -> None:
        self.connection: 'Redis' = redis.Redis(
            host=self.setting.host,
            port=self.setting.port,
            db=0
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


class Redis:
    def __new__(self):
        return RedisContextManager
