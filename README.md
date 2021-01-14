<p align="center">
 <img alt="Header" src="https://user-images.githubusercontent.com/14465407/103291172-8083bb80-4a2e-11eb-8687-f9c748593f7d.png" height="180px">
</p>
<h1 align="center">🌾 seed</h1>
<p align="center">
 Boilerplate for restful API with <a href="https://github.com/tiangolo/fastapi">tiangolo/fastapi</a>
</p>
<p align="center">
 <a href="https://codecov.io/gh/h4wldev/seed"><img src="https://codecov.io/gh/h4wldev/seed/branch/develop/graph/badge.svg?token=56FGFR91EX"></a>
</p>

## Features
- __[Endpoints]__ Auth, Sign up, Withdrawal, ... routes included *(In Progress)*
- __[Router]__ Support class based Route
- __[Config]__ `.toml` based config system, support environments
- __[Authorize]__ Support custom OAuth2 authorization ([Kakao](seed/oauth/kakao.py))
- __[Model]__ User and User related(meta, profile, ...) models
- __[Depend]__ JWT(Json Web Token) based authorize, support httponly cookie mode
- __[Depend]__ Integer(Bitfield) based role, permission
- __[Depend]__ User specific id with UUID
- __[Depend]__ Logger with UUID
- __[Integrate]__ Integrate with Sentry, Logstash
- And support all features of fastapi


## How to Run
#### 1. Pull this Repo

#### 2. Configuration
1. Remove `.example` extension, change env on filename & content from [.secrets.<<env>.toml.example](settings/secrets/.secrets.<env>.toml.example) and [setting.<<env>.toml.example](settings/setting.<env>.toml.example) 
2. Uncomment or add on [setting.py](setting.py), setting files

#### 3. DB Migration
```bash
 $ alembic upgrade head
```

#### 4. Just Run!
```bash
 $ uvicorn app:app
```


## How to Use
### Class based Route
seed's `Router` is inherit [fastapi.APIRouter](https://github.com/tiangolo/fastapi/blob/master/fastapi/routing.py#L408), So you can use all the methods in `APIRouter`

```python
from fastapi.responses import ORJSONResponse

from seed.api.router import Router, Route

router = Router(
  endpoint_options
)

@router.Route(
  '/{item_id}',
  endpoint_options={
    'response_class': ORJSONResponse
  }  # You can set default endpoint options
)  # This decorator add route into router
class Item(Route):
  _endpoint_options: Dict[str, Any] = {
    'status_code': 404
  }
  # Also you can setting default endpoint options in here
  # Option Priority : on Router -> on Route -> on Endpoint

  def get(item_id: int) -> Any:
    return f'item_id = {item_id}', 200  # You can set status code like this

  @Route.option(dependencies=[])  # Set FastAPI endpoints argument, More infos on below example
  def post(item_id: int) -> Any:
    return ORJSONResponse(f'item_id = {item_id}', status_code=201)  # Also, you can use FastAPI Response Class

  @Route.option(default_status_code=403)  # Or setting on option
  def post(item_id: int) -> Any:
    return '403 Forbidden'

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

#### Route
##### > Route.option
arguments : name, default_status_code(=status_code), dependencies, operation_id, response_class, route_class_override, callbacks

##### > Route.doc_option
arguments : enable(=include_in_schema), tags, summary, description, response_description, responses, deprecated

##### > Route.response_model
arguments : response_model, response_model_include, response_model_exclude, response_model_by_alias, response_model_exclude_unset, response_model_exclude_defaults, response_model_exclude_none


### UUID Depend
```python
from seed.depends.uuid import UUID

@router.get('/uuid')
def jwt_required(uuid: UUID = Depends()) -> Any:
  return uuid  # 01dbd65e-1b46-35aa-9928-51333fe20858
```

##### > UUID.get_uuid(request: Request)
Get uuid with fastapi request


### Context Logger Depend
> This depend include UUID depend, same usage with just logger<br>

```python
from logger import logger as default_logger
from seed.depends.context_logger import ContextLogger


@router.get('/logger_with_uuid')
def logger_with_uuid(context_logger: ContextLogger = Depends()) -> Any:
  default_logger.info('not show uuid!')  # not show uuid on stdout log
  context_logger.info('show uuid!')  # show uuid on stdout log
  return None
```

## How to custom OAuth handler
#### 1. Configuration
```toml
[<env>.oauth]
    providers = ['kakao']
```
1. Add your OAuth provider's name on `<env>.oauth.providers`
```toml
[<env>.oauth.<provider>]
  handler = 'seed.oauth.<provider>.<provider>OAuthHandler'
```
2. Add provider's setting on `<env>.oauth.<provider>`

#### 2. Make handler
Make handler reference from [Base Handler](seed/oauth/__init__.py) and [Kakao Handler](seed/oauth/kakao.py)


## Integrate
### Sentry
Change or add setting `<env>.integrate.sentry`
```toml
[<env>.integrate.sentry]
enable = true
dsn = '<set_your_sentry_dsn'
```

### Logstash
Change or add setting `<env>.integrate.logstash`
```toml
[default.integrate.logstash]
enable = true
host = '127.0.0.1'
port = 5959
database_path = 'logstash.db'

    [default.integrate.logstash.options]
    transport = 'logstash_async.transport.TcpTransport'
    ssl_enable = false
    ssl_verify = true
    keyfile = ''
    certfile = ''
    ca_certs = ''
    encoding = 'utf-8'
```


## TODO
- [ ] API endpoints
- [ ] Add unittest testcases

## Requirements
You can see [Here](requirements.txt)!

## License: MIT
Copyright (c) 2020 h4wldev@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
