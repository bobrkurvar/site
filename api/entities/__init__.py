from fastapi import APIRouter, Depends

from adapters.auth import get_user_from_token

from .category import router as categories_router
from .collections import router as entity_collections_router
from .tile import router as tile_router
from .tile_boxes import router as tile_boxes_router
from .tile_color import router as tile_color_router
from .tile_producers import router as tile_producers_router
from .tile_size import router as tile_size_router
from .tile_surface import router as tile_surface_router

#admin_router = APIRouter(dependencies=[Depends(get_user_from_token)])
admin_router = APIRouter()
admin_router.include_router(tile_router)
admin_router.include_router(tile_size_router)
admin_router.include_router(tile_color_router)
admin_router.include_router(tile_surface_router)
admin_router.include_router(tile_boxes_router)
admin_router.include_router(tile_producers_router)
admin_router.include_router(categories_router)
admin_router.include_router(entity_collections_router)
