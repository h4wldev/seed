from fastapi import Depends
from typing import Any, Tuple

from seed.router import Route
from seed.depends.auth import Auth


class User(Route):
    @Route.option(
        name='Get User'
    )
    @Route.doc_option(
        tags=['users'],
        description='Get user Information',
        responses={
            200: {
                'description': 'Get User Information',
                'content': {
                    'application/json': {
                        'example': None
                    }
                }
            }
        }
    )
    async def get(
        auth: Auth(required=True) = Depends(),
    ) -> Tuple[Any, int]:
        print(auth)
        
        return 'foo', 200
