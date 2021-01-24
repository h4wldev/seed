from seed.api.router import Router

from .oauth import OAuth


router = Router()
router += '/oauth', OAuth
