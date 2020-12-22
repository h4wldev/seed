import sys
import logging
import typing

from loguru import logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        try:
            level: str = logger.level(record.levelname).name
        except ValueError:
            level: str = self.loglevel_mapping[record.levelno]

        frame: 'Frame', depth: int = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def logger_configure(log_level: int = logging.DEBUG) -> None:
    logging.getLogger().handlers = [InterceptHandler()]

    logger.configure(handlers=[{'sink': sys.stderr, 'level': log_level}])


def intercept_loggers(
    logger_names: typing.List[str] = [],
    log_level: int = logging.DEBUG,
) -> None:
    for logger_name in logger_names:
        logging_logger = logging.getLogger(logger_name)

        logging_logger.handlers = [InterceptHandler(level=log_level)]
        logging_logger.propagate = False
