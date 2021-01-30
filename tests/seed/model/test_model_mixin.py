from app.models import UserModel
from seed.model.mixin import ModelMixin

from seed.db import db


def test_model_mixin_repr():
    class Model(ModelMixin):
        _repr_attrs = ('id', 'name')

        id = 'id'
        name = 'name'
        secret = 'secret_data'

    model = Model()

    assert str(model) == '<Model id=id, name=name>'


def test_model_mixin_query(query_string):
    model_mixin = ModelMixin()
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
    """)  # noqa: E501

    with db():
        assert str(model_mixin.q(UserModel)) == query_string


def test_model_mixin_query_on_model(query_string):
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
    """)  # noqa: E501

    with db():
        assert str(UserModel.q()) == query_string
