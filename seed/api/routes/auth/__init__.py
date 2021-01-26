from seed.api.router import Router

from .oauth import OAuth
from .logout import Logout


router = Router()
router += '/oauth', OAuth
router += '/logout', Logout
