import pytest

from seed.depends.role.types import Flag


def test_flag_init():
    flag = Flag(value=2, mapping=['flag1', 'flag2'])

    assert flag.mapping == {'flag1': 0, 'flag2': 1}
    assert flag.bitfield == [False, True]


def test_flag_get():
    flag = Flag(value=2, mapping=['flag1', 'flag2'])

    assert not flag.get('flag1')
    assert flag.get('flag2')
    assert not flag.get('not_exist_name')


def test_flag_has():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    assert not flag.has('flag1', 'flag2')  # flag1 and flag2
    assert flag.has('flag1', ['flag2', 'flag3'])  # flag1 and (flag2 or flag3)

    flag.set('flag3', False)
    assert not flag.has('flag1', ['flag2', 'flag3'])  # flag1 and (flag2 or flag3)


def test_flag_get_all():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    assert flag.get_all() == {
        'flag1': True,
        'flag2': False,
        'flag3': True,
    }


def test_flag_reset():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])
    flag.reset()

    assert flag.bitfield == [False, False, False]


def test_flag_set():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    assert flag.get('flag1')

    flag.set('flag1', False)

    assert not flag.get('flag1')


def test_flag_set_not_exist_key():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    with pytest.raises(KeyError):
        flag.set('not_exist_key', False)


def test_flag_value_property():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    assert flag.value == 5


def test_flag_value_setter():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])
    flag.value = 0

    assert flag.bitfield == [False, False, False]


def test_flag_from_bitfield():
    flag = Flag.from_bitfield(
        value=[False, False],
        mapping=['flag1', 'flag2'],
    )

    assert flag.mapping == {'flag1': 0, 'flag2': 1}
    assert flag.bitfield == [False, False]


def test_flag_set_bitfield():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])
    flag._set_bitfield(0)

    assert flag.bitfield == [False, False, False]


def test_flag_repr():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])

    assert str(flag) == '<Flag flags=[flag1,flag3]>'


def test_flag_eq():
    flag = Flag(value=5, mapping=['flag1', 'flag2', 'flag3'])
    flag2 = Flag(value=3, mapping=['flag1', 'flag2', 'flag3'])

    assert flag != flag2
    assert flag == 5
    assert flag != 'string'

    flag2.value = 5

    assert flag == flag2
