from functools import partialmethod
from loguru import logger
from typing import Any, Callable, List

from .types import LogLevel, LOG_LEVELS


class LoggerConfigure:  # pragma: no cover
    @staticmethod
    def add_levels(levels: List[LogLevel] = LOG_LEVELS) -> None:
        for level in levels:
            logger.level(level.name, **level.kwargs)

            if not level.exists:
                method: Callable[..., Any] = partialmethod(logger.__class__.log, level.name)

                setattr(logger.__class__, level.name.lower(), method)
