
from seed.utils.database import make_database_url


def test_make_database_url():
    assert make_database_url(
        dbms='mysql',
        host='127.0.0.1',
        user='root',
        password='password',
        database='database'
    ) == 'mysql://root:password@127.0.0.1/database?charset=utf-8'


def test_make_database_url_without_password():
    assert make_database_url(
        dbms='mysql',
        host='127.0.0.1',
        user='root',
        database='database'
    ) == 'mysql://root@127.0.0.1/database?charset=utf-8'


def test_make_database_url_without_host():
    assert make_database_url(
        dbms='mysql',
        user='root',
        password='password',
        database='database'
    ) == 'mysql://root:password/database?charset=utf-8'
