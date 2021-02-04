from fastapi.exceptions import HTTPException as FastAPIHTTPExcetion
from jwt.exceptions import PyJWTError

from seed.exceptions import HTTPException as SeedHTTPException


def test_seed_http_exception_handler(empty_app, get_test_client):
    @empty_app.get('/seed-http-exception')
    def endpoint():
        raise SeedHTTPException(symbol='foobar')

    client = get_test_client(empty_app)
    response = client.get('/seed-http-exception')

    assert response.status_code == 400
    assert list(response.json().keys()) == ['trace_id', 'symbol', 'status_code', 'type']


def test_request_validation_exception_handler(empty_app, get_test_client):
    @empty_app.get('/request-validation-exception')
    def endpoint(q: str):
        pass

    client = get_test_client(empty_app)
    response = client.get('/request-validation-exception')

    assert response.status_code == 400
    assert list(response.json().keys()) == ['trace_id', 'symbol', 'detail', 'status_code', 'type']
    assert response.json()['symbol'] == 'request_validation_failed'


def test_seed_fastapi_exception_handler(empty_app, get_test_client):
    @empty_app.get('/fastapi-exception')
    def endpoint():
        raise FastAPIHTTPExcetion(detail='foobar', status_code=400)

    client = get_test_client(empty_app)
    response = client.get('/fastapi-exception')

    assert response.status_code == 400
    assert list(response.json().keys()) == ['trace_id', 'symbol', 'detail', 'status_code', 'type']
    assert response.json()['symbol'] == 'http_exception'


def test_seed_pyjwt_exception_handler(empty_app, get_test_client):
    @empty_app.get('/pyjwt-exception')
    def endpoint():
        raise PyJWTError('foobar')

    client = get_test_client(empty_app)
    response = client.get('/pyjwt-exception')

    assert response.status_code == 400
    assert list(response.json().keys()) == ['trace_id', 'symbol', 'message', 'status_code', 'type']
    assert response.json()['symbol'] == 'jwt_py_jwt_exception'


def test_seed_pyjwt_exception_handler_with_mapper(empty_app, get_test_client):
    @empty_app.get('/pyjwt-exception-with-mapper')
    def endpoint():
        raise PyJWTError('Signature verification failed')

    client = get_test_client(empty_app)
    response = client.get('/pyjwt-exception-with-mapper')

    assert response.status_code == 400
    assert list(response.json().keys()) == ['trace_id', 'symbol', 'message', 'status_code', 'type']
    assert response.json()['symbol'] == 'jwt_invalid_signature'
