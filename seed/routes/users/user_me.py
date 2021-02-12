import orjson

from fastapi import Request, Depends
from fastapi.encoders import jsonable_encoder
from typing import Any, Tuple, Optional, Dict, Set

from seed.depends.auth import Auth
from seed.exceptions import AuthHTTPException
from seed.router import Route, status


class UserMe(Route):
    @Route.option(
        name='Get User Information (me)',
        default_status_code=status.HTTP_200_OK
    )
    @Route.doc_option(
        tags=['users'],
        description='Get User Information',
        responses={
            status.HTTP_200_OK: {
                'description': 'Successfully get user information (me)',
                'content': {
                    'application/json': {
                        'example': {
                            'email': '<string>',
                            'username': '<string>',
                            'profile': {
                                'display_name': '<string>'
                            },
                            'meta': {
                                'email_promotion': False,
                                'email_notification': False,
                                'is_certified': True
                            },
                            'social_accounts': ['<string>']
                        }
                    }
                }
            }
        }
    )
    async def get(
        auth: Auth(required=True) = Depends()
    ) -> Tuple[Any, int]:
        exclude: Set[str] = {'id', 'user_id', 'updated_at'}

        return {
            **auth.user.jsonify(include={'email', 'username'}),
            'profile': auth.user.profile.jsonify(exclude=exclude),
            'meta': auth.user.meta.jsonify(exclude=exclude),
            'social_accounts': list(map(lambda s: s.provider, auth.user.social_accounts))
        }, status.HTTP_200_OK
