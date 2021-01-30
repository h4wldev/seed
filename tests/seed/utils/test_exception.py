import pytest

from seed.exceptions import HTTPException
from seed.utils.exception import exception_wrapper


def test_exception_wrapper():
    with pytest.raises(HTTPException) as e:
        @exception_wrapper(
            exc=HTTPException,
            excs=(ZeroDivisionError),
            status_code=500
        )
        def exception_wrapped():
            1 / 0

        exception_wrapped()

    assert e.value.status_code == 500
    assert e.value.detail == 'division by zero'


def test_exception_wrapper_message_handler():
    with pytest.raises(HTTPException) as e:
        @exception_wrapper(
            exc=HTTPException,
            excs=(ZeroDivisionError),
            message_handler=lambda e: str(e).split()
        )
        def exception_wrapped():
            1 / 0

        exception_wrapped()

    assert e.value.detail == ['division', 'by', 'zero']
