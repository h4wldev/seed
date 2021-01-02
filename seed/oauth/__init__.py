
class OAuthHandler:
    def __init__(
        self,
        handler_setting: 'Dynaconf'
    ) -> None:
        self.handler_setting: 'Dynaconf' = handler_setting

    def get_access_token(
        self,
        code: str
    ) -> str:
        assert False, 'Not implemented get_access_token method'

    def get_user_id(
        self,
        access_token: str
    ) -> str:
        assert False, 'Not implemented get_user_id method'
