from typing import Any, Dict, Tuple

from fastapi.requests import Request as FastAPIRequest


class Request(FastAPIRequest):
    @staticmethod
    def from_request(request: FastAPIRequest) -> 'Request':
        return Request(
            scope=request.scope,
            receive=request._receive,
            send=request._send
        )

    @property
    def trace_dict(self) -> Dict[str, Any]:
        keys: Tuple[str] = ('path', 'path_params', 'scheme', 'type', 'http_version')
        result: Dict[str, Any] = dict(map(
            lambda k: (k, dict(self).get(k, None)), keys
        ))

        result['query_string'] = dict(self).get('query_string', b'').decode('utf-8')
        result['client'] = dict(self.client._asdict())
        result['headers'] = dict(self.headers)

        return result
