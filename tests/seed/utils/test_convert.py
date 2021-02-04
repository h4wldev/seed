from seed.utils.convert import (
    camelcase_to_underscore,
    units_to_seconds
)


def test_camelcase_to_underscore():
    assert camelcase_to_underscore('CamelCase') == 'camel_case'
    assert camelcase_to_underscore('CAMELCase') == 'camel_case'


def test_units_to_seconds():
    assert units_to_seconds(300) == 300
    assert units_to_seconds('300') == 300

    assert units_to_seconds('1s') == 1
    assert units_to_seconds('1m') == 60
    assert units_to_seconds('1h') == 3600
    assert units_to_seconds('1d') == 86400
    assert units_to_seconds('1w') == 604800
    assert units_to_seconds('1M') == 2592000
    assert units_to_seconds('1q') == 10368000
    assert units_to_seconds('1y') == 31536000

    assert units_to_seconds('90m') == 60 * 90
    assert units_to_seconds('1h 90m') == 60 * (60 + 90)
