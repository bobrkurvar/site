import logging

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from repo import get_db_manager, Crud
from typing import Annotated
from domain.tile import Tile


router = APIRouter()
templates = Jinja2Templates('templates')
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

log = logging.getLogger(__name__)

@router.get("/")
async def get_main_page(request: Request, manager: dbManagerDep):
    products = await manager.read(Tile)
    log.debug(products)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "featured_tiles": products}
    )
