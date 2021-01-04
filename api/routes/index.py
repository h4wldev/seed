import uuid
from geolite2 import geolite2

from fastapi import Request, Depends, Response
from fastapi.responses import ORJSONResponse
from api.router import Route, Router

from db import db
from logger import logger as default_logger
from exceptions import HTTPException

from seed.depends.context_logger import ContextLogger
from seed.depends.jwt import JWT
from seed.utils.geoip import GeoIP

from models.user_login_history_model import UserLoginHistoryModel


router = Router()


# @router.Route('/')
class Index(Route):
    @Route.doc_option(tags=['index'])
    async def get(request: Request, jwt: JWT() = Depends()) -> str:
        user_login_history = UserLoginHistoryModel.from_request(
            user_id=1,
            request=request,
            success=True,
            provider='Kakao',
        )

        print(user_login_history)

        return {}, 203

    @Route.doc_option(summary='post당')
    def post() -> str:
        return 'test'
