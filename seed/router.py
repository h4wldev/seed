import sys

from fastapi import APIRouter, status, Request as FastAPIRequest
from fastapi.responses import Response, ORJSONResponse
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from seed.logger import logger
from seed.setting import setting
from seed.exceptions import HTTPException as SeedHTTPException
from seed.exceptions.handlers import seed_http_exception_handler

from .request import Request as SeedRequest


class Route:
    _available_methods: List[str] = [
        'get', 'head', 'post', 'put', 'delete', 'options', 'trace', 'patch'
    ]
    _endpoint_options: Dict[str, Any] = {}

    @classmethod
    def doc_option(
        cls,
        enable: bool = True,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = 'Successful Response',
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _(method):
            method.doc_options: Dict[str, Any] = {
                'include_in_schema': enable,
                'tags': tags,
                'summary': summary,
                'description': description,
                'response_description': response_description,
                'responses': responses,
                'deprecated': deprecated,
            }
            return method
        return _

    @classmethod
    def option(
        cls,
        name: Optional[str] = None,
        default_status_code: int = 200,
        dependencies: Optional[List['Depends']] = None,
        operation_id: Optional[str] = None,
        response_class: Response = ORJSONResponse,
        route_class_override: Optional['APIRoute'] = None,
        callbacks: Optional[List['BaseRoute']] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _(method):
            method.endpoint_options: Dict[str, Any] = {
                'dependencies': dependencies,
                'status_code': default_status_code,
                'operation_id': operation_id,
                'response_class': response_class,
                'name': name,
                'route_class_override': route_class_override,
                'callbacks': callbacks,
            }
            return method
        return _

    @classmethod
    def response_model(
        cls,
        response_model: Any,
        response_model_include: Optional[Union['SetIntStr', 'DictIntStrAny']] = None,
        response_model_exclude: Optional[Union['SetIntStr', 'DictIntStrAny']] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def _(method):
            method.response_model: Dict[str, Any] = {
                'response_model': response_model,
                'response_model_include': response_model_include,
                'response_model_exclude': response_model_exclude,
                'response_model_by_alias': response_model_by_alias,
                'response_model_exclude_unset': response_model_exclude_unset,
                'response_model_exclude_defaults': response_model_exclude_defaults,
                'response_model_exclude_none': response_model_exclude_none,
            }
            return method
        return _

    @classmethod
    def _get_endpoints(cls) -> Dict[str, Callable[..., Any]]:
        endpoints: Dict[str, Callable[..., Any]] = {}

        for k in cls._available_methods:
            method: Callable[..., Any] = getattr(cls, k, None)

            if method and callable(method):
                endpoints[k] = method

        return endpoints


class Router(APIRouter):
    def __init__(
        self,
        *args,
        endpoint_options: Optional[Dict[str, Any]] = {},
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.endpoint_options: Dict[str, Any] = endpoint_options

    def Route(
        self,
        path: str,
        endpoint_options: Optional[Dict[str, Any]] = {}
    ) -> Callable[..., Any]:
        assert path.startswith('/'), "Path must start with '/'"

        def _(cls: Route) -> Route:
            assert isinstance(cls, Route.__class__), 'Route must be inherit route class'

            endpoints: Dict[str, Callable[..., Any]] = cls._get_endpoints()

            for method, endpoint in endpoints.items():
                kwargs: Dict[str, Any] = {
                    **self.endpoint_options,
                    **cls._endpoint_options,
                    **endpoint_options,
                    **getattr(endpoint, 'endpoint_options', {}),
                    **getattr(endpoint, 'doc_options', {}),
                    **getattr(endpoint, 'response_model', {})
                }

                kwargs['methods'] = [method.upper()]

                endpoint.options: Dict[str, Any] = kwargs
                endpoint: Callable[..., 'Response'] = self._endpoint_wrapper(endpoint)

                self.add_api_route(*(path, endpoint), **endpoint.options)

        return _

    def _endpoint_wrapper(
        self,
        method: Callable[..., Any]
    ) -> Any:
        @wraps(method)
        async def _(*args, **kwargs):
            response: Any = None
            method_options: Dict[str, Any] = {}

            for key, value in kwargs.items():
                if isinstance(value, FastAPIRequest):  # Request Override
                    kwargs[key] = SeedRequest.from_request(value)

            try:
                method_options = method.options
            except AttributeError:
                pass

            status_code: int = method_options.get(
                'status_code',
                status.HTTP_200_OK
            )

            if not hasattr(method, 'is_coroutine'):
                method.is_coroutine: bool = iscoroutinefunction(method)
            try:
                if method.is_coroutine:
                    response: Any = await method(*args, **kwargs)
                else:
                    response: Any = method(*args, **kwargs)

                if isinstance(response, tuple):
                    assert len(response) == 2, 'Response must be Tuple[response, status_code]'

                    response, status_code = response

                assert isinstance(status_code, int), 'Status code must be integer type'

                if isinstance(response, Response):
                    response.status_code = status_code
                else:
                    response_class = method_options.get('response_class', ORJSONResponse)
                    response = response_class(response, status_code=status_code)
            except Exception as e:
                response: ORJSONResponse = await self._catch_server_error(e)

            return response

        return _

    async def _catch_server_error(
        self,
        e: Exception
    ) -> ORJSONResponse:
        exc: SeedHTTPException = SeedHTTPException(
            symbol='server_error_occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        if setting.debug:
            traceback: 'traceback' = e.__traceback__
            traceback = traceback.tb_next

            tracebacks: List[Dict[str, Any]] = []

            while traceback is not None:
                tracebacks.append({
                    'filename': traceback.tb_frame.f_code.co_filename,
                    'name': traceback.tb_frame.f_code.co_name,
                    'lineno': traceback.tb_lineno,
                })

                traceback = traceback.tb_next

            exc.detail: Dict[str, Any] = {
                'exception': e.__class__.__name__,
                'message': str(e),
                'tracebacks': tracebacks,
            }

            exc_type, exc_value, tb = sys.exc_info()
            tb = tb.tb_next

            logger.opt(exception=(None, exc_value, tb)).debug({
                'exception': e.__class__.__name__,
                'message': str(e),
                'trace_id': str(exc.trace_id),
            })

        if setting.integrate.sentry.enable:
            import sentry_sdk

            with sentry_sdk.push_scope() as scope:
                scope.set_extra('trace_id', str(exc.trace_id))
                sentry_sdk.capture_exception(e)

        return await seed_http_exception_handler(exc=exc)

    def __add__(
        self,
        payload: Tuple[str, 'Route']
    ) -> 'Router':
        assert (
            isinstance(payload, tuple) and len(payload) == 2
        ), 'Add payload must be Tuple[path, route] type'

        path, route_class = payload

        self.Route(path)(route_class)

        return self

    def add(
        self,
        path: str,
        route_class: 'Route',
        endpoint_options: Optional[Dict[str, Any]] = {},
    ) -> None:
        self.Route(path, endpoint_options=endpoint_options)(route_class)

    def join(self, router: 'Router', **kwargs) -> None:
        assert issubclass(
            router.__class__, APIRouter
        ), "Router must be 'Router' or 'APIRouter' class"

        self.include_router(router, **kwargs)
