import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import *
from repo import Crud, get_db_manager

router = APIRouter(tags=["admin"], prefix="/admin")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile, to_join=["color"])

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    color_properties = await manager.read(TileColorFeature)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "color_properties": color_properties,
        },
    )
