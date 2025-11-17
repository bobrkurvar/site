from fastapi import APIRouter

from .tile import router as tile_router
from .tile_size import router as tile_size_router
from .tile_color import router as tile_color_router

router = APIRouter(tags=["admin"], prefix="/admin/tile")
router.include_router(tile_router)
router.include_router(tile_size_router)
router.include_router(tile_color_router)
