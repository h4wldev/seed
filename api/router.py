from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from typing import Any, Callable, Dict, List, Optional, Tuple

from utils.http import HTTPMethod


class Route:
    _available_methods: List[str] = [m.value for m in HTTPMethod]

    @classmethod
    def option(cls, **options):
        def _(method):
            method.options: Dict[str, Any] = options
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
    def Route(
        self,
        path: str,
        default_options: Optional[Dict[str, Any]] = None
    ) -> Callable[..., Any]:
        assert path.startswith('/'), "Path must start with '/'"

        if default_options is None:
            default_options = {
                'response_class': ORJSONResponse
            }

        def _(cls: Route) -> Route:
            assert isinstance(cls, Route.__class__), 'Route must be inherit route class'

            endpoints: Dict[str, Callable[..., Any]] = cls._get_endpoints()

            for method, endpoint in endpoints.items():
                kwargs: Dict[str, Any] = {
                    **default_options,
                    **getattr(endpoint, 'options', {})
                }

                kwargs['methods'] = [method.upper()]

                self.add_api_route(*(path, endpoint), **kwargs)

        return _

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
        route_class: 'Route'
    ) -> None:
        self.Route(path)(route_class)

    def join(self, router: 'Router', **kwargs) -> None:
        assert issubclass(
            router.__class__, APIRouter
        ), "Router must be 'Router' or 'APIRouter' class"

        self.include_router(router, **kwargs)
