import logging

import seed.logger as logger

from dynaconf import Dynaconf
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from jwt.exceptions import PyJWTError
from starlette.middleware.cors import CORSMiddleware

from seed.exceptions import HTTPException as SeedHTTPException
from seed.exceptions.handlers import (
    fastapi_exception_handler,
    seed_http_exception_handler,
    pyjwt_exception_handler
)
from seed.utils.database import make_database_url
from seed.setting import setting


class Application:  # pragma: no cover
    def __init__(
        self,
        router: APIRouter,
        name: str = __name__,
        env: str = 'development',
        setting: Dynaconf = setting,
    ) -> None:
        self.name: str = name
        self.env: str = env
        self.setting: Dynaconf = setting
        self.router: APIRouter = router

        self.setting.setenv(self.env)

    def create_app(self) -> FastAPI:
        self.app: FastAPI = FastAPI(
            title=self.name,
            debug=self.setting.debug,
            exception_handlers={
                FastAPIHTTPException: fastapi_exception_handler,
                SeedHTTPException: seed_http_exception_handler,
                PyJWTError: pyjwt_exception_handler,
            },
        )

        self.app.include_router(self.router, prefix=self.setting.api_prefix)

        self.bind_database_middleware()
        self.bind_middleware()

        self.bind_integrates()

        self.logger_configure()

        return self.app

    def bind_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.setting.cors.allowed_origins,
            allow_credentials=self.setting.cors.allow_credentials,
            allow_methods=self.setting.cors.allow_methods,
            allow_headers=self.setting.cors.allow_headers,
        )

    def bind_database_middleware(self) -> None:
        database_setting: Dict[str, str] = {
            **self.setting.database,
            **{'password': self.setting.password.database_password}
        }

        self.app.add_middleware(
            DBSessionMiddleware,
            db_url=make_database_url(**{
                k.lower(): v for k, v in database_setting.items()
            }),
            commit_on_exit=self.setting.sqlalchemy.commit_on_exit,
            session_args=self.setting.sqlalchemy.session_args,
            engine_args=self.setting.sqlalchemy.engine_args
        )

    def bind_integrates(self) -> None:
        if self.setting.integrate.sentry.enable:
            import sentry_sdk

            from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

            sentry_sdk.init(
                self.setting.integrate.sentry.dsn,
                **self.setting.integrate.sentry.options
            )

            self.app.add_middleware(SentryAsgiMiddleware)

    def logger_configure(self) -> None:
        log_level: int = logging.DEBUG if self.setting.debug else logging.INFO

        logger.logger_configure(log_level)
        logger.intercept_loggers(self.setting.logging.intercept_loggers, log_level)
