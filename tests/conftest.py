import os
import pytest
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)  # noqa: E501

from db import db

from routes import router

from seed.application import Application


# Initialize testing application
application = Application(
    router=router,
    env='testing',
).create_app()


@pytest.fixture
def get_test_client():
    return lambda app: TestClient(app)


@pytest.fixture(scope='session')
def app():
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope='function')
def empty_app():
    return FastAPI()


@pytest.fixture
def empty_endpoint():
    def endpoint():
        return {'foo': 'bar'}

    return endpoint


@pytest.fixture
def query_string():
    def strip(s):
        return s.replace('  ', '\t').strip('\t')

    return lambda s: '\n'.join(map(
        lambda s: f'{strip(s)} ',
        s.split('\n')
    )).strip()


@pytest.fixture
def dummy_record():
    class _:
        def __init__(self, *data):
            self.data = data

        def __enter__(self):
            for data in self.data:
                db.session.add(data)

            db.session.commit()

            return self.data

        def __exit__(self, exc_type, exc_val, exc_tb):
            for data in self.data:
                db.session.delete(data)

            db.session.commit()

    return _
