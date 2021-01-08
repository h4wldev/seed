from fastapi import Depends
from typing import Any, Tuple

from api.router import Route
from seed.depends.jwt.depend import JWT


class TokenRefresh(Route):
    @Route.option(
        name='Token Refresh'
    )
    @Route.doc_option(
        tags=['auth'],
        description='Return access token with refresh token',
        responses={
            200: {
                'description': 'Return jwt access tokens',
                'content': {
                    'application/json': {
                        'example': {
                            'access_token': '<jwt_access_token>',
                            'access_token_expires_in': 1800
                        }
                    }
                }
            }
        }
    )
    async def post(
        jwt: JWT(required=True, token_type='refresh') = Depends()
    ) -> Tuple[Any, int]:
        response_token, _ = jwt.get_response(
            subject=jwt.token.claims['sub'],
            payload=jwt.token.payload,
            token_types=['access'],
            return_tokens=True
        )

        return response_token
