from fastapi import APIRouter, Depends, File, UploadFile, Form, Request
from repo import get_db_manager, Crud
from typing import Annotated
from domain.tile import Tile
from services.tile import add_tile, delete_tile
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)

@router.post("/tile")
async def create_tile(
        name: Annotated[str, Form()],
        price: Annotated[float, Form()],
        image: Annotated[UploadFile, File()],
        manager: dbManagerDep,
):
    result = await add_tile(name, price, image, manager)
    return result

@router.get("/tile")
async def get_tile_lst(manager: dbManagerDep):
    result = await manager.read(Tile)
    return result


@router.get("/tile{tile_id}")
async def get_tile_by_id(tile_id: int,  manager: dbManagerDep):
    result = await manager.read(Tile, ident_val=tile_id)
    return result


@router.delete('/tile{tile_id}')
async def delete_tile_by_id(tile_id: int, manager: dbManagerDep):
    result = await delete_tile(manager, tile_id)
    return result


@router.delete('/tile')
async def delete_tile_by_criteria_or_all(
        manager: dbManagerDep,
        ident: str | None = None,
        ident_val = None
):
    params = {}
    if ident:
        params.update({ident: ident_val})
    elif ident_val:
        params.update(tile_id=ident_val)
    log.debug(params)
    await delete_tile(manager, **params)
