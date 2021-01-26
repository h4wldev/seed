from seed.depends.auth.types import JWTToken
from seed.depends.redis import RedisContextManager


def test_jwt_token_init():
    credential = JWTToken.create(subject='foobar', expires=10).credential
    token = JWTToken(credential)

    assert token.subject == 'foobar'


def test_jwt_token_verify():
    token = JWTToken.create(subject='foobar', expires=10)

    assert token.verify()

    with RedisContextManager() as r:
        r.delete('token:foobar')

    assert not token.verify()


def test_jwt_token_create():
    token = JWTToken.create(subject='foobar', expires=10)

    assert isinstance(token, JWTToken)

    with RedisContextManager() as r:
        assert r.hget('token:foobar', 'access')
