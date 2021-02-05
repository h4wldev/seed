import pytest

from seed.fields.user_fields import RegisterFields


def test_register_fields_email_validate():
    assert RegisterFields.email_pattern('foobar@test.com')

    with pytest.raises(ValueError) as e:
        RegisterFields.email_pattern('foobar')

        assert str(e) == 'must email pattern'
