import pytest

from fastapi.responses import ORJSONResponse

from seed.router import Route, Router


@pytest.fixture
def get_wrapped_response():
    async def _(endpoint):
        router = Router()
        wrapped = router._endpoint_wrapper(endpoint)

        return await wrapped()

    return _


def test_route_endpoint_doc_option(empty_endpoint):
    route = Route()
    endpoint = route.doc_option()(empty_endpoint)

    assert endpoint.doc_options == {
        'include_in_schema': True,
        'tags': None,
        'summary': None,
        'description': None,
        'response_description': 'Successful Response',
        'responses': None,
        'deprecated': None,
    }


def test_route_endpoint_option(empty_endpoint):
    route = Route()
    endpoint = route.option()(empty_endpoint)

    assert endpoint.endpoint_options == {
        'dependencies': None,
        'status_code': 200,
        'operation_id': None,
        'response_class': ORJSONResponse,
        'name': None,
        'route_class_override': None,
        'callbacks': None,
    }


def test_route_endpoint_response_model(empty_endpoint):
    route = Route()
    endpoint = route.response_model(
        response_model='response_model'
    )(empty_endpoint)

    assert endpoint.response_model == {
        'response_model': 'response_model',
        'response_model_include': None,
        'response_model_exclude': None,
        'response_model_by_alias': True,
        'response_model_exclude_unset': False,
        'response_model_exclude_defaults': False,
        'response_model_exclude_none': False,
    }


def test_route_get_endpoints():
    class _Route(Route):
        get = 'not_callable'

        def head(): pass  # noqa: E704
        def post(): pass  # noqa: E704
        def put(): pass  # noqa: E704
        def delete(): pass  # noqa: E704
        def options(): pass  # noqa: E704
        def trace(): pass  # noqa: E704
        def patch(): pass  # noqa: E704
        def not_http_method(): pass  # noqa: E704

    methods = _Route._get_endpoints()
    method_names = list(map(lambda k: k[0], methods.items()))

    assert method_names == [
        'head', 'post', 'put', 'delete', 'options', 'trace', 'patch',
    ]


def test_router_route_bind(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint
        post = empty_endpoint

    router = Router()
    router.Route('/')(_Route)

    assert len(router.routes) == 2

    assert router.routes[0].path == '/'
    assert router.routes[0].methods == {'GET'}

    assert router.routes[1].path == '/'
    assert router.routes[1].methods == {'POST'}


def test_router_route_bind_with_endpoint_options(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint

    router = Router()
    router.Route('/', endpoint_options={
        'name': 'foobar'
    })(_Route)

    assert router.routes[0].name == 'foobar'


def test_router_endpoint_options(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint

    router = Router(endpoint_options={
        'name': 'foobar'
    })
    router.Route('/')(_Route)

    assert router.routes[0].name == 'foobar'


@pytest.mark.asyncio
async def test_router_endpoint_wrapper(
    empty_endpoint,
    get_wrapped_response
):
    response = await get_wrapped_response(
        empty_endpoint
    )
    response.body == b'{}'
    response.status_code == 200


@pytest.mark.asyncio
async def test_router_endpoint_wrapper_with_status_code(get_wrapped_response):
    def endpoint_with_status_code():
        return {}, 400

    response = await get_wrapped_response(
        endpoint_with_status_code
    )
    response.body == b'{}'
    response.status_code == 400


@pytest.mark.asyncio
async def test_router_endpoint_wrapper_with_corutine_endpoint(get_wrapped_response):
    async def corutine_endpoint():
        return {}

    response = await get_wrapped_response(
        corutine_endpoint
    )
    response.body == b'{}'
    response.status_code == 200


@pytest.mark.asyncio
async def test_router_endpoint_wrapper_with_return_response_class(get_wrapped_response):
    async def return_response_class():
        return ORJSONResponse({})

    response = await get_wrapped_response(
        return_response_class
    )
    response.body == b'{}'
    response.status_code == 200


@pytest.mark.asyncio
async def test_router_endpoint_wrapper_with_return_response_class_status_code(get_wrapped_response):
    async def return_response_class_status_code():
        return ORJSONResponse({}), 400

    response = await get_wrapped_response(
        return_response_class_status_code
    )
    response.body == b'{}'
    response.status_code == 400


def test_router_route_bind_add_operator(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint

    router = Router()
    router += '/', _Route

    assert router.routes[0].path == '/'
    assert router.routes[0].methods == {'GET'}


def test_router_route_bind_add_method(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint

    router = Router()
    router.add('/', _Route, endpoint_options={
        'name': 'foobar'
    })

    assert router.routes[0].name == 'foobar'
    assert router.routes[0].path == '/'
    assert router.routes[0].methods == {'GET'}


def test_router_join_router(empty_endpoint):
    class _Route(Route):
        get = empty_endpoint

    router1 = Router()
    router2 = Router()

    router1.add('/', _Route)
    router2.join(router1)

    assert router2.routes[0].path == '/'
    assert router2.routes[0].methods == {'GET'}
