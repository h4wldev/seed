import pytest

from seed.depends.role.column_types import MutableRole, Role as RoleType
from seed.depends.role.types import Flag as FlagType


@pytest.fixture
def flag():
    return FlagType(value=2, mapping=['flag1', 'flag2'])


@pytest.fixture
def mutable_role(flag):
    return MutableRole(value=flag)


def test_mutable_role_init(mutable_role):
    assert mutable_role.bitfield == [False, True]


def test_mutable_role_coerce(flag):
    mutable_role = MutableRole.coerce(key='', value=flag)

    assert isinstance(mutable_role, MutableRole)


def test_role_type_process_bind_param(flag):
    value = RoleType.process_bind_param(value=flag, dialect='')
    value2 = RoleType.process_bind_param(value=2, dialect='')

    assert value == 2
    assert value2 == 2


def test_role_type_process_result_value(flag):
    value = RoleType.process_result_value(value=2, dialect='')
    value2 = RoleType.process_result_value(value=flag, dialect='')

    assert isinstance(value, RoleType.type_)
    assert isinstance(value2, FlagType)
