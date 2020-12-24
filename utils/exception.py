from typing import Any, Callable, Optional, Tuple, Union

from utils.http import HTTPStatusCode


def exception_wrapper(
        exc: 'HTTPException',
        excs: Tuple[Exception] = (),
        status_code: Union[int, HTTPStatusCode] = 400,
        message_handler: Optional[Callable[[Exception], str]] = None,
    ) -> Callable[..., Callable[..., Any]]:
        def decorator(method: Callable[..., Any]) -> Callable[..., Any]:
            def _(*args, **kwargs) -> Any:
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
