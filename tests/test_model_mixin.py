from seed.models import ModelMixin


def test_model_mixin_repr():
    class Model(ModelMixin):
        _repr_attrs = ('id', 'name')

        id = 'id'
        name = 'name'
        secret = 'secret_data'

    model = Model()

    assert str(model) == '<Model id=id, name=name>'
