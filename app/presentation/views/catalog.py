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


ITEMS_PER_PAGE = 20

@router.get("")
async def get_catalog_page(
    request: Request,
    manager: dbManagerDep,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = {}
    if name:
        filters["name"] = name
    if color:
        filters["color_name"] = color
    if size:
        filters["size_width"], filters["size_height"] = (
            float(i) for i in size.split(",")
        )

    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    tiles = await manager.read(
        Tile, to_join=["color"], offset=offset, limit=limit, **filters
    )

    total_count = len(await manager.read(Tile, **filters))
    total_pages = max((total_count + limit - 1) // limit, 1)

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
        },
    )


@router.get("/{tile_id}")
async def get_tile_page(request: Request, tile_id: int, manager: dbManagerDep):
    tile = await manager.read(Tile, id=tile_id, to_join=["color"])
    tile = tile[0] if tile else {}
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
        },
    )
