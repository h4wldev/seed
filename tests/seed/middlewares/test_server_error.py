from fastapi import FastAPI

from seed.middlewares.server_error import ServerErrorMiddleware


def test_auth_depend(get_test_client):
    app = FastAPI()
    app.add_middleware(ServerErrorMiddleware)

    client = get_test_client(app)

    @app.get('/test')
    def endpoint():
        1 / 0

    response = client.get('/test')

    assert response.status_code == 500
    assert response.json()['symbol'] == 'server_error_occurred'
