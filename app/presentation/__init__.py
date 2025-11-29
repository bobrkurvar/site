from fastapi import APIRouter

from .entities import (tile_color_router, tile_router, tile_size_router,
                       tile_surface_router, tile_boxes_router, tile_producers_router)
from .views.admin import router as view_admin_router
from .views.catalog import router as catalog_router
from .views.home import router as home_router

presentation_router = APIRouter()

presentation_router.include_router(tile_router)
presentation_router.include_router(tile_size_router)
presentation_router.include_router(tile_color_router)
presentation_router.include_router(tile_surface_router)
presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
presentation_router.include_router(view_admin_router)
presentation_router.include_router(tile_boxes_router)
presentation_router.include_router(tile_producers_router)
