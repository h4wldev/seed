# 🌾 seed
![Lint](https://github.com/h4wldev/seed/workflows/Lint/badge.svg)

Boilerplate for restful API with [tiangolo/fastapi](https://github.com/tiangolo/fastapi)


## Features
- __[Endpoints]__ Auth, Sign up, Withdrawal, ... routes included
- __[Router]__ Support class based Route
- __[Config]__ `.toml` based config system, support environments
- __[Authorize]__ Support custom OAuth2 authorization
- __[Model]__ User and User related(meta, profile, ...) models
- __[Depend]__ JWT(Json Web Token) based authorize
- __[Depend]__ Integer(Bitfield) based role, permission
- And support all features of fastapi


## How to Run
#### 1. Pull this Repo

#### 2. Configuration
1. Remove `.example` extension from [.secrets.settings.toml.example](.secrets.settings.toml.example) 
2. Change content of `file from step 1` and [settings.toml](settings/settings.toml)

#### 3. Just Run!
```bash
 $ uvicorn app:app
```


## How to Use
### Class based Route
```python
from api.router import Router, Route

router = Router()

@router.Route('/{item_id}')  # This decorator add route into router
class Item(Route):
  def get(item_id: int) -> Any:
    return f'item_id = {item_id}'

  @Route.option(tags=['Item'], summary='it is post!')  # You can use FastAPI options like this
  def post(item_id: int) -> Any:
    return f'item_id = {item_id}'

router.Route('/foo/{item_id}')(Item)  # Or you can add route like this
router += '/bar/{item_id}', Item  # Or this
router.add('/daz/{item_id}')  # Or this

other_router = Router()

router.join(other_router, prefix='/foobar')  # You can include router like this
router.join(
  other_router,
  prefix='/barbaz',
  tags=['other_router'],
  responses={418: {"description": "I'm a teapot"}}
)  # Also, Support fastapi options!
```

### JWT Depend
```python
from depends.jwt import JWT

@router.get('/jwt_required')
def jwt_required(jwt: JWT(required=True) = Depends()) -> Any:
  return jwt.user.email  # h4wldev@gmail.com
```

#### JWT(required, token_type, user_loader, user_cache)
You can setting jwt expires time, algorithm on [here](settings/settings.toml), and secret key on [here](settings/.secrets.settings.toml.example)

| argument    | type                 | description                                                                                          | default             |
|-------------|----------------------|------------------------------------------------------------------------------------------------------|---------------------|
| required    | bool                 | token required or not                                                                                | False               |
| token_type  | str                  | select token's type (access, refresh)                                                                | 'access'            |
| user_loader | Callable[[str], Any] | custom user loader (parameter : jwt token's subject) [example](depends/jwt.py#L96) | load from UserModel |
| user_cache  | bool                 | caching user data when loaded or not                                                                  | True                |

##### > JWT.user -> Union[UserModel, Any]  @property
User data property, after load token and user data

##### > JWT.load_token(credential: str)
Load token with credential (jwt token string)

##### > JWT.decode_token(token: str, algorithm: str = 'HS256') -> Dict[str, Any]  @staticmethod
Decode token with algorithm

##### > JWT.create_access_token(subject: str, payload: Dict[str, Any] = {}) -> str  @staticmethod
Create access token with payload. subject must be set unique data

##### > JWT.create_refresh_token(subject: str, payload: Dict[str, Any] = {}) -> str  @staticmethod
Create refresh token with payload. subject must be set unique data and payload must be same with access token


### Role Depend
> This depend include JWT depend, and jwt required<br>

```python
from depends.role import Role

@router.get('/need_roles')
def need_roles(
  role: Role(roles=[('admin', 'writer')], perms=['auth', 'write']
) = Depends()) -> Any:
  return role.user.email  # h4wldev@gmail.com
```

#### Role(roles, perms, user_loader, user_cache)
| argument    | type                        | description                                                                        | default               |
|-------------|-----------------------------|------------------------------------------------------------------------------------|-----------------------|
| roles       | List[Union[List[str], str]] | role names to check, using `Role.has` method                                       | []                    |
| perms       | List[Union[List[str], str]] | permission names to check, using `Role.has` method                                 | []                    |
| user_loader | Callable[[str], Any]        | custom user loader (parameter : jwt token's subject) [example](depends/jwt.py#L96) | (load from UserModel) |
| user_cache  | bool                        | caching user data when loaded or not                                               | True                  |

##### > Role.user -> Union[UserModel, Any]  @property
User data property, after load token and user data on JWT Depend


### Bitfield based Role, Permission
```diff
- [Caution] Working with mapping array index, Don't mess array element's order!
```

```python
# Same usage with Role and Permission
from depends.role.types import Role, Permission

mapping: List[str] = ['super-admin', 'admin', 'writer', 'reader']

role = Role(0, mapping=mapping)  # diffrent from role depend class
Role.from_bitfield([False, False, False, False], mapping=mapping)  # or initialize with bitfield

role.get('admin')  # True
role.get('super-admin')  # False
role.get('undefined')  # False

role.set('super-admin', True); role.get('super-admin')  # True
role.set('super-admin', False); role.get('super-admin')  # False
role.set('undefined', False)  # Raise Error!

role.has('reader', ['admin', 'writer'])  # True : reader AND (admin OR writer)
role.has('reader', 'super-admin')  # False : reader AND super-admin
# Using list, tuple type to or operate

role.get_all()  # {'super-admin': False, 'admin': True, ...}

role.reset()
```

#### Role, Permission(value, mapping)
You can setting mapping array on [here](settings/settings.toml)

| argument | type      | description                           | default       |
|----------|-----------|---------------------------------------|---------------|
| value    | int       | integer value before convert bitfield | (Required)    |
| mapping  | List[str] | mapping array                         | (on settings) |

##### > Role.value -> int  @property
Get integer value of role/permission

##### > Role.bitfield -> List[bool]  @property
Get bitfield of role/permission

##### > Role.get(name: str) -> bool
Get has role/permission on name

##### > Role.has(*roles: Tuple[Union[List[str], str]]) -> bool
Get has role/permission on roles, list is or operate. detail on example.

##### > Role.get_all() -> Dict[str, bool]
Get all of role/permission

##### > Role.reset()
Reset on role/permission

##### > Role.set(name: str, value: bool)
Set value on role/permission

##### > Role.from_bitfield(value: List[bool], mapping: List[str])  @classmethod
Initialize with bitfield. detail on example.

## TODO
- [ ] Class based route
- [ ] API endpoints

## Requirements
You can see [Here](requirements.txt)!
