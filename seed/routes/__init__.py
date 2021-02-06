from seed.router import Router

from .auth import router as auth_router
from .users import router as users_router


router = Router()
router.join(auth_router)
router.join(users_router, prefix='/users')
