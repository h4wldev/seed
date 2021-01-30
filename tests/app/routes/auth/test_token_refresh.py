from seed.depends.auth import JWTToken

from seed.setting import setting


def test_token_refresh(client):
    token = JWTToken.create(
        subject='test@foobar.com',
        token_type='refresh',
        expires=5
    )
    headers = {
        'Authorization': f'Bearer {token.credential}'
    }

    setting.jwt.refresh_token_renewal_before_expire = '1s'

    response = client.post('/api/token/refresh', headers=headers)

    assert response.status_code == 201
    assert 'access_token' in response.json()
    assert 'refresh_token' not in response.json()


def test_token_refresh_refresh_token_renewal(client):
    token = JWTToken.create(
        subject='test@foobar.com',
        token_type='refresh',
        expires=5
    )
    headers = {
        'Authorization': f'Bearer {token.credential}'
    }

    setting.jwt.refresh_token_renewal_before_expire = '1y'

    response = client.post('/api/token/refresh', headers=headers)

    assert response.status_code == 201
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()
