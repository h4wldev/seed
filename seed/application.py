import os
import sys
import logging

import seed.logger as logger

from fastapi import FastAPI, APIRouter, status
from fastapi.exceptions import (
    HTTPException as FastAPIHTTPException,
    RequestValidationError
)
from fastapi_sqlalchemy import DBSessionMiddleware
from typing import List, Union, Dict
from jwt.exceptions import PyJWTError
from starlette.middleware.cors import CORSMiddleware

from .exceptions import HTTPException as SeedHTTPException
from .exceptions.handlers import (
    fastapi_exception_handler,
    seed_http_exception_handler,
    pyjwt_exception_handler,
    request_validation_exception_handler
)
from .exceptions.schemas import RequestValidationExceptionSchema
from .middlewares.server_error import ServerErrorMiddleware
from .utils.database import make_database_url
from .setting import setting
from .routes import router as seed_router


class Application:  # pragma: no cover
    def __init__(
        self,
        router: APIRouter,
        name: str = __name__,
        env: str = 'development',
        setting_files: List[str] = [
            'settings/*.toml',
            'settings/secrets/.secrets.*.toml'
        ]
    ) -> None:
        self.name: str = name
        self.env: str = env
        self.router: APIRouter = router
        self.setting_files: List[str] = setting_files

    def create_app(self) -> FastAPI:
        self.load_setting_files()

        self.app: FastAPI = FastAPI(
            title=self.name,
            debug=setting.debug,
            responses={
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    'description': '__[RequestValidationException]__\n\nRequest validation failed',
                    'content': {
                        'application/json': {
                            'example': {
                                'trace_id': '<error_trace_id>',
                                'symbol': 'request_validation_failed',
                                'status_code': status.HTTP_422_UNPROCESSABLE_ENTITY,
                                'type': 'RequestValidationError',
                                'detail': [
                                    {'loc': ['<string>'], 'msg': '<message>', 'type': '<type>'}
                                ]
                            }
                        }
                    },
                    'model': RequestValidationExceptionSchema
                }
            },
        )

        self.app.include_router(seed_router, prefix=setting.api_prefix)
        self.app.include_router(self.router, prefix=setting.api_prefix)

        self.bind_database_middleware()
        self.bind_middleware()
        self.bind_integrates()
        self.bind_exception_handlers()

        self.logger_configure()

        return self.app

    def load_setting_files(self) -> None:
        setting_files: List[str] = list(map(
            lambda p: os.path.join(os.getcwd(), p),
            self.setting_files
        ))

        setting.setenv(self.env)
        setting.load_file(path=setting_files)

    def bind_exception_handlers(self) -> None:
        self.app.add_exception_handler(FastAPIHTTPException, fastapi_exception_handler)
        self.app.add_exception_handler(SeedHTTPException, seed_http_exception_handler)
        self.app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
        self.app.add_exception_handler(PyJWTError, pyjwt_exception_handler)

    def bind_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=setting.cors.allowed_origins,
            allow_credentials=setting.cors.allow_credentials,
            allow_methods=setting.cors.allow_methods,
            allow_headers=setting.cors.allow_headers,
        )

        self.app.add_middleware(ServerErrorMiddleware)

    def bind_database_middleware(self) -> None:
        database_setting: Dict[str, str] = {
            **setting.database,
            **{'password': setting.password.database_password}
        }

        self.app.add_middleware(
            DBSessionMiddleware,
            db_url=make_database_url(**{
                k.lower(): v for k, v in database_setting.items()
            }),
            commit_on_exit=setting.sqlalchemy.commit_on_exit,
            session_args=setting.sqlalchemy.session_args,
            engine_args=setting.sqlalchemy.engine_args
        )

    def bind_integrates(self) -> None:
        if setting.integrate.sentry.enable:
            import sentry_sdk

            from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

            sentry_sdk.init(
                setting.integrate.sentry.dsn,
                **setting.integrate.sentry.options
            )

            self.app.add_middleware(SentryAsgiMiddleware)

    def logger_configure(self) -> None:
        log_level: Union[int, str] = setting.logging.get('level', 'INFO')

        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)

        log_level: int = logging.DEBUG if setting.debug else log_level

        logger.logger_configure(log_level)
        logger.intercept_loggers(setting.logging.intercept_loggers, log_level)
