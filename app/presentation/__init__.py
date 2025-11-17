from fastapi import APIRouter

from .entities import router as entities_router
from .views.catalog import router as catalog_router
from .views.home import router as home_router
from .views.admin import router as view_admin_router

presentation_router = APIRouter()

presentation_router.include_router(entities_router)
presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
presentation_router.include_router(view_admin_router)
