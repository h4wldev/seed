
def make_database_url(
    dbms: str,
    host: str,
    user: str,
    password: str,
    database: str,
    charset: str = 'utf8'
) -> str:
    if len(password):
        password = f':{password}'

    if len(host):
        host = f'@{host}'

    return f'{dbms}://{user}{password}{host}/{database}?charset={charset}'
