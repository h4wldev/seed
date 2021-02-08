import arrow

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from typing import Any, Tuple, List

from seed.setting import setting

from seed.router import Route, status
from seed.depends.auth import Auth
from seed.depends.redis import Redis
from seed.utils.convert import units_to_seconds

from .oauth import OAuth


class TokenRefresh(Route):
    @Route.option(
        name='Token Refresh',
        default_status_code=status.HTTP_201_CREATED
    )
    @Route.doc_option(
        tags=['auth'],
        description='Return access / refresh token with refresh token',
        responses={
            status.HTTP_201_CREATED: {
                'description': 'Return jwt access / refresh tokens (refresh_token_renewal_before_expire)',
                'content': {
                    'application/json': {
                        'example': {
                            'access_token': '<jwt_access_token>',
                            'access_token_expires_in': 1800,
                            'refresh_token': '<jwt_refresh_token>',
                            'refresh_token_expires_in': 99999
                        }
                    }
                }
            }
        }
    )
    async def post(
        auth: Auth(required=True, token_type='refresh') = Depends(),
        redis: Redis() = Depends()
    ) -> Tuple[Any, int]:
        now: int = arrow.now(setting.timezone).int_timestamp
        token_types: List[str] = ['access', 'refresh']
        renewal_in: int = units_to_seconds(
            setting.jwt.refresh_token_renewal_before_expire
        )

        if auth.token.expires.int_timestamp - renewal_in > now:
            token_types = ['access']

        response: ORJSONResponse = OAuth.get_token_response(
            token_types=token_types,
            subject=auth.token.subject,
            payload=auth.token.payload,
            secrets=auth.token.secrets,
        )

        return response, status.HTTP_201_CREATED
