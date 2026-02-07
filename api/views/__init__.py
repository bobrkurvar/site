from fastapi import APIRouter

from .admin import router as view_admin_router
from .catalog import router as catalog_router
from .clients import router as clients_router
from .collections import router as collections_router
from .home import router as home_router

view_router = APIRouter()
view_router.include_router(view_admin_router)
view_router.include_router(catalog_router)
view_router.include_router(clients_router)
view_router.include_router(collections_router)
view_router.include_router(home_router)
