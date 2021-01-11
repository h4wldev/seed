import os
import pytest
import sys

from fastapi.testclient import TestClient


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)  # noqa: E501

from app import app as application


@pytest.fixture
def get_test_client():
    return lambda app: TestClient(app)


@pytest.fixture(scope='module')
def app():
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def empty_endpoint():
    def endpoint():
        return {'foo': 'bar'}

    return endpoint
