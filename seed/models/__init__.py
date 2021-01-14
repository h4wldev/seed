from typing import Tuple

from sqlalchemy.ext.declarative import declarative_base

from db import db

from .utils.query import Query


Base = declarative_base()


class ModelMixin(Query):
    _repr_attrs: Tuple[str] = ()
    db: 'DBSessionMeta' = db

    def __repr__(self) -> str:
        attr_string: str = ''

        if len(self._repr_attrs):
            repr_attrs: Dict[str, any] = {
                attr: getattr(self, attr, None) for attr in self._repr_attrs
            }

            repr_attrs = ', '.join(
                '='.join((str(k), str(v))) for k, v in repr_attrs.items()
            )

            attr_string = f' {repr_attrs}'

        return f'<{self.__class__.__name__}{attr_string}>'
