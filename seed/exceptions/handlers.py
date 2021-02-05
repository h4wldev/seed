import orjson

from typing import Dict, Any, Optional

from fastapi import Request as FastAPIRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from seed.logger import logger
from seed.utils.convert import camelcase_to_underscore
from seed.utils.request import get_trace_dict

from .exceptions import HTTPException as SeedHTTPException


async def seed_http_exception_handler(
    request: Optional[FastAPIRequest] = None,
    exc: SeedHTTPException = SeedHTTPException
) -> ORJSONResponse:
    error_data: Dict[str, Any] = dict(exc)
    extra: Dict[str, Any] = {}

    if exc.request:
        extra = {'request': await get_trace_dict(exc.request)}
    elif request:
        extra = {'request': await get_trace_dict(request)}

    logger_data: str = orjson.dumps({
        **error_data,
        **extra
    }).decode('utf-8')

    logger.error(logger_data)

    return ORJSONResponse(
        error_data,
        status_code=exc.status_code
    )


async def fastapi_exception_handler(
    request: FastAPIRequest,
    exc: 'FastAPIHTTPException'
) -> ORJSONResponse:
    exc_type: str = exc.__class__.__name__
    symbol: str = camelcase_to_underscore(exc_type)

    exc: SeedHTTPException = SeedHTTPException(
        symbol=symbol,
        detail=exc.detail,
        headers=exc.headers,
        status_code=exc.status_code,
        request=request
    )
    exc.type_: str = exc_type

    return await seed_http_exception_handler(
        request=request,
        exc=exc,
    )


async def request_validation_exception_handler(
    request: FastAPIRequest,
    exc: 'RequestValidationError'
) -> ORJSONResponse:
    exc_type: str = exc.__class__.__name__
    detail: Dict[str, Any] = jsonable_encoder(exc.errors())

    exc: SeedHTTPException = SeedHTTPException(
        symbol='request_validation_failed',
        detail=detail,
        request=request
    )
    exc.type_: str = exc_type

    return await seed_http_exception_handler(
        request=request,
        exc=exc,
    )


async def pyjwt_exception_handler(
    request: FastAPIRequest,
    exc: 'PyJWTError'
) -> ORJSONResponse:
    message_error_mapper: Dict[str, str] = {
        'Invalid token type': 'token',
        'Not enough segments': 'segments',
        'Invalid header padding': 'header',
        'Invalid header string': 'header_type',
        'Invalid payload padding': 'payload',
        'Invalid crypto padding': 'crypto',
        'The specified alg value is not allowed': 'algorithm',
        'Algorithm not supported': 'algorithm',
        'Signature verification failed': 'signature',
        'Key ID header parameter must be a string': 'header',
    }
    exc_type: str = exc.__class__.__name__

    symbol: str = camelcase_to_underscore(exc_type)
    symbol = symbol.replace('error', 'exception')
    symbol = f'jwt_{symbol}'

    for k, v in message_error_mapper.items():
        if str(exc).startswith(k):
            symbol = f'jwt_invalid_{v}'

    exc: SeedHTTPException = SeedHTTPException(
        symbol=symbol,
        message=str(exc),
        request=request
    )
    exc.type_: str = exc_type

    return await seed_http_exception_handler(
        request=request,
        exc=exc,
    )
