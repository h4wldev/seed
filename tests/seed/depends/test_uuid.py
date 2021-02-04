import re

from fastapi import Request, Depends

from seed.depends.uuid import UUID


def valid_uuid(uuid):
    regex = re.compile(r'\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b')
    match = regex.match(uuid)

    return bool(match)


def test_uuid_depend(empty_app, get_test_client):
    @empty_app.get('/uuid-depend')
    def endpoint(request: Request, uuid: UUID = Depends()):
        return uuid

    client = get_test_client(empty_app)
    response = client.get('/uuid-depend')

    assert response.status_code == 200
    assert valid_uuid(response.json())
