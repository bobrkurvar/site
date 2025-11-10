
from . import home
from fastapi import APIRouter

router = APIRouter()
router.include_router(home.router)