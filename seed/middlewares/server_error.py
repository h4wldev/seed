import sys

from typing import Callable, Dict, Any

from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send

from seed.logger import logger
from seed.exceptions import HTTPException as SeedHTTPException
from seed.exceptions.handlers import seed_http_exception_handler
from seed.router import status
from seed.setting import setting


class ServerErrorMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        handler: Callable = None,
        debug: bool = False
    ) -> None:
        self.app: ASGIApp = app
        self.handler: Callable = handler
        self.debug: bool = debug

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send
    ) -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            request: Request = Request(scope)
            response: 'ORJSONResponse' = await self._catch_server_error(request, e)

            await response(scope, receive, send)

    async def _catch_server_error(
        self,
        request: Request,
        e: Exception
    ) -> ORJSONResponse:
        exc: SeedHTTPException = SeedHTTPException(
            symbol='server_error_occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        exc_info: Dict[str, str] = {
            'exception': e.__class__.__name__,
            'message': str(e),
        }

        if setting.integrate.sentry.enable:  # pragma: no cover
            import sentry_sdk

            with sentry_sdk.push_scope() as scope:
                scope.set_extra('trace_id', str(exc.trace_id))
                exc_info['event_id']: str = sentry_sdk.capture_exception(e)

        if setting.debug:  # pragma: no cover
            exc_type, exc_value, tb = sys.exc_info()

            while tb.tb_next is not None:
                tb = tb.tb_next

            exc.detail: Dict[str, Any] = {
                **exc_info,
                **{
                    'traceback': {
                        'filename': tb.tb_frame.f_code.co_filename,
                        'name': tb.tb_frame.f_code.co_name,
                        'lineno': tb.tb_lineno,
                    },
                },
            }

            logger.opt(exception=(None, exc_value, tb)).debug({
                **exc_info,
                **{'trace_id': str(exc.trace_id)},
            })

        return await seed_http_exception_handler(request=request, exc=exc)
