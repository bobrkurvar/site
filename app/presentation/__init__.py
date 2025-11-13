from .admin import router as admin_router
from .home import router as home_router
from fastapi import APIRouter


presentation_router = APIRouter(tags=['pages'])

presentation_router.include_router(admin_router)
presentation_router.include_router(home_router)
