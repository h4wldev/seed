import orjson
import importlib

from fastapi import Request
from fastapi.responses import ORJSONResponse
from typing import Any, Dict, Optional, List, Tuple, Union

from seed.db import db
from seed.setting import setting

from seed.router import Route, status
from seed.exceptions import OAuthHTTPException  
from seed.schemas.auth_schemas import OAuthCodeSchema
from seed.depends.auth import Auth, JWTToken
from seed.models import (
    UserSocialAccountModel,
    UserLoginHistoryModel
)
from seed.utils.crypto import AESCipher



class OAuth(Route):
    @Route.option(
        name='OAuth',
        default_status_code=status.HTTP_201_CREATED
    )
    @Route.doc_option(
        tags=['auth'],
        description='Using OAuth for Authentication',
        responses={
            status.HTTP_201_CREATED: {
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
            status.HTTP_404_NOT_FOUND: {
                'description': 'That social user not exists',
                'content': {
                    'application/json': {
                        'example': {
                            'code': '<aes_string>'
                        }
                    }
                }
            },
            **OAuthHTTPException.doc_object([
                'oauth_not_supported'
            ])
        }
    )
    async def post(
        request: Request,
        oauth_code: OAuthCodeSchema
    ) -> Tuple[Any, int]:
        oauth_handler: 'OAuthHandler' = OAuth.get_oauth_handler(oauth_code.provider)

        if oauth_handler is None:
            raise OAuthHTTPException(
                symbol='oauth_not_supported',
                message=f"'{oauth_code.provider}' is not support provider",
                detail={
                    'provider': oauth_code.provider,
                },
            )

        access_token, refresh_token = oauth_handler.get_tokens(oauth_code.code)
        social_id, email = oauth_handler.get_user_info(access_token)

        user_social_account: UserSocialAccountModel = UserSocialAccountModel\
            .q_social_id_and_provider(
                social_id=social_id,
                provider=oauth_code.provider
            )\
            .first()

        if user_social_account is None:
            return {
                'email': email,
                'code': OAuth.get_code(
                    provider=oauth_code.provider,
                    social_id=social_id,
                )
            }, status.HTTP_404_NOT_FOUND

        user_social_account.access_token = access_token
        user_social_account.refresh_token = refresh_token

        response: ORJSONResponse = OAuth.get_token_response(
            subject=user_social_account.user.key_field,
            payload={},
        )

        login_history: UserLoginHistoryModel = UserLoginHistoryModel.from_request(
            user_id=user_social_account.user_id,
            request=request,
            success=True,
            provider=oauth_code.provider
        )

        db.session.add(login_history)
        db.session.commit()

        return response, status.HTTP_201_CREATED

    @staticmethod
    def get_code(
        provider: str,
        social_id: str
    ) -> str:  # pragma: no cover
        payload: str = orjson.dumps({
            'provider': provider,
            'social_id': social_id,
        }).decode('utf-8')

        return AESCipher().encrypt(payload)

    @staticmethod
    def get_token_response(
        token_types: List[str] = ['access', 'refresh'],
        **kwargs
    ) -> ORJSONResponse:
        tokens: Dict[str, JWTToken] = {}
        content: Dict[str, Union[str, int]] = {}

        for type_ in token_types:
            kwargs['token_type']: str = type_
            kwargs['expires']: str = setting.jwt.get(f'{type_}_token_expires')

            token: JWTToken = JWTToken.create(**kwargs)

            tokens[type_] = token
            content[f'{type_}_token'] = token.credential
            content[f'{type_}_token_expires'] = token.expires_in

        response: ORJSONResponse = ORJSONResponse(content=content)

        for type_ in token_types:
            Auth.bind_set_cookie(
                response=response,
                token=tokens[type_]
            )

        return response

    @staticmethod
    def get_oauth_handler(provider: str) -> Optional['OAuthHandler']:
        handler_setting: Optional['Dynaconf'] = getattr(setting.oauth, provider, None)

        if handler_setting is None:
            return None

        handler_path: str = handler_setting.get('handler', 'seed.oauth.OAuthHandler')
        handler_path_tokens: List[str] = handler_path.split('.')

        module_path, class_name = (
            '.'.join(handler_path_tokens[:-1]), handler_path_tokens[-1]
        )

        handler_module: 'module' = importlib.import_module(module_path)
        handler_class: 'OAuthHandler' = getattr(handler_module, class_name)

        return handler_class(handler_setting)
