import logging

import seed.logger as logger

from dynaconf import Dynaconf
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import (
    HTTPException as FastAPIHTTPException,
    RequestValidationError
)
from fastapi_sqlalchemy import DBSessionMiddleware
from jwt.exceptions import PyJWTError
from starlette.middleware.cors import CORSMiddleware

from seed.exceptions import HTTPException as SeedHTTPException
from seed.exceptions.handlers import (
    fastapi_exception_handler,
    seed_http_exception_handler,
    pyjwt_exception_handler,
    request_validation_exception_handler
)
from seed.utils.database import make_database_url
from seed.setting import setting


class Application:  # pragma: no cover
    def __init__(
        self,
        router: APIRouter,
        name: str = __name__,
        env: str = 'development',
    ) -> None:
        self.name: str = name
        self.env: str = env
        self.router: APIRouter = router

        setting.setenv(self.env)

    def create_app(self) -> FastAPI:
        self.app: FastAPI = FastAPI(
            title=self.name,
            debug=setting.debug,
            exception_handlers={
                FastAPIHTTPException: fastapi_exception_handler,
                SeedHTTPException: seed_http_exception_handler,
                RequestValidationError: request_validation_exception_handler,
                PyJWTError: pyjwt_exception_handler,
            },
        )

        self.app.include_router(self.router, prefix=setting.api_prefix)

        self.bind_database_middleware()
        self.bind_middleware()

        self.bind_integrates()

        self.logger_configure()

        return self.app

    def bind_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=setting.cors.allowed_origins,
            allow_credentials=setting.cors.allow_credentials,
            allow_methods=setting.cors.allow_methods,
            allow_headers=setting.cors.allow_headers,
        )

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
        log_level: int = logging.DEBUG if setting.debug else logging.INFO

        logger.logger_configure(log_level)
        logger.intercept_loggers(setting.logging.intercept_loggers, log_level)
