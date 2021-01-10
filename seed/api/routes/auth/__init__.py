from seed.api.router import Router

from .oauth import OAuth
from .token_refresh import TokenRefresh
from .logout import Logout


router = Router()
router += '/oauth', OAuth
router += '/token/refresh', TokenRefresh
router += '/logout', Logout
