from typing import Any, Tuple, Dict, Optional, Callable

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
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        custom_encoder: Dict[Any, Callable[[Any], Any]] = {}
    ) -> Dict[str, str]:
        return jsonable_encoder(
            self,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            custom_encoder=custom_encoder,
            sqlalchemy_safe=True
        )

    @classmethod
    def q(
        self,
        *models: Tuple[Any]
    ) -> None:
        if issubclass(self.__class__, api.DeclarativeMeta):
            models = (self,) + models

        return Query(*models)
