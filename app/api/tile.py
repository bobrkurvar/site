import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.schemas.tile import TileDelete, TileSizeInput
from domain.tile import Tile, TileSize
from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/tiles")
async def create_tile(
    name: Annotated[str, Form()],
    height: Annotated[float, Form(gt=0)],
    width: Annotated[float, Form(gt=0)],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    bytes_image = await image.read()
    result = await add_tile(name, height, width, bytes_image, manager)
    return result


@router.get("/tiles")
async def get_tile_lst(manager: dbManagerDep):
    result = await manager.read(Tile)
    return result


@router.post("/tiles/sizes")
async def create_tile_size(tile_size: TileSizeInput, manager: dbManagerDep):
    result = await manager.create(TileSize, **tile_size.model_dump())
    return result


@router.get("/tiles/sizes")
async def get_all_tile_size(manager: dbManagerDep):
    result = await manager.read(TileSize)
    return result


@router.get("/tiles{tile_id}")
async def get_tile_by_id(tile_id: int, manager: dbManagerDep):
    result = await manager.read(Tile, id=tile_id)
    return result


@router.delete("/tiles{tile_id}")
async def delete_tile_by_id(tile_id: int, manager: dbManagerDep):
    result = await delete_tile(manager, id=tile_id)
    return result


@router.delete("/tiles")
async def delete_tile_by_criteria_or_all(manager: dbManagerDep, tile: TileDelete):
    params = {}
    if tile.name:
        params.update(name=tile.name)
    if tile.size:
        params.update(size_height=tile.size.height, size_width=tile.size.width)
    log.debug(params)
    await delete_tile(manager, **params)
