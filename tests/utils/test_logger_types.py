from seed.utils.logger.types import LogLevel


def test_log_level_kwargs():
    log_level = LogLevel(
        name='TEST',
        level=20,
        icon='★',
    )

    assert log_level.kwargs == {
        'icon': '★',
        'color': None,
    }


def test_log_level_kwargs_with_exists():
    log_level = LogLevel(
        name='TEST',
        level=20,
        icon='★',
        exists=False,
    )

    assert log_level.kwargs == {
        'icon': '★',
        'color': None,
        'no': 20,
    }
