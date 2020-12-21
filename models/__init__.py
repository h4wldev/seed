import typing

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ModelMixin:
    _repr_attrs: typing.Tuple[str] = ()

    def __repr__(self) -> str:
        attr_string = ''

        if len(self._repr_attrs):
            repr_attrs = {
                attr: getattr(self, attr, None) for attr in self._repr_attrs
            }

            repr_attrs = ', '.join(
                '='.join((str(k), str(v))) for k, v in repr_attrs.items()
            )

            attr_string = f' {repr_attrs}'

        return f'<{self.__class__.__name__}{attr_string}>'
