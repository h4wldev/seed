from fastapi import Depends
from fastapi.responses import ORJSONResponse
from typing import Any, Tuple

from seed.api.router import Route
from seed.depends.redis import RedisContextManager
from seed.depends.jwt.depend import JWT


class Logout(Route):
    @Route.option(
        name='Logout'
    )
    @Route.doc_option(
        tags=['auth'],
        description='Expire access, refresh token',
        responses={
            200: {
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
        response: ORJSONResponse,
        jwt: JWT(required=True, token_type='access') = Depends()
    ) -> Tuple[Any, int]:
        JWT.bind_delete_cookie(response, 'access', 'refresh')

        with RedisContextManager() as r:
            r.delete(jwt.token.redis_name)

        return response
