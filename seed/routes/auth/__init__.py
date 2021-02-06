from seed.router import Router

from .oauth import OAuth
from .logout import Logout
from .token_refresh import TokenRefresh


router = Router()
router += '/oauth', OAuth
router += '/logout', Logout
router += '/token/refresh', TokenRefresh
