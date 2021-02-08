import pytest

from seed.schemas.user_schemas import RegisterSchema


def test_register_schema_email_validate():
    assert RegisterSchema.email_pattern('foobar@test.com')

    with pytest.raises(ValueError) as e:
        RegisterSchema.email_pattern('foobar')

        assert str(e) == 'must email pattern'
