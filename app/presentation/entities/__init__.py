from fastapi import APIRouter

from .tile import router as tile_router
from .tile_size import router as tile_size_router

router = APIRouter(tags=["admin"], prefix="/admin")
router.include_router(tile_router)
router.include_router(tile_size_router)
