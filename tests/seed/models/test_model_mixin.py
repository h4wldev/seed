from seed.models import ModelMixin, UserModel


def test_model_mixin_repr():
    class Model(ModelMixin):
        _repr_attrs = ('id', 'name')

        id = 'id'
        name = 'name'
        secret = 'secret_data'

    model = Model()

    assert str(model) == '<Model id=id, name=name>'


def test_model_mixin_json():
    assert UserModel.q().first().json() == {
        'id': 1,
        'email': 'test@foobar.com',
        'updated_at': '2012-08-02T08:54:30',
        'username': 'test',
        'created_at': '1987-06-28T23:28:17'
    }


def test_model_mixin_query(query_string):
    model_mixin = ModelMixin()
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
    """)  # noqa: E501

    assert str(model_mixin.q(UserModel)) == query_string


def test_model_mixin_query_on_model(query_string):
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
    """)  # noqa: E501

    assert str(UserModel.q()) == query_string
