import datetime

from fastapi import Depends, Request, Header

from seed.depends.auth.depend import Auth
from seed.depends.redis import RedisContextManager
from seed.models import (
    RoleModel,
    AbilityModel,
    RoleAbilityModel,
    UserRoleModel,
    UserBanModel
)

from seed.setting import setting


def test_auth_depend(empty_app, get_test_client, create_token):
    @empty_app.get('/auth_optional')
    def endpoint(auth: Auth() = Depends()):
        return auth.token is not None

    client = get_test_client(empty_app)
    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {create_token().credential}',
    })

    assert response.status_code == 200
    assert response.json()


def test_auth_depend_optional_without_credential(empty_app, get_test_client):
    @empty_app.get('/auth_optional')
    def endpoint(auth: Auth() = Depends()):
        return auth.token is not None

    client = get_test_client(empty_app)
    response = client.get('/auth_optional')

    assert response.status_code == 200
    assert not response.json()


def test_auth_depend_with_token_type(empty_app, get_test_client, create_token):
    @empty_app.get('/auth_optional')
    def endpoint(auth: Auth(token_type='refresh') = Depends()):
        return auth.token is not None

    access_token = create_token().credential
    refresh_token = create_token(type_='refresh').credential

    client = get_test_client(empty_app)

    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {access_token}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_token_type_not_correct'

    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {refresh_token}',
    })

    assert response.status_code == 200
    assert response.json()


def test_auth_depend_jwt_notin_redis(empty_app, get_test_client, create_token):
    @empty_app.get('/auth_optional')
    def endpoint(auth: Auth() = Depends()):
        return auth.token is not None

    token = create_token()
    credential = token.credential

    with RedisContextManager() as r:
        r.delete('token:foobar')

    client = get_test_client(empty_app)
    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {credential}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_token_expired_or_not_verified'


def test_auth_depend_auth_required(empty_app, get_test_client):
    @empty_app.get('/auth_required')
    def endpoint(auth: Auth(required=True) = Depends()):
        return auth.token is not None

    client = get_test_client(empty_app)
    response = client.get('/auth_required')

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_token_required'


def test_auth_depend_get_credential(empty_app, get_test_client):
    @empty_app.get('/get_credential')
    def endpoint(
        request: Request,
        authorization: str = Header(None)
    ) -> str:
        return Auth()._get_credential(request, authorization)

    client = get_test_client(empty_app)

    cookies = {setting.jwt.cookie.key.access: 'from_cookie'}
    headers = {'Authorization': 'Bearer from_header'}

    from_cookie_response = client.get('/get_credential', cookies=cookies)
    assert from_cookie_response.json() == 'from_cookie'

    from_header_response = client.get('/get_credential', headers=headers)
    assert from_header_response.json() == 'from_header'

    from_both_response = client.get('/get_credential', cookies=cookies, headers=headers)
    assert from_both_response.json() == 'from_header'


def test_auth_depend_get_credential_header(empty_app, get_test_client):
    @empty_app.get('/get_credential_header')
    def endpoint(authorization: str = Header(None)) -> str:
        return Auth()._get_credential_header(authorization)

    client = get_test_client(empty_app)
    response = client.get('/get_credential_header', headers={
        'Authorization': 'Bearer foobar',
    })

    assert response.status_code == 200
    assert response.json() == 'foobar'


def test_auth_depend_get_credential_header_struct_error(empty_app, get_test_client):
    @empty_app.get('/get_credential_header_struct_error')
    def endpoint(authorization: str = Header(None)) -> str:
        return Auth()._get_credential_header(authorization)

    client = get_test_client(empty_app)
    response = client.get('/get_credential_header_struct_error', headers={
        'Authorization': 'foobar',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_header_structure_not_correct'


def test_auth_depend_get_credential_header_type_error(empty_app, get_test_client):
    @empty_app.get('/get_credential_header_type_error')
    def endpoint(authorization: str = Header(None)) -> str:
        return Auth()._get_credential_header(authorization)

    client = get_test_client(empty_app)
    response = client.get('/get_credential_header_type_error', headers={
        'Authorization': 'ErrorType foobar',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_header_type_not_correct'


def test_auth_depend_get_credential_cookie(empty_app, get_test_client):
    @empty_app.get('/get_credential_cookie')
    def endpoint(request: Request) -> str:
        return Auth()._get_credential_cookie(request)

    client = get_test_client(empty_app)
    response = client.get('/get_credential_cookie', cookies={
        setting.jwt.cookie.key.access: 'foobar',
    })

    assert response.status_code == 200
    assert response.json() == 'foobar'


def test_auth_role_check(session, empty_app, get_test_client, create_token):
    @empty_app.get('/role_check')
    def endpoint(
        auth: Auth(
            required=True,
            roles=['user', ('admin', 'super-admin')]
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    session.bulk_save_objects([
        RoleModel(role='user'),
        RoleModel(role='admin'),
        UserRoleModel(user_id=1, role_='user'),
        UserRoleModel(user_id=1, role_='admin')
    ])

    response = client.get('/role_check', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 200
    assert response.json()


def test_auth_ability_check(session, empty_app, get_test_client, create_token):
    @empty_app.get('/ability_check')
    def endpoint(
        auth: Auth(
            required=True,
            abilities=['auth', ('read', 'write')]
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    session.bulk_save_objects([
        RoleModel(role='user'),
        AbilityModel(ability='auth'),
        AbilityModel(ability='read'),
        RoleAbilityModel(role_='user', ability_='auth'),
        RoleAbilityModel(role_='user', ability_='read'),
        UserRoleModel(user_id=1, role_='user')
    ])

    response = client.get('/ability_check', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 200
    assert response.json()


def test_auth_check_permission_user_not_exist(empty_app, get_test_client, create_token):
    @empty_app.get('/user_not_exist')
    def endpoint(
        auth: Auth(
            required=True,
            abilities=['auth']
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='not_exist_user')
    client = get_test_client(empty_app)

    response = client.get('/user_not_exist', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_user_not_exists'


def test_auth_check_permission_permission_denied(empty_app, get_test_client, create_token):
    @empty_app.get('/permission_denied')
    def endpoint(
        auth: Auth(
            required=True,
            roles=['user']
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    response = client.get('/permission_denied', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_permmision_denied'


def test_auth_check_permission_banned_role(session, empty_app, get_test_client, create_token):
    @empty_app.get('/banned-role')
    def endpoint(
        auth: Auth(
            required=True,
            roles=['user']
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    session.bulk_save_objects([
        RoleModel(role='user'),
        AbilityModel(ability='auth'),
        RoleAbilityModel(role_='user', ability_='auth'),
        UserRoleModel(user_id=1, role_='user'),
        UserBanModel(user_id=1, role_='user', reason='foobar')
    ])

    response = client.get('/banned-role', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_banned_user'


def test_auth_check_permission_banned_ability(session, empty_app, get_test_client, create_token):
    @empty_app.get('/banned-ability')
    def endpoint(
        auth: Auth(
            required=True,
            abilities=['auth']
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    session.bulk_save_objects([
        RoleModel(role='user'),
        AbilityModel(ability='auth'),
        RoleAbilityModel(role_='user', ability_='auth'),
        UserRoleModel(user_id=1, role_='user'),
        UserBanModel(user_id=1, ability_='auth', reason='foobar')
    ])

    response = client.get('/banned-ability', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_banned_user'


def test_auth_check_permission_banned_not_continue(session, empty_app, get_test_client, create_token):
    @empty_app.get('/banned-not-continue')
    def endpoint(
        auth: Auth(
            required=True,
            roles=['user']
        ) = Depends()
    ) -> str:
        return True

    token = create_token(subject='test@foobar.com')
    client = get_test_client(empty_app)

    session.bulk_save_objects([
        RoleModel(role='user'),
        AbilityModel(ability='auth'),
        RoleAbilityModel(role_='user', ability_='auth'),
        UserRoleModel(user_id=1, role_='user'),
        UserBanModel(user_id=1, role_='user', until_at=datetime.datetime(1999, 3, 6))
    ])

    response = client.get('/banned-not-continue', headers={
        'Authorization': f'Bearer {token.credential}',
    })

    assert response.status_code == 200
    assert response.json()


def test_check_has():
    assert Auth()._check_has({'has1', 'has2'}, ['has1', ('has2', 'has3')])
    assert not Auth()._check_has({'has1', 'has2'}, ['has1', ('has3', 'has4')])
    assert not Auth()._check_has({'has1', 'has2'}, ['has1', 'has3'])
    assert not Auth()._check_has(set(), ['has1', 'has3'])
