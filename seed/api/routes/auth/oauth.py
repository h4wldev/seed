import datetime
import orjson
import importlib

from fastapi import Request
from pydantic import BaseModel
from typing import Any, Optional, List, Tuple

from seed.api.router import Route, status
from db import db
from seed.exceptions import HTTPException
from seed.models.user_login_history_model import UserLoginHistoryModel
from seed.models.user_social_account_model import UserSocialAccountModel
from seed.depends.jwt.depend import JWT
from seed.utils.crypto import AESCipher
from setting import setting


class OAuthCode(BaseModel):
    provider: str
    code: str


class OAuth(Route):
    @Route.option(
        name='OAuth',
        default_status_code=201
    )
    @Route.doc_option(
        tags=['auth'],
        description='Using OAuth for Authentication',
        responses={
            201: {
                'description': 'Return jwt access, refresh tokens',
                'content': {
                    'application/json': {
                        'example': {
                            'access_token': '<jwt_access_token>',
                            'access_token_expires_in': 1800,
                            'refresh_token': '<jwt_refresh_token>',
                            'refresh_token_expires_in': 86400
                        }
                    }
                }
            },
            404: {
                'description': 'That social user not exists',
                'content': {
                    'application/json': {
                        'example': {
                            'code': '<aes_string>'
                        }
                    }
                }
            }
        }
    )
    async def post(
        request: Request,
        oauth_code: OAuthCode
    ) -> Tuple[Any, int]:
        if oauth_code.provider not in setting.oauth.providers:
            raise HTTPException(f"'{oauth_code.provider}' is not support provider")

        oauth_handler = OAuth.get_handler(oauth_code.provider)

        access_token, refresh_token = oauth_handler.get_tokens(oauth_code.code)
        user_id: str = oauth_handler.get_user_id(access_token)

        user_social_account = db.session.query(UserSocialAccountModel)\
            .filter(UserSocialAccountModel.provider == oauth_code.provider)\
            .filter(UserSocialAccountModel.social_id == user_id)\
            .first()

        print(type(db))

        return None
        # if user_social_account is None:
        #     aes_cipher: AESCipher = AESCipher()

        #     return {
        #         'code': aes_cipher.encrypt(orjson.dumps({
        #             'provider': 'kakao',
        #             'user_social_id': user_id
        #         }).decode('utf-8')),
        #     }, status.HTTP_404_NOT_FOUND

        # user_social_account.access_token = access_token
        # user_social_account.refresh_token = refresh_token

        # login_history = UserLoginHistoryModel.from_request(
        #     user_id=user_social_account.user_id,
        #     request=request,
        #     success=True,
        #     provider=oauth_code.provider
        # )

        # db.session.add(login_history)
        # db.session.commit()

        # return JWT(mode=setting.jwt.mode).get_create_response(
        #     subject=user_social_account.user.key_field,
        #     payload={}
        # ), status.HTTP_201_CREATED

    @staticmethod
    def get_handler(
        provider: str
    ) -> 'OAuthHandler':
        handler_setting: Optional['Dynaconf'] = setting.oauth.get(provider)

        handler_path: str = handler_setting.get('handler', 'seed.oauth.OAuthHandler')
        handler_path_tokens: List[str] = handler_path.split('.')

        module_path, class_name = (
            '.'.join(handler_path_tokens[:-1]), handler_path_tokens[-1]
        )

        handler_module: 'module' = importlib.import_module(module_path)
        handler_class: 'OAuthHandler' = getattr(handler_module, class_name)

        return handler_class(handler_setting)
