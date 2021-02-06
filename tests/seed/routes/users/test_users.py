from seed.models import (
    UserModel,
    UserMetaModel,
    UserProfileModel,
    UserSocialAccountModel,
    UserRoleModel
)


register_code = 'utoDjhIEBooTAY0XwCyOrmt/KgIiRBUpJREMRQq9tXTEacmxkbbQb/41b+wI5IFZ7ySDCVBfrGv/3lf71FN8yg=='


def test_register(client):
    data = {
        'email': 'foobar@foodaz.com',
        'code': register_code,
        'username': 'foobar',
        'display_name': 'foobar'
    }

    response = client.post('/api/users/', json=data)
    new_user = UserModel.q().filter(UserModel.email == 'foobar@foodaz.com').first()

    assert response.status_code == 201

    assert new_user is not None
    assert UserProfileModel.q().filter(UserProfileModel.user_id == new_user.id).count() > 0
    assert UserMetaModel.q().filter(UserMetaModel.user_id == new_user.id).count() > 0
    assert UserSocialAccountModel.q().filter(UserSocialAccountModel.user_id == new_user.id).count() > 0
    assert UserRoleModel.q().filter(UserRoleModel.user_id == new_user.id).count() > 0


def test_register_invalid_register_code(client):
    data = {
        'email': 'foobar@foodaz.com',
        'code': 'invalid_code_invalid_code_invalid_code',
        'username': 'foobar',
        'display_name': 'foobar'
    }

    response = client.post('/api/users/', json=data)

    assert response.status_code == 400
    assert response.json()['symbol'] == 'invalid_register_code'


def test_register_social_user_already_exists(client):
    data = {
        'email': 'foobar@foodaz.com',
        'code': '58wvprm0nn6kgXEeJdosIImQyoXffQsh5Yg8PEU+xf1d4m+h7JRk36zTWBn3VZ93jXKYZCAAMUEZupKbUUfZMg==',
        'username': 'foobar',
        'display_name': 'foobar'
    }

    response = client.post('/api/users/', json=data)

    assert response.status_code == 400
    assert response.json()['symbol'] == 'social_user_already_exists'


def test_register_already_exist_email_or_username(client):
    data = {
        'email': 'test@foobar.com',
        'code': register_code,
        'username': 'foobar',
        'display_name': 'foobar'
    }

    response = client.post('/api/users/', json=data)

    assert response.status_code == 400
    assert response.json()['symbol'] == 'already_exist_email_or_username'
