import typing

from utils.http import HTTPStatusCode


def exception_wrapper(
        exc: 'HTTPException',
        excs: typing.Tuple[Exception] = (),
        status_code: typing.Union[int, HTTPStatusCode] = 400,
        message_handler: typing.Optional[typing.Callable[[Exception], str]] = None
    ) -> typing.Callable[..., typing.Callable[..., typing.Any]]:
        def decorator(
            method: typing.Callable[..., typing.Any]
        ) -> typing.Callable[..., typing.Any]:
            def _(*args, **kwargs) -> typing.Any:
                try:
                    return method(*args, **kwargs)
                except excs as e:
                    message: str = str(e)

                    if message_handler:
                        message = message_handler(e)

                    raise exc(
                        status_code=status_code,
                        detail=message
                    )
            
            return _

        return decorator
