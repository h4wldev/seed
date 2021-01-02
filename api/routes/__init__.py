from api.router import Router

from .oauth import OAuth


router = Router()
router += '/ouath', OAuth
