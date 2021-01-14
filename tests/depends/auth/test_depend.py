from fastapi import Depends, Request, Header

from seed.depends.auth.depend import Auth
from seed.depends.auth.types import JWTToken
from seed.depends.redis import RedisContextManager

from setting import setting


def create_token(type_='access', expires='10s'):
    return JWTToken.create(
        subject='foobar',
        token_type=type_,
        expires=expires
    )


def test_auth_depend(empty_app, get_test_client):
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


def test_auth_depend_with_token_type(empty_app, get_test_client):
    @empty_app.get('/auth_optional')
    def endpoint(auth: Auth(token_type='refresh') = Depends()):
        return auth.token is not None

    access_token = create_token().credential
    refresh_token = create_token('refresh').credential

    client = get_test_client(empty_app)

    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {access_token}',
    })

    assert response.status_code == 400
    assert response.json()['detail'] == "Token type must be 'refresh'"

    response = client.get('/auth_optional', headers={
        'Authorization': f'Bearer {refresh_token}',
    })

    assert response.status_code == 200
    assert response.json()


def test_auth_depend_jwt_notin_redis(empty_app, get_test_client):
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

    assert response.status_code == 400
    assert response.json()['detail'] == 'Signature has expired or not verified'


def test_auth_depend_auth_required(empty_app, get_test_client):
    @empty_app.get('/auth_required')
    def endpoint(auth: Auth(required=True) = Depends()):
        return auth.token is not None

    client = get_test_client(empty_app)
    response = client.get('/auth_required')

    assert response.status_code == 400
    assert response.json()['detail'] == 'JWT credential required'


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

    assert response.status_code == 400
    assert response.json()['detail'] == "Authorization header must like 'Bearer <credentials>'"


def test_auth_depend_get_credential_header_type_error(empty_app, get_test_client):
    @empty_app.get('/get_credential_header_type_error')
    def endpoint(authorization: str = Header(None)) -> str:
        return Auth()._get_credential_header(authorization)

    client = get_test_client(empty_app)
    response = client.get('/get_credential_header_type_error', headers={
        'Authorization': 'ErrorType foobar',
    })

    assert response.status_code == 400
    assert response.json()['detail'] == "Authorization token type must be 'Bearer'"


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


def test_auth_depend_user_loader(empty_app, get_test_client):
    def user_loader(subject):
        return subject

    @empty_app.get('/user_loader')
    def endpoint(auth: Auth(
        required=True,
        user_loader=user_loader
    ) = Depends()):
        return auth.user

    access_token = create_token().credential

    client = get_test_client(empty_app)
    response = client.get('/user_loader', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 200
    assert response.json() == 'foobar'


def test_auth_depend_user_loader_without_token(empty_app, get_test_client):
    def user_loader(subject):
        return subject

    @empty_app.get('/user_loader_without_token')
    def endpoint(auth: Auth(
        user_loader=user_loader
    ) = Depends()):
        return auth.user

    client = get_test_client(empty_app)
    response = client.get('/user_loader_without_token')

    assert response.status_code == 200
    assert response.json() is None
