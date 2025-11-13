from fastapi import APIRouter, Depends, File, UploadFile, Form, Request
from fastapi.responses import RedirectResponse
from repo import get_db_manager, Crud
from typing import Annotated
from domain.tile import Tile
from services.tile import add_tile, delete_tile
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter(tags=['admin'])
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates('templates')
log = logging.getLogger(__name__)

@router.get("/admin")
async def admin_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "tiles": tiles
    })


@router.post("/admin/tile/delete/{tile_id}")
async def admin_delete_tile(tile_id: int, manager: dbManagerDep):
    await delete_tile(manager, tile_id=tile_id)
    return RedirectResponse("/admin", status_code=303)



@router.post("/admin/tile")
async def admin_create_tile(
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    await add_tile(name, price, image, manager)
    return RedirectResponse("/admin", status_code=303)


