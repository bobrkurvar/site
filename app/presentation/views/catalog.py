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
