import enum

from sqlalchemy import or_, case, asc, desc
from sqlalchemy.orm.query import Query as SAQuery
from typing import Any, Tuple, Union, Set, Callable

from seed.db import db as db_


class Query:
    db: 'DBSessionMeta' = db_

    def __init__(
        self,
        *models: Tuple[Any]
    ) -> None:
        self.models: Tuple[Any] = models
        self.query_: 'Query' = db_.session.query(*self.models)

    def __str__(self) -> str:
        return str(self.query_)

    def __getattribute__(
        self,
        name: str
    ) -> Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            return self._mapper(name)

    def filter(
        self,
        *filters: Tuple[Union[Tuple['BinaryExpression'], 'BinaryExpression']]
    ) -> 'Query':
        for f in filters:
            if isinstance(f, tuple):
                f = or_(*f)

            self.query_ = self.query_.filter(f)

        return self

    def paging(
        self,
        page: int,
        limit: int
    ) -> 'Query':
        self.query_ = self.query_.limit(limit).offset(page * limit)

        return self

    def exists(self) -> bool:
        return self.query_.count() > 0

    def enum_order_by(
        self,
        column: 'InstrumentedAttribute',
        priorities: Set[Any] = set(),
        order_by: Union[str, Callable[..., Any]] = asc
    ) -> 'Query':
        whens: Dict[str, int] = {}

        for i, item in enumerate(priorities):
            if isinstance(item, enum.Enum):
                item = item.value

            whens[item] = i

        if isinstance(order_by, str):
            order_by = {'desc': desc, 'asc': asc}.get(order_by, asc)

        self.query_ = self.query_.order_by(
            order_by(case(value=column, whens=whens).label(column.key))
        )

        return self

    def _mapper(
        self,
        name: str
    ) -> 'Query':
        def _(*args, **kwargs) -> Any:
            result: Any = getattr(self.query_, name)(*args, **kwargs)

            if isinstance(result, SAQuery):
                self.query_ = result

                return self

            return result

        return _
