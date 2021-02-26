import os
import pytest
import sys

from unittest.mock import patch, PropertyMock

from fastapi import APIRouter
from fastapi.testclient import TestClient


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)  # noqa: E501

from seed.db import db

from app.routes import router

from seed.application import Application
from seed.depends.auth.types import JWTToken


# Initialize testing application
application = Application(
    router=router,
    env='testing'
).create_app()


@pytest.fixture(autouse=True)
def session():
    with db():
        db.session.begin_nested()

        with patch(
            'fastapi_sqlalchemy.middleware.DBSessionMeta.session',
            return_value=db.session,
            new_callable=PropertyMock
        ):
            yield db.session

        db.session.rollback()
        db.session.close()


@pytest.fixture
def get_test_client():
    return lambda app: TestClient(app)


@pytest.fixture(scope='session')
def app():
    return application


@pytest.fixture
def client(session, app):
    return TestClient(app)


@pytest.fixture
def empty_app():
    return Application(
        router=APIRouter(),
        env='testing'
    ).create_app()


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
def create_token():
    def _(
        subject='foobar',
        type_='access',
        expires='10s'
    ):
        return JWTToken.create(
            subject=subject,
            token_type=type_,
            expires=expires
        )

    return _
