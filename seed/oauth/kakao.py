from . import OAuthHandler


class KakaoOAuthHandler(OAuthHandler):
    def get_access_token(
        self,
        code: str
    ) -> str:
        return '1'

    def get_user_id(
        self,
        access_token: str
    ) -> str:
        return '1'
