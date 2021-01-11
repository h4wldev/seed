from loguru._logger import Logger

from seed.depends.context_logger import ContextLogger


def test_context_logger_depend_new():
    context_logger = ContextLogger()
    *options, extra = context_logger._options

    assert isinstance(context_logger, Logger)
    assert 'uuid' in extra
