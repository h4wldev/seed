import enum
import pytest

from seed.models import UserModel
from seed.models.utils.query import Query

from seed.db import db


def test_query_init(query_string):
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
    """)  # noqa: E501

    with db():
        assert str(Query(UserModel)) == query_string


def test_query_filter(query_string):
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
        WHERE (users.email LIKE %s OR users.email LIKE %s) AND users.id < %s
    """)  # noqa: E501

    with db():
        query = Query(UserModel).filter(
            (UserModel.email.like('%@naver.com'), UserModel.email.like('%@naver.com')),
            UserModel.id < 100
        )

        assert str(query) == query_string


def test_query_paging(query_string):
    query_string = query_string("""
        SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
        FROM users
         LIMIT %s, %s
    """)  # noqa: E501

    with db():
        query = Query(UserModel).paging(page=0, limit=30)

        assert str(query) == query_string


def test_query_exists():
    assert Query(UserModel).filter(
        UserModel.email == 'test@foobar.com'
    ).exists()


def test_query_getattribute_on_sa_query():
    assert Query(UserModel).count()


def test_query_getattribute_attribute_error():
    with pytest.raises(AttributeError):
        Query(UserModel).foobar()


def test_query_mix_query_and_sa_query():
    assert Query(UserModel)\
        .order_by(UserModel.id.desc())\
        .paging(page=0, limit=30)\
        .count()


def test_query_enum_order_by(query_string):
    query = Query(UserModel).enum_order_by(UserModel.username, ['super-admin', 'admin'])
    query_string = query_string("""
    SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
FROM users ORDER BY CASE users.username WHEN %s THEN %s WHEN %s THEN %s END ASC
""")  # noqa: E501

    assert str(query) == query_string


def test_query_enum_order_by_with_enum(query_string):
    class Enum(enum.Enum):
        one = 'one'
        two = 'two'

    query = Query(UserModel).enum_order_by(UserModel.username, [Enum.one, Enum.two])
    query_string = query_string("""
    SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
FROM users ORDER BY CASE users.username WHEN %s THEN %s WHEN %s THEN %s END ASC
""")  # noqa: E501

    assert str(query) == query_string


def test_query_enum_order_by_with_order(query_string):
    class Enum(enum.Enum):
        one = 'one'
        two = 'two'

    query = Query(UserModel).enum_order_by(UserModel.username, [], 'desc')
    query_string = query_string("""
    SELECT users.id AS users_id, users.email AS users_email, users.username AS users_username, users.updated_at AS users_updated_at, users.created_at AS users_created_at
FROM users ORDER BY CASE users.username END DESC
""")  # noqa: E501

    assert str(query) == query_string
