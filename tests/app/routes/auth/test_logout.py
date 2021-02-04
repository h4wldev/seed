from seed.depends.auth import JWTToken
from seed.depends.redis import RedisContextManager


def test_logout(client):
    token = JWTToken.create(
        subject='test@foobar.com',
        token_type='access',
        expires=5
    )
    headers = {
        'Authorization': f'Bearer {token.credential}'
    }

    client.post('/api/logout', headers=headers)

    with RedisContextManager() as r:
        assert r.hget(token.redis_name, 'access') is None


def test_logout_redis_expire(client):
    token = JWTToken.create(
        subject='test@foobar.com',
        token_type='access',
        expires=5
    )
    headers = {
        'Authorization': f'Bearer {token.credential}'
    }

    client.post('/api/logout', headers=headers)

    response = client.post('/api/logout', headers=headers)

    assert response.status_code == 401
    assert response.json()['symbol'] == 'auth_token_expired_or_not_verified'
