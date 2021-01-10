import logging

from loguru import logger
from typing import Dict

from .types import LOG_LEVELS


class InterceptHandler(logging.Handler):  # pragma: no cover
    loglevel_mapping: Dict[int, str] = {
        log.level: log.name for log in LOG_LEVELS
    }

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        try:
            level: str = logger.level(record.levelname).name
        except ValueError:
            level: str = self.loglevel_mapping[record.levelno]

        frame: 'Frame' = logging.currentframe()
        depth: int = 2

        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )
