import sys
import logging

from loguru import logger
from logstash_async.handler import AsynchronousLogstashHandler
from typing import List

from seed.utils.logger import LoggerConfigure
from seed.utils.logger.formatter import Formatter
from seed.utils.logger.handlers import InterceptHandler
from seed.setting import setting


def logger_configure(log_level: int = logging.DEBUG) -> None:  # pragma: no cover
    formatter: Formatter = Formatter()

    logger.configure(**{
        'handlers': [
            {'sink': sys.stdout, 'colorize': True, 'format': formatter.stdout_format},
        ],
        'extra': {
            'headers': '',
            'uuid': None,
        },
    })

    LoggerConfigure.add_levels()

    if setting.integrate.logstash.enable:
        logger.add(AsynchronousLogstashHandler(
            setting.integrate.logstash.host,
            setting.integrate.logstash.port,
            setting.integrate.logstash.database_path,
            **setting.integrate.logstash.options,
        ))


def intercept_loggers(
    logger_names: List[str] = None,
    log_level: int = logging.DEBUG,
) -> None:  # pragma: no cover
    if logger_names is None:
        logger_names = []

    for logger_name in logger_names:
        logging_logger = logging.getLogger(logger_name)

        logging_logger.handlers = [InterceptHandler(level=log_level)]
        logging_logger.propagate = False
