import logging

from loguru import logger
from logstash_async.handler import AsynchronousLogstashHandler
from typing import List

from setting import setting


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

        frame: 'Frame' = logging.currentframe()
        depth: int = 2

        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def logger_configure(log_level: int = logging.DEBUG) -> None:
    logger.configure(**{
        'extra': {
            'uuid': None,
            'user_id': None,
        },
    })

    if setting.integrate.logstash.enable:
        logger.add(AsynchronousLogstashHandler(
            setting.integrate.logstash.host,
            setting.integrate.logstash.port,
            setting.integrate.logstash.database_path,
            **setting.integrate.logstash.options,
        ))


def intercept_loggers(
    logger_names: List[str] = [],
    log_level: int = logging.DEBUG,
) -> None:
    for logger_name in logger_names:
        logging_logger = logging.getLogger(logger_name)

        logging_logger.handlers = [InterceptHandler(level=log_level)]
        logging_logger.propagate = False
