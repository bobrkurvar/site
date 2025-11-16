from .admin import router as admin_router
from .home import router as home_router
from .catalog import router as catalog_router
from fastapi import APIRouter


presentation_router = APIRouter(tags=['presentation'])

presentation_router.include_router(admin_router)
presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
