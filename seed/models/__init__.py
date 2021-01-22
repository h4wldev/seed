from typing import Any, Tuple

from sqlalchemy.ext.declarative import api, declarative_base

from db import db as db_

from .utils.query import Query


Base = declarative_base()


class ModelMixin:
    _repr_attrs: Tuple[str] = ()

    db: 'DBSessionMeta' = db_

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

    @classmethod
    def q(
        self,
        *models: Tuple[Any]
    ) -> None:
        if issubclass(self.__class__, api.DeclarativeMeta):
            models = (self,) + models

        return Query(*models)
