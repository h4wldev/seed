from typing import Any, Tuple, Dict, Union, Optional, Callable

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.declarative import api, declarative_base

from seed.db import db as db_

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

    def json(
        self,
        include: Optional[Union[str, set]] = None,
        exclude: Optional[Union[str, set]] = None,
        exclude_none: bool = False,
        custom_handler: Dict[str, Callable[[Any], Any]] = {}
    ) -> Dict[str, str]:
        result: Dict[str, Any] = {}

        for column in self.__table__.columns:
            if (include and column.key not in include)\
                or (exclude and column.key in exclude):
                continue

            data: Any = jsonable_encoder(getattr(self, column.key, None))

            if column.key in custom_handler.keys():
                data = custom_handler[column.key](data)

            if exclude_none and data is None:
                continue

            result[column.key]: Any = data

        return result

    @classmethod
    def q(
        self,
        *models: Tuple[Any]
    ) -> None:
        if issubclass(self.__class__, api.DeclarativeMeta):
            models = (self,) + models

        return Query(*models)
