import uuid

from fastapi import Request


__version__ = '0.0.1'


class UUID:
    def __new__(
        self,
        request: Request
    ) -> str:
        accept_language: str = request.headers.get('accept-language', '')
        user_agent: str = request.headers.get('user-agent', '')
        user_ip: str = request.client.host

        payload: str = f'{user_ip}${accept_language}${user_agent}'
        payload = ''.join(filter(str.isalnum, payload))

        return uuid.uuid3(uuid.NAMESPACE_URL, payload)
