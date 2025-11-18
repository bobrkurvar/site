import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Tile, TileColor
from repo import Crud, get_db_manager

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def get_catalog_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile, to_join=['color'])
    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
        },
    )

@router.get('/{tile_id}')
async def get_tile_page(request: Request, tile_id: int, manager: dbManagerDep):
    tile = await manager.read(Tile, id=tile_id, to_join=['color'])
    tile = tile[0] if tile else {}
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
        },
    )
