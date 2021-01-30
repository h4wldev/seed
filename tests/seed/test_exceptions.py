from seed.exceptions import HTTPException


def test_http_exception_init():
    exception = HTTPException('foobar')

    assert exception.detail == 'foobar'
    assert exception.status_code == 400


def test_http_exception_init_with_status_code():
    exception = HTTPException('foobar', status_code=500)

    assert exception.detail == 'foobar'
    assert exception.status_code == 500
