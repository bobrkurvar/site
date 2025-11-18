import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain.tile import Tile
from repo import Crud, get_db_manager

router = APIRouter()
templates = Jinja2Templates("templates")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

log = logging.getLogger(__name__)


@router.get("/")
async def get_main_page(request: Request, manager: dbManagerDep):
    products = await manager.read(Tile, to_join=['color'])
    log.debug(products)
    return templates.TemplateResponse(
        "home.html", {"request": request, "featured_tiles": products}
    )
