from sqlalchemy import or_
from typing import Any, Tuple, Union

from db import db as db_


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
        except AttributeError:
            return getattr(self.query_, name)

    def filter(
        self,
        *filters: Tuple[Union[Tuple[str], str]]
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
