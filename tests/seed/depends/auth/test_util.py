from fastapi import Response

from seed.depends.auth.types import JWTToken
from seed.depends.auth.util import AuthUtil


def test_bind_delete_cookie():
    response = Response()
    AuthUtil.bind_delete_cookie(response, 'access')

    assert response.raw_headers[0][0] == b'set-cookie'
    assert response.raw_headers[0][1].decode().find('="";')


def test_bind_delete_multiple_cookie():
    response = Response()
    AuthUtil.bind_delete_cookie(response, 'access', 'refresh')

    assert len(response.raw_headers) == 2

    assert response.raw_headers[0][0] == b'set-cookie'
    assert response.raw_headers[1][0] == b'set-cookie'


def test_bind_set_cookie():
    token = JWTToken.create(subject='foobar')

    response = Response()
    AuthUtil.bind_set_cookie(response, token)

    assert response.raw_headers[0][0] == b'set-cookie'
    assert response.raw_headers[0][1].decode().find(f'="{token.credential}";')


def test_token_type_filter():
    AuthUtil.token_type_filter(['access', 'refresh']) == {'access', 'refresh'}
    AuthUtil.token_type_filter(['access', 'not_token_type']) == {'access'}
