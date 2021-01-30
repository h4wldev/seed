from fastapi import Depends
from typing import Any, Tuple

from seed.router import Route
from seed.depends.auth import Auth


class Users(Route):
    @Route.option(
        name='Register'
    )
    @Route.doc_option(
        tags=['users'],
        description='Register with OAuth Code',
        responses={
            201: {
                'description': 'Successfully create user',
                'content': {
                    'application/json': {
                        'example': None
                    }
                }
            }
        }
    )
    async def post() -> Tuple[Any, int]:
        return 'foo', 200
