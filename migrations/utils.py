import os
import sys
import sqlalchemy as sa

from typing import Any, List, Dict

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from seed.models.mixin import Base


def table_args(model: Base) -> None:
    def create_new_column(column: sa.Column) -> sa.Column:
        attributes: List[str] = [
            'name', 'type', 'key', 'primary_key',
            'nullable', 'default', 'server_default',
            'server_onupdate', 'index', 'unique',
            'system', 'doc', 'onupdate', 'autoincrement',
            'comment',
        ]

        kwargs: Dict[str, Any] = {
            a: getattr(column, a, None) for a in attributes
        }
        kwargs['type_']: 'TypeEngine' = kwargs.get('type', None)
        del kwargs['type']

        return sa.Column(**kwargs)
        
    columns: List[sa.Column] = list(map(
        create_new_column,
        model.__table__.columns.values()
    ))

    return (
        model.__tablename__,
        *columns,
    )
