from seed.application import Application

from .routes import router


app = Application(
    router=router
).create_app()
