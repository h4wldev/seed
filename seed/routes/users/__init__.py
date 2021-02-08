from seed.router import Router

from .users import Users
from .user_me import UserMe


router = Router()
router += '/', Users
router += '/me', UserMe
