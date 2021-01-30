from typing import List

from .types import JWTToken

from seed.setting import setting


class AuthUtil:
    @classmethod
    def bind_delete_cookie(
        cls,
        response: 'Response',
        *token_types: List[str],
    ) -> 'Response':
        for t in cls.token_type_filter(token_types):
            response.delete_cookie(
                key=setting.jwt.cookie.key.get(t, t),
                domain=','.join(setting.jwt.cookie.domains),
            )

        return response

    @staticmethod
    def bind_set_cookie(
        response: 'Response',
        token: JWTToken
    ) -> 'Response':
        response.set_cookie(
            key=setting.jwt.cookie.key.get(token.token_type, token.token_type),
            value=token.credential,
            domain=','.join(setting.jwt.cookie.domains),
            max_age=token.expires_in,
            httponly=setting.jwt.cookie.httponly,
        )

        return response

    @staticmethod
    def token_type_filter(
        token_types: List[str]
    ) -> List[str]:
        return set(filter(
            lambda t: t in ('access', 'refresh'), token_types
        ))
