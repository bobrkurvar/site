from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from typing import Annotated
from repo import Crud, get_db_manager
from domain import Tile
import logging

router = APIRouter(tags=['presentation'], prefix='/catalog')
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates('templates')
log = logging.getLogger(__name__)

@router.get("")
async def get_catalog_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile)
    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "tiles": tiles,
    })
