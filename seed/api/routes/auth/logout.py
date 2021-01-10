from fastapi import Depends
from typing import Any, Tuple

from seed.api.router import Route
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
        jwt: JWT(required=True, token_type='access') = Depends()
    ) -> Tuple[Any, int]:
        return jwt.get_expire_response()
