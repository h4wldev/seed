from typing import Dict, Any


async def get_trace_dict(request: 'Request') -> Dict[str, Any]:
    keys: Tuple[str] = ('path', 'path_params', 'scheme', 'type', 'http_version')
    result: Dict[str, Any] = dict(map(
        lambda k: (k, dict(request).get(k, None)), keys
    ))

    result['query_string'] = dict(request).get('query_string', b'').decode('utf-8')
    result['client'] = dict(request.client._asdict())
    result['headers'] = dict(request.headers)

    return result
