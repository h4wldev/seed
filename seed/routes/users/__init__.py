from seed.router import Router

from .users import Users


router = Router()
router += '/', Users
