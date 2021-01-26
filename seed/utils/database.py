
def make_database_url(
    dbms: str,
    user: str,
    database: str,
    host: str = '',
    password: str = '',
    charset: str = 'utf-8'
) -> str:
    if password and len(password):
        password = f':{password}'

    if host and len(host):
        host = f'@{host}'

    return f'{dbms}://{user}{password}{host}/{database}?charset={charset}'
