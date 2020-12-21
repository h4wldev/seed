import logging

import logger

from dynaconf import Dynaconf
from fastapi import FastAPI, APIRouter
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.routes import router
from db import make_database_uri
from setting import setting


class Application:
    def __init__(
        self,
        name: str = __name__,
        env: str = 'development',
        setting: Dynaconf = setting,
        router: APIRouter = router
    ) -> None:
        self.name = name
        self.env = env
        self.setting = setting
        self.router = router

        self.setting.setenv(self.env)

    def create_app(self) -> FastAPI:
        self.app = FastAPI(title=self.name, debug=self.setting.DEBUG)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.setting.ALLOWED_ORIGINS or ['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        self.app.add_middleware(
            DBSessionMiddleware,
            db_url=make_database_uri(**dict(
                (k.lower(), v) for k, v in setting.database.items(),
            )),
        )

        self.app.include_router(router, prefix=self.setting.API_PREFIX)

        self.logger_configure()

        return self.app

    def logger_configure(self) -> None:
        log_level = logging.DEBUG if self.setting.DEBUG else logging.INFO

        logger.logger_configure(log_level)
        logger.intercept_loggers(self.setting.LOGGING.INTERCEPT_LOGGERS, log_level)


app = Application().create_app()
