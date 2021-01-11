import arrow

from fastapi import Depends
from typing import Any, Tuple

from seed.api.router import Route
from seed.depends.jwt.depend import JWT
from seed.utils.convert import units2seconds
from setting import setting


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
        now: int = arrow.now(setting.timezone).int_timestamp
        token_types: List[str] = ['access', 'refresh']

        renewal_in: int = units2seconds(
            setting.jwt.refresh_token_renewal_before_expire
        )

        if jwt.token.expires - renewal_in > now:
            token_types = ['access']

        return jwt.get_create_response(
            subject=jwt.token.subject,
            payload=jwt.token.payload,
            token_types=token_types
        )
