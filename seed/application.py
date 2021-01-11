import logging

import logger

from dynaconf import Dynaconf
from fastapi import FastAPI, APIRouter
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from seed.utils.database import make_database_url
from setting import setting

from .api.routes import router


class Application:  # pragma: no cover
    def __init__(
        self,
        name: str = __name__,
        env: str = 'development',
        setting: Dynaconf = setting,
        router: APIRouter = router
    ) -> None:
        self.name: str = name
        self.env: str = env
        self.setting: Dynaconf = setting
        self.router: APIRouter = router

        self.setting.setenv(self.env)

    def create_app(self) -> FastAPI:
        self.app: FastAPI = FastAPI(title=self.name, debug=self.setting.debug)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.setting.cors.allowed_origins,
            allow_credentials=self.setting.cors.allow_credentials,
            allow_methods=self.setting.cors.allow_methods,
            allow_headers=self.setting.cors.allow_headers,
        )

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

        if self.setting.integrate.sentry.enable:
            import sentry_sdk

            from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

            sentry_sdk.init(
                self.setting.integrate.sentry.dsn,
                **self.setting.integrate.sentry.options
            )

            self.app.add_middleware(SentryAsgiMiddleware)

        self.app.include_router(router, prefix=self.setting.api_prefix)

        self.logger_configure()

        return self.app

    def logger_configure(self) -> None:
        log_level: int = logging.DEBUG if self.setting.debug else logging.INFO

        logger.logger_configure(log_level)
        logger.intercept_loggers(self.setting.logging.intercept_loggers, log_level)
