from seed.models import ModelMixin, UserModel


def test_model_mixin_repr():
    class Model(ModelMixin):
        _repr_attrs = ('id', 'name')

        id = 'id'
        name = 'name'
        secret = 'secret_data'

    model = Model()

    assert str(model) == '<Model id=id, name=name>'


def test_model_mixin_jsonify():
    data = UserModel.q().first().jsonify()

    assert list(data.keys()) == ['id', 'email', 'username', 'updated_at', 'created_at']


def test_model_mixin_jsonify_include():
    data = UserModel.q().first().jsonify(include={'email', 'username'})

    assert list(data.keys()) == ['email', 'username']


def test_model_mixin_jsonify_exclude():
    data = UserModel.q().first().jsonify(exclude={'id'})

    assert list(data.keys()) == ['email', 'username', 'updated_at', 'created_at']


def test_model_mixin_jsonify_custom_handler():
    data = UserModel.q().first().jsonify(custom_handler={'email': lambda e: e.split('@')[1]})

    assert data['email'] == 'foobar.com'


def test_model_mixin_jsonify_column_alias():
    UserModel._column_alias = {'email': 'id'}
    data = UserModel.q().first().jsonify()

    UserModel._column_alias = {}

    assert data['email'] == data['id']


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
