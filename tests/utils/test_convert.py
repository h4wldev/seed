from seed.utils.convert import (
    int2bitfield,
    bitfield2int,
    units2seconds
)


def test_int2bitfield():
    assert int2bitfield(0) == [False]
    assert int2bitfield(1) == [True]
    assert int2bitfield(30) == [False, True, True, True, True]
    assert (
        int2bitfield(999) == [True, True, True, False, False, True, True, True, True, True]
    )


def test_bitfield2int():
    assert bitfield2int([False]) == 0
    assert bitfield2int([True]) == 1
    assert bitfield2int([False, True, True, True, True]) == 30
    assert (
        bitfield2int([True, True, True, False, False, True, True, True, True, True]) == 999
    )


def test_units2seconds():
    assert units2seconds(300) == 300
    assert units2seconds('300') == 300

    assert units2seconds('1s') == 1
    assert units2seconds('1m') == 60
    assert units2seconds('1h') == 3600
    assert units2seconds('1d') == 86400
    assert units2seconds('1w') == 604800
    assert units2seconds('1M') == 2592000
    assert units2seconds('1q') == 10368000
    assert units2seconds('1y') == 31536000

    assert units2seconds('90m') == 60 * 90
    assert units2seconds('1h 90m') == 60 * (60 + 90)
