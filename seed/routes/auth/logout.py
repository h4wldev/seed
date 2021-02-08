from fastapi import Depends
from fastapi.responses import ORJSONResponse
from typing import Any, Tuple

from seed.router import Route, status
from seed.depends.auth import Auth
from seed.depends.redis import Redis


class Logout(Route):
    @Route.option(
        name='Logout'
    )
    @Route.doc_option(
        tags=['auth'],
        description='Expire access, refresh token',
        responses={
            status.HTTP_200_OK: {
                'description': 'Expire access, refresh token',
                'content': {
                    'application/json': {
                        'example': None
                    }
                }
            }
        }
    )
    async def post(
        auth: Auth(required=True) = Depends(),
        redis: Redis() = Depends()
    ) -> Tuple[Any, int]:
        response: ORJSONResponse = ORJSONResponse()

        auth.bind_delete_cookie(
            response,
            'access', 'refresh'
        )

        with redis as r:
            r.delete(auth.token.redis_name)

        return response
