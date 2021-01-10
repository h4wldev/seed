from api.router import Router

from .auth import router as auth_router


router = Router()
router.join(auth_router)
