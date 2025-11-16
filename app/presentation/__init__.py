from fastapi import APIRouter

from .entities import router as admin_router
from .views.catalog import router as catalog_router
from .views.home import router as home_router
from .views.admin import router as admin_router

presentation_router = APIRouter(tags=["presentation"])

presentation_router.include_router(admin_router)
presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
presentation_router.include_router(admin_router)
