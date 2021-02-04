import re

from typing import Dict, Any

from fastapi import Request as FastAPIRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from seed.logger import logger
from seed.request import Request as SeedRequest

from .exceptions import HTTPException as SeedHTTPException


async def seed_http_exception_handler(
    request: FastAPIRequest,
    exc: SeedHTTPException
) -> ORJSONResponse:
    exc.request = SeedRequest.from_request(request)
    error_data: Dict[str, Any] = dict(exc)

    logger.error({
        **error_data,
        **{
            'request': exc.request.trace_dict,
        },
    })

    return ORJSONResponse(
        error_data,
        status_code=exc.status_code
    )


async def fastapi_exception_handler(
    request: FastAPIRequest,
    exc: 'FastAPIHTTPException'
) -> ORJSONResponse:
    pattern: 'Pattern' = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    exc_type: str = exc.__class__.__name__
    symbol: str = pattern.sub(r'_\1', exc_type).lower()

    exc: SeedHTTPException = SeedHTTPException(
        symbol=symbol,
        detail=detail,
        headers=exc.headers,
        status_code=exc.status_code,
        request=request
    )
    exc.type_: str = exc.__class__.__name__

    return seed_http_exception_handler(exc)
