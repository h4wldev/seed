from seed.application import Application

from app.routes import router


app = Application(
    router=router,
).create_app()
