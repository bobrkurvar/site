from fastapi import APIRouter, Depends, Request
from repo import get_db_manager, Crud
from typing import Annotated
from domain import Tile, TileSize
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter(tags=['admin'], prefix='/admin')
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates('templates')
log = logging.getLogger(__name__)

@router.get("")
async def admin_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile)
    tile_sizes = await manager.read(TileSize)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "tiles": tiles,
        "tile_sizes": tile_sizes
    })
