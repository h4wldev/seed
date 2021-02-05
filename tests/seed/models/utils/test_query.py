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
