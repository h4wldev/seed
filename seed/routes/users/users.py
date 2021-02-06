import orjson

from fastapi import Request, Depends
from typing import Any, Tuple, Optional, Dict

from seed.db import db
from seed.exceptions import UserHTTPException
from seed.fields.user_fields import RegisterFields, SocialInfoFields
from seed.router import Route, status
from seed.models import (
    UserModel,
    UserMetaModel,
    UserProfileModel,
    UserRoleModel,
    UserSocialAccountModel,
)
from seed.utils.crypto import AESCipher


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
    async def post(
        request: Request,
        body: RegisterFields
    ) -> Tuple[Any, int]:
        try:
            social_info: SocialInfoFields = SocialInfoFields(
                **orjson.loads(AESCipher().decrypt(body.code))
            )
        except Exception:
            raise UserHTTPException(
                symbol='invalid_register_code',
                detail={'body': dict(body)}
            )

        if UserSocialAccountModel.q_social_id_and_provider(
            **social_info.dict()
        ).exists():
            raise UserHTTPException(symbol='social_user_already_exists')

        if UserModel.q_email_or_username(
            email=body.email,
            username=body.username,
        ).exists():
            raise UserHTTPException(symbol='already_exist_email_or_username')

        user: UserModel = UserModel.create(
            register_fields=body,
            social_info_fields=social_info
        )

        db.session.commit()

        return '', status.HTTP_201_CREATED
