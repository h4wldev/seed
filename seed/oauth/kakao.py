from typing import Dict, Tuple

from seed.logger import logger
from seed.setting import setting

from seed.exceptions import OAuthHTTPException

from . import OAuthHandler


class KakaoOAuthHandler(OAuthHandler):
    api_key: str = setting.api_key.kakao_api_key

    setting: 'Dynaconf' = setting.oauth.kakao

    def get_tokens(
        self,
        code: str
    ) -> Tuple['access_token', 'refresh_token']:
        data: Dict[str, str] = {
            'grant_type': 'authorization_code',
            'client_id': self.api_key,
            'redirect_uri': self.redirect_uri,
            'code': code,
        }

        status_code, response = self.api_call(
            self.setting.auth_api_url,
            '/oauth/token',
            method='post',
            data=data,
        )
        response: Dict[str, any] = response.json()

        if status_code != 200:
            logger.error(response)

            raise OAuthHTTPException(
                symbol='oauth_get_token_error',
                message='Error has been occurs with OAuth Provider',
                detail={
                    'provider': 'kakao',
                    'message': response.get('error', None),
                    'on': 'get_tokens',
                },
            )

        return response['access_token'], response['refresh_token']

    def get_user_info(
        self,
        access_token: str
    ) -> Tuple['user_id', 'email']:
        headers: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}'
        }

        status_code, response = self.api_call(
            self.setting.api_url,
            '/v2/user/me',
            method='get',
            headers=headers,
        )
        response: Dict[str, any] = response.json()

        if status_code != 200:
            logger.error(response)

            raise OAuthHTTPException(
                symbol='oauth_get_user_info_error',
                message='Error has been occurs with OAuth Provider',
                detail={
                    'provider': 'kakao',
                    'error': response.get('error', None),
                    'on': 'get_user_info',
                },
            )

        email: str = response['kakao_account'].get('email', None)
        user_id: str = str(response['id'])

        return user_id, email

    def get_token_by_refresh_token(
        self,
        refresh_token: str
    ) -> Tuple['access_token', 'refresh_token']:
        data: Dict[str, str] = {
            'grant_type': 'refresh_token',
            'client_id': self.api_key,
            'refresh_token': refresh_token,
        }

        status_code, response = self.api_call(
            self.setting.auth_api_url,
            '/oauth/token',
            method='post',
            data=data,
        )
        response: Dict[str, any] = response.json()

        if status_code != 200:
            logger.error(response)

            raise OAuthHTTPException(
                symbol='oauth_get_token_by_refresh_token_error',
                message='Error has been occurs with OAuth Provider',
                detail={
                    'provider': 'kakao',
                    'error': response.get('error', None),
                    'on': 'get_token_by_refresh_token',
                },
            )

        return response['access_token'], response.get('refresh_token', refresh_token)

    def unlink(
        self,
        access_token: str
    ) -> bool:
        headers: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}',
        }

        status_code, response = self.api_call(
            self.setting.api_url,
            '/v1/user/unlink',
            method='post',
            headers=headers,
        )
        response: Dict[str, any] = response.json()

        if status_code != 200:
            logger.error(response)

            raise OAuthHTTPException(
                symbol='oauth_unlink_error',
                message='Error has been occurs with OAuth Provider',
                detail={
                    'provider': 'kakao',
                    'error': response.get('error', None),
                    'on': 'unlink',
                },
            )

        return True

    @property
    def redirect_uri(self) -> str:
        return f'{setting.base_url.web}{self.setting.redirect_uri}'
