from seed.exceptions import HTTPException


def test_http_exception_init():
    exception = HTTPException('foobar')

    assert exception.symbol == 'foobar'
    assert exception.status_code == 400
    assert exception.type_ == 'HTTPException'


def test_http_exception_init_with_status_code():
    exception = HTTPException('foobar', status_code=500)

    assert exception.symbol == 'foobar'
    assert exception.status_code == 500


def test_http_exception_str():
    exception = HTTPException('foobar')

    assert str(exception) == "<HTTPException symbol='foobar' status_code=400>"


def test_http_exception_iter():
    exception = HTTPException('foobar')
    dict_ = dict(exception)

    assert list(dict_.keys()) == ['trace_id', 'symbol', 'status_code', 'type']


def test_http_exception_iter_with_headers():
    exception = HTTPException('foobar', headers={'Foo': 'bar'})
    dict_ = dict(exception)

    assert list(dict_.keys()) == ['trace_id', 'symbol', 'headers', 'status_code', 'type']
