import orjson
import importlib

from pydantic import BaseModel
from typing import Any, Optional, List, Tuple

from api.router import Route, status
from db import db
from exceptions import HTTPException
from models.user_social_account_model import UserSocialAccountModel
from seed.depends.jwt import JWT
from seed.utils.crypto import AESCipher
from setting import setting


class OAuthCode(BaseModel):
    provider: str
    code: str


class OAuth(Route):
    async def post(
        oauth_code: OAuthCode
    ) -> Tuple[Any, int]:
        if oauth_code.provider not in setting.oauth.providers:
            raise HTTPException(f"'{oauth_code.provider}' is not support provider")

        handler_setting: Optional['Dynaconf'] = setting.oauth.get(
            oauth_code.provider, {}
        )

        handler_path: str = handler_setting.get('handler', 'seed.oauth.OAuthHandler')
        handler: 'OAuthHandler' = OAuth.get_handler_class(handler_path)(handler_setting)

        access_token: str = handler.get_access_token(oauth_code.code)
        user_id: str = handler.get_user_id(access_token)

        user_social_account = db.session.query(UserSocialAccountModel)\
            .filter(UserSocialAccountModel.provider == oauth_code.provider)\
            .filter(UserSocialAccountModel.social_id == user_id)\
            .first()

        if user_social_account is None:
            aes_cipher: AESCipher = AESCipher()

            payload: str = orjson.dumps({
                'provider': 'kakao',
                'user_social_id': user_id
            }).decode('utf-8')

            return {
                'code': aes_cipher.encrypt(payload),
            }, status.HTTP_404_NOT_FOUND

        return JWT.get_jwt_token_response(
            user_social_account.user.key_field, {}
        ), status.HTTP_201_CREATED

    @staticmethod
    def get_handler_class(
        handler_path: str
    ) -> 'OAuthHandler':
        handler_path_tokens: List[str] = handler_path.split('.')
        module_path, class_name = (
            '.'.join(handler_path_tokens[:-1]), handler_path_tokens[-1]
        )

        handler_module: 'module' = importlib.import_module(module_path)
        handler_class: 'OAuthHandler' = getattr(handler_module, class_name)

        return handler_class
