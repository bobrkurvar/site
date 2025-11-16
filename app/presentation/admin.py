from fastapi import APIRouter, Depends, File, UploadFile, Form, Request
from fastapi.responses import RedirectResponse
from repo import get_db_manager, Crud
from typing import Annotated
from domain import Tile, TileSize
from services.tile import add_tile, delete_tile
from fastapi.templating import Jinja2Templates
from app.schemas.tile import TileSizeInput
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


@router.post('/tile/delete-all')
async def delete_tile_by_criteria_or_all(
        manager: dbManagerDep,
):
    await delete_tile(manager)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/sizes/delete")
async def admin_delete_tile_size(
        manager: dbManagerDep,
        height: Annotated[float | None, Form(gt=0)] = None,
        width: Annotated[float | None, Form(gt=0)] = None,
):
    if height is not None and width is not None:
        await manager.delete(TileSize, height=height, width=width)
    else:
        await manager.delete(TileSize)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/delete/{tile_id}")
async def admin_delete_tile(tile_id: int, manager: dbManagerDep):
    await delete_tile(manager, id=tile_id)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    bytes_image = await image.read()
    height_str, width_str = size.split(',')
    height = float(height_str)
    width = float(width_str)
    await add_tile(name, height, width, color, bytes_image, manager)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/sizes")
async def admin_create_tile_size(
        manager: dbManagerDep,
        height: Annotated[float | None, Form(gt=0)],
        width: Annotated[float | None, Form(gt=0)]
):
    await manager.create(TileSize, height=height, width=width)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/sizes/delete")
async def admin_delete_tile_size(tile_size: TileSizeInput, manager: dbManagerDep):
    await manager.delete(TileSize, **tile_size.model_dump())
    return RedirectResponse("/admin", status_code=303)
