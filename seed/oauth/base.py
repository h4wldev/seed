import requests

from typing import Any, Callable, Dict, Optional, Tuple


class OAuthHandler:
    setting: Optional['Dynaconf'] = None

    def __init__(
        self,
        setting: Optional['Dynaconf'] = None
    ) -> None:
        if setting is not None:
            self.setting: 'Dynaconf' = setting

    def api_call(
        self,
        api_url: str,
        path: str,
        method: str = 'get',
        data: dict = {},
        params: dict = {},
        headers: dict = {},
        json: bool = False
    ) -> Tuple[int, Any]:
        uri: str = f'{api_url}{path}'
        method: Callable[..., Any] = getattr(requests, method, requests.get)

        kwargs: Dict[str, Any] = {
            'headers': headers,
            'params': params
        }
        kwargs['json' if json else 'data'] = data

        response: 'Response' = method(uri, **kwargs)

        return response.status_code, response

    def get_tokens(
        self,
        code: str
    ) -> Tuple['access_token', 'refresh_token']:
        assert False, 'Not implemented get_access_token method'

    def get_user_info(
        self,
        access_token: str
    ) -> Tuple['user_id', 'email']:
        assert False, 'Not implemented get_user_info method'

    def get_token_by_refresh_token(
        self,
        refresh_token: str
    ) -> Tuple['access_token', 'refresh_token']:
        assert False, 'Not implemented get_token_by_refresh_token method'

    def unlink(
        self,
        access_token: str
    ) -> bool:
        assert False, 'Not implemented unlink method'
